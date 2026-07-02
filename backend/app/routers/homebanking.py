from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user
from app.database import get_db
from app.models.cuentas import Cliente, Cuenta, Movimiento
from app.models.rbac import Usuario
from app.schemas.cuenta import MiCuentaResponse, CuentaOut

router = APIRouter(prefix="/homebanking", tags=["Homebanking"])


@router.get("/mi-cuenta", response_model=MiCuentaResponse)
def mi_cuenta(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """
    Devuelve el perfil del cliente logueado con sus cuentas y últimos
    movimientos. Esta es la prueba viva de la integración Core<->Homebanking:
    cualquier movimiento que el Core registre (desembolso, pago de cuota)
    aparece aquí de inmediato porque ambos leen la misma tabla `movimientos`.
    """
    cliente = db.query(Cliente).filter(Cliente.id_usuario == usuario.id_usuario).first()
    if cliente is None:
        raise HTTPException(404, "Este usuario no tiene un perfil de cliente asociado")

    cuentas = (
        db.query(Cuenta)
        .options(selectinload(Cuenta.movimientos))
        .filter(Cuenta.id_cliente == cliente.id_cliente)
        .all()
    )

    cuentas_out = []
    for c in cuentas:
        movs_ordenados = sorted(c.movimientos, key=lambda m: m.creado_en, reverse=True)[:10]
        cuentas_out.append(
            CuentaOut(
                id_cuenta=c.id_cuenta,
                numero_cuenta=c.numero_cuenta,
                tipo_cuenta=c.tipo_cuenta,
                moneda=c.moneda,
                saldo_disponible=float(c.saldo_disponible),
                estado=c.estado,
                movimientos=movs_ordenados,
            )
        )

    return MiCuentaResponse(
        nombres=cliente.nombres,
        apellidos=cliente.apellidos,
        numero_documento=cliente.numero_documento,
        es_sujeto_credito=cliente.es_sujeto_credito,
        cuentas=cuentas_out,
    )
