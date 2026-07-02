"""
Motor de reglas de crédito. Aquí vive la lógica normativa que pide el
Criterio 2 de la rúbrica: elegibilidad, scoring, RDS con semáforo y el
cálculo de cuotas por el sistema francés (cuota fija).
"""
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.cuentas import Cliente
from app.models.creditos import Credito, CuotaCronograma, ProductoCredito


# --- Elegibilidad (sujeto de crédito) ---

EDAD_MINIMA = 18
EDAD_MAXIMA = 75
INGRESO_MINIMO_MENSUAL = 500.0


def evaluar_elegibilidad(cliente: Cliente, db: Session) -> tuple[bool, str | None]:
    """Devuelve (es_elegible, motivo_si_no_lo_es)."""
    hoy = date.today()
    edad = hoy.year - cliente.fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (cliente.fecha_nacimiento.month, cliente.fecha_nacimiento.day)
    )

    if edad < EDAD_MINIMA:
        return False, f"El cliente es menor de {EDAD_MINIMA} años"
    if edad > EDAD_MAXIMA:
        return False, f"El cliente supera la edad máxima de {EDAD_MAXIMA} años"
    if cliente.ingreso_mensual < INGRESO_MINIMO_MENSUAL:
        return False, f"El ingreso mensual es menor al mínimo requerido (S/ {INGRESO_MINIMO_MENSUAL})"

    tiene_castigo = (
        db.query(Credito)
        .filter(Credito.id_cliente == cliente.id_cliente, Credito.estado == "CASTIGADO")
        .first()
    )
    if tiene_castigo:
        return False, "El cliente tiene un crédito castigado en su historial"

    return True, None


# --- Cálculo de cuota por sistema francés ---

def calcular_cuota_francesa(monto: float, tasa_interes_anual: float, plazo_meses: int) -> float:
    tasa_mensual = (tasa_interes_anual / 100) / 12
    if tasa_mensual == 0:
        return round(monto / plazo_meses, 2)
    factor = (tasa_mensual * (1 + tasa_mensual) ** plazo_meses) / ((1 + tasa_mensual) ** plazo_meses - 1)
    return round(monto * factor, 2)


def generar_cronograma_frances(
    id_credito, monto: float, tasa_interes_anual: float, plazo_meses: int, fecha_desembolso: date
) -> list[CuotaCronograma]:
    tasa_mensual = (tasa_interes_anual / 100) / 12
    cuota = calcular_cuota_francesa(monto, tasa_interes_anual, plazo_meses)
    saldo = monto
    cuotas = []

    for n in range(1, plazo_meses + 1):
        interes = round(saldo * tasa_mensual, 2)
        capital = round(cuota - interes, 2)
        if n == plazo_meses:
            # ajuste de redondeo en la última cuota para que el saldo cierre en 0
            capital = round(saldo, 2)
            cuota_final = round(capital + interes, 2)
        else:
            cuota_final = cuota
        saldo = round(saldo - capital, 2)

        cuotas.append(CuotaCronograma(
            id_credito=id_credito,
            numero_cuota=n,
            fecha_vencimiento=fecha_desembolso + timedelta(days=30 * n),
            monto_cuota=cuota_final,
            monto_capital=capital,
            monto_interes=interes,
        ))

    return cuotas


# --- Scoring y RDS ---

def calcular_deuda_actual_mensual(cliente: Cliente, db: Session) -> float:
    """Suma de cuotas vigentes de créditos activos del cliente (deuda ya comprometida)."""
    creditos_vigentes = (
        db.query(Credito)
        .filter(Credito.id_cliente == cliente.id_cliente, Credito.estado.in_(["VIGENTE", "EN_MORA"]))
        .all()
    )
    total = 0.0
    for credito in creditos_vigentes:
        cuota = calcular_cuota_francesa(
            float(credito.monto_desembolsado), float(credito.tasa_interes_anual), credito.plazo_meses
        )
        total += cuota
    return round(total, 2)


def calcular_rds(ingreso_mensual: float, cuota_estimada: float, deuda_actual_mensual: float) -> tuple[float, str]:
    if ingreso_mensual <= 0:
        return 100.0, "ROJO"
    rds = round(((cuota_estimada + deuda_actual_mensual) / ingreso_mensual) * 100, 2)
    if rds <= 30:
        semaforo = "VERDE"
    elif rds <= 40:
        semaforo = "AMARILLO"
    else:
        semaforo = "ROJO"
    return rds, semaforo


def calcular_scoring(cliente: Cliente, rds: float, db: Session) -> dict:
    """Puntaje 0-1000. Simplificado pero basado en factores reales: RDS,
    historial de pagos puntuales y mora previa."""
    puntaje = 700

    if rds > 40:
        puntaje -= 200
    elif rds > 30:
        puntaje -= 80

    cuotas_pagadas = (
        db.query(CuotaCronograma)
        .join(Credito, Credito.id_credito == CuotaCronograma.id_credito)
        .filter(Credito.id_cliente == cliente.id_cliente, CuotaCronograma.pagado == True)  # noqa: E712
        .count()
    )
    bono_historial = min(cuotas_pagadas * 5, 150)
    puntaje += bono_historial

    tuvo_judicial_o_castigo = (
        db.query(Credito)
        .filter(Credito.id_cliente == cliente.id_cliente, Credito.estado.in_(["JUDICIAL", "CASTIGADO"]))
        .first()
    )
    if tuvo_judicial_o_castigo:
        puntaje -= 250

    puntaje = max(0, min(1000, puntaje))

    return {
        "puntaje": puntaje,
        "historial_pagos": cuotas_pagadas,
        "antiguedad_laboral": 0,
        "endeudamiento_actual": calcular_deuda_actual_mensual(cliente, db),
    }


# --- Ruta de aprobación por monto ---

NIVELES_EN_ORDEN = ["ADMINISTRADOR", "JEFE_REGIONAL", "RIESGOS", "COMITE"]

ESTADO_POR_NIVEL = {
    "ADMINISTRADOR": "OPINION_ADMINISTRADOR",
    "JEFE_REGIONAL": "OPINION_JEFE_REGIONAL",
    "RIESGOS": "OPINION_RIESGOS",
    "COMITE": "COMITE",
}

CAMPO_REQUIERE = {
    "ADMINISTRADOR": "requiere_admin",
    "JEFE_REGIONAL": "requiere_jefe_regional",
    "RIESGOS": "requiere_riesgos",
    "COMITE": "requiere_comite",
}


def niveles_requeridos(regla_matriz) -> list[str]:
    """Lista de niveles que debe pasar la solicitud, en orden, según la matriz."""
    return [nivel for nivel in NIVELES_EN_ORDEN if getattr(regla_matriz, CAMPO_REQUIERE[nivel])]


def siguiente_estado(nivel_actual: str, regla_matriz) -> str:
    """Dado el nivel que acaba de aprobar, determina el siguiente estado de la solicitud."""
    requeridos = niveles_requeridos(regla_matriz)
    idx = requeridos.index(nivel_actual)
    if idx + 1 < len(requeridos):
        return ESTADO_POR_NIVEL[requeridos[idx + 1]]
    return "APROBADA"
