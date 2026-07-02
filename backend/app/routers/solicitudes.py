import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user, require_permiso
from app.database import get_db
from app.models.cuentas import Cliente, Cuenta, Movimiento
from app.models.creditos import (
    ProductoCredito, SolicitudCredito, ScoringCrediticio, EvaluacionRDS,
    MatrizAprobacion, Aprobacion, Credito,
)
from app.models.rbac import Usuario, Rol
from app.schemas.solicitud import SolicitudCreate, SolicitudOut, OpinionRequest, DesembolsoOut
from app.services import credito_service as svc

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes de Crédito"])

# Rol de usuario esperado para cada estado "pendiente de opinión"
ROL_ESPERADO_POR_ESTADO = {
    "OPINION_ADMINISTRADOR": "ADMINISTRADOR",
    "OPINION_JEFE_REGIONAL": "JEFE_REGIONAL",
    "OPINION_RIESGOS": "RIESGOS",
    "COMITE": "COMITE",
}
NIVEL_POR_ESTADO = {
    "OPINION_ADMINISTRADOR": "ADMINISTRADOR",
    "OPINION_JEFE_REGIONAL": "JEFE_REGIONAL",
    "OPINION_RIESGOS": "RIESGOS",
    "COMITE": "COMITE",
}


def _obtener_regla_matriz(db: Session, monto: float) -> MatrizAprobacion:
    regla = (
        db.query(MatrizAprobacion)
        .filter(MatrizAprobacion.monto_desde <= monto, MatrizAprobacion.monto_hasta >= monto)
        .first()
    )
    if regla is None:
        raise HTTPException(400, "No existe una regla de aprobación para ese monto")
    return regla


@router.post("/", response_model=SolicitudOut)
def crear_solicitud(
    payload: SolicitudCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_permiso("solicitudes_credito", "crear")),
):
    """
    Nace típicamente desde el Homebanking (canal_origen se decide aquí según
    el rol de quien llama). Evalúa elegibilidad, calcula scoring y RDS, y
    deja la solicitud en el primer nivel de la ruta de aprobación.
    """
    cliente = db.query(Cliente).filter(Cliente.id_usuario == usuario.id_usuario).first()
    if cliente is None:
        raise HTTPException(404, "El usuario autenticado no tiene un perfil de cliente asociado")

    producto = db.get(ProductoCredito, payload.id_producto)
    if producto is None or not producto.activo:
        raise HTTPException(404, "Producto de crédito no encontrado o inactivo")

    if not (float(producto.monto_minimo) <= payload.monto_solicitado <= float(producto.monto_maximo)):
        raise HTTPException(400, f"El monto debe estar entre {producto.monto_minimo} y {producto.monto_maximo}")
    if not (producto.plazo_min_meses <= payload.plazo_meses <= producto.plazo_max_meses):
        raise HTTPException(400, f"El plazo debe estar entre {producto.plazo_min_meses} y {producto.plazo_max_meses} meses")

    elegible, motivo = svc.evaluar_elegibilidad(cliente, db)
    if not elegible:
        raise HTTPException(422, f"Cliente no es sujeto de crédito: {motivo}")
    cliente.es_sujeto_credito = True

    regla = _obtener_regla_matriz(db, payload.monto_solicitado)

    solicitud = SolicitudCredito(
        id_cliente=cliente.id_cliente,
        id_producto=producto.id_producto,
        monto_solicitado=payload.monto_solicitado,
        plazo_meses=payload.plazo_meses,
        canal_origen="HOMEBANKING",
        estado="EN_EVALUACION",
    )
    db.add(solicitud)
    db.flush()

    # --- Scoring y RDS, calculados automáticamente al crear la solicitud ---
    cuota_estimada = svc.calcular_cuota_francesa(
        payload.monto_solicitado, float(producto.tasa_interes_anual), payload.plazo_meses
    )
    deuda_actual = svc.calcular_deuda_actual_mensual(cliente, db)
    rds, semaforo = svc.calcular_rds(float(cliente.ingreso_mensual), cuota_estimada, deuda_actual)

    db.add(EvaluacionRDS(
        id_solicitud=solicitud.id_solicitud,
        ingreso_mensual=cliente.ingreso_mensual,
        cuota_estimada=cuota_estimada,
        deuda_actual_mensual=deuda_actual,
        rds=rds,
        semaforo=semaforo,
    ))

    datos_scoring = svc.calcular_scoring(cliente, rds, db)
    db.add(ScoringCrediticio(id_solicitud=solicitud.id_solicitud, **datos_scoring))

    # Primer nivel de la ruta de aprobación (según seed, ADMIN siempre es requerido)
    primer_nivel = svc.niveles_requeridos(regla)[0]
    solicitud.estado = svc.ESTADO_POR_NIVEL[primer_nivel]

    db.commit()
    db.refresh(solicitud)
    return _cargar_solicitud_completa(db, solicitud.id_solicitud)


def _cargar_solicitud_completa(db: Session, id_solicitud: uuid.UUID) -> SolicitudCredito:
    return (
        db.query(SolicitudCredito)
        .options(
            selectinload(SolicitudCredito.scoring),
            selectinload(SolicitudCredito.evaluacion_rds),
            selectinload(SolicitudCredito.aprobaciones),
        )
        .filter(SolicitudCredito.id_solicitud == id_solicitud)
        .first()
    )


