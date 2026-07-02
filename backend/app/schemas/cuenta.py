import uuid
from datetime import datetime, date


from pydantic import BaseModel


class MovimientoOut(BaseModel):
    id_movimiento: uuid.UUID
    tipo_movimiento: str
    monto: float
    saldo_posterior: float
    canal_origen: str
    descripcion: str | None = None
    creado_en: datetime

    model_config = {"from_attributes": True}


class CuentaOut(BaseModel):
    id_cuenta: uuid.UUID
    numero_cuenta: str
    tipo_cuenta: str
    moneda: str
    saldo_disponible: float
    estado: str
    movimientos: list[MovimientoOut] = []

    model_config = {"from_attributes": True}


class MiCuentaResponse(BaseModel):
    nombres: str
    apellidos: str
    numero_documento: str
    es_sujeto_credito: bool
    cuentas: list[CuentaOut]