@router.get("/", response_model=list[SolicitudOut])
def listar_solicitudes(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """
    Un CLIENTE ve solo sus propias solicitudes; el personal del Core
    (asesor, admin, jefe regional, riesgos, comité) ve la bandeja completa.
    """
    rol = db.get(Rol, usuario.id_rol)
    query = db.query(SolicitudCredito).options(
        selectinload(SolicitudCredito.scoring),
        selectinload(SolicitudCredito.evaluacion_rds),
        selectinload(SolicitudCredito.aprobaciones),
    )

    if rol.codigo == "CLIENTE":
        cliente = db.query(Cliente).filter(Cliente.id_usuario == usuario.id_usuario).first()
        if cliente is None:
            return []
        query = query.filter(SolicitudCredito.id_cliente == cliente.id_cliente)

    return query.order_by(SolicitudCredito.creado_en.desc()).all()


@router.get("/{id_solicitud}", response_model=SolicitudOut)
def obtener_solicitud(
    id_solicitud: uuid.UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    solicitud = _cargar_solicitud_completa(db, id_solicitud)
    if solicitud is None:
        raise HTTPException(404, "Solicitud no encontrada")
    return solicitud


@router.post("/{id_solicitud}/opinar", response_model=SolicitudOut)
def opinar_solicitud(
    id_solicitud: uuid.UUID,
    payload: OpinionRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """
    Registra la opinión del nivel que corresponde según el estado actual
    de la solicitud. El rol del usuario debe coincidir con el nivel esperado
    -- si no, 403. Esto es lo que materializa la "ruta de aprobación por
    montos" del Criterio 2 como una máquina de estados real, no decorativa.
    """
    solicitud = db.get(SolicitudCredito, id_solicitud)
    if solicitud is None:
        raise HTTPException(404, "Solicitud no encontrada")

    rol_requerido = ROL_ESPERADO_POR_ESTADO.get(solicitud.estado)
    if rol_requerido is None:
        raise HTTPException(400, f"La solicitud no está en un estado que admita opinión (estado actual: {solicitud.estado})")

    rol_usuario = db.get(Rol, usuario.id_rol)
    if rol_usuario.codigo != rol_requerido:
        raise HTTPException(403, f"Esta solicitud requiere la opinión de {rol_requerido}, no de {rol_usuario.codigo}")

    nivel = NIVEL_POR_ESTADO[solicitud.estado]
    db.add(Aprobacion(
        id_solicitud=solicitud.id_solicitud,
        id_usuario=usuario.id_usuario,
        nivel=nivel,
        decision=payload.decision,
        comentario=payload.comentario,
    ))

    if payload.decision == "RECHAZADO":
        solicitud.estado = "RECHAZADA"
        solicitud.motivo_rechazo = payload.comentario or f"Rechazado por {rol_requerido}"
    else:
        regla = _obtener_regla_matriz(db, float(solicitud.monto_solicitado))
        solicitud.estado = svc.siguiente_estado(nivel, regla)

    db.commit()
    return _cargar_solicitud_completa(db, id_solicitud)


@router.post("/{id_solicitud}/desembolsar", response_model=DesembolsoOut)
def desembolsar_solicitud(
    id_solicitud: uuid.UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """
    Cierra el ciclo del Criterio 1: genera el crédito, el cronograma de
    cuotas, y refleja el desembolso como un movimiento en la cuenta del
    cliente -- que el Homebanking verá de inmediato porque lee la misma fila.
    """
    rol = db.get(Rol, usuario.id_rol)
    if rol.codigo not in ("ADMINISTRADOR", "GERENCIA"):
        raise HTTPException(403, "Solo un Administrador o Gerencia puede ejecutar el desembolso")

    solicitud = db.get(SolicitudCredito, id_solicitud)
    if solicitud is None:
        raise HTTPException(404, "Solicitud no encontrada")
    if solicitud.estado != "APROBADA":
        raise HTTPException(400, f"La solicitud debe estar APROBADA para desembolsar (estado actual: {solicitud.estado})")

    producto = db.get(ProductoCredito, solicitud.id_producto)
    cuenta = db.query(Cuenta).filter(Cuenta.id_cliente == solicitud.id_cliente, Cuenta.estado == "ACTIVA").first()
    if cuenta is None:
        raise HTTPException(400, "El cliente no tiene una cuenta activa para recibir el desembolso")

    fecha_hoy = date.today()
    credito = Credito(
        id_solicitud=solicitud.id_solicitud,
        id_cliente=solicitud.id_cliente,
        id_cuenta_desembolso=cuenta.id_cuenta,
        monto_desembolsado=solicitud.monto_solicitado,
        tasa_interes_anual=producto.tasa_interes_anual,
        plazo_meses=solicitud.plazo_meses,
        fecha_desembolso=fecha_hoy,
        estado="VIGENTE",
        banda_mora_actual="VIGENTE",
    )
    db.add(credito)
    db.flush()

    cuotas = svc.generar_cronograma_frances(
        credito.id_credito, float(solicitud.monto_solicitado), float(producto.tasa_interes_anual),
        solicitud.plazo_meses, fecha_hoy,
    )
    db.add_all(cuotas)

    cuenta.saldo_disponible = float(cuenta.saldo_disponible) + float(solicitud.monto_solicitado)
    db.add(Movimiento(
        id_cuenta=cuenta.id_cuenta,
        tipo_movimiento="DESEMBOLSO_CREDITO",
        monto=solicitud.monto_solicitado,
        saldo_posterior=cuenta.saldo_disponible,
        canal_origen="CORE",
        referencia=str(credito.id_credito),
        descripcion=f"Desembolso de crédito {producto.nombre}",
    ))

    solicitud.estado = "DESEMBOLSADA"
    db.commit()
    db.refresh(credito)

    return DesembolsoOut(
        id_credito=credito.id_credito,
        monto_desembolsado=float(credito.monto_desembolsado),
        fecha_desembolso=credito.fecha_desembolso,
        numero_cuotas=len(cuotas),
        primera_cuota_vencimiento=cuotas[0].fecha_vencimiento,
        nuevo_saldo_cuenta=float(cuenta.saldo_disponible),
    )
