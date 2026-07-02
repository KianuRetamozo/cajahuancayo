import uuid
from datetime import datetime, date

from pydantic import BaseModel, Field


class SolicitudCreate(BaseModel):
    id_producto: int
    monto_solicitado: float = Field(gt=0)
    plazo_meses: int = Field(gt=0)


class ScoringOut(BaseModel):
    puntaje: int
    historial_pagos: int
    antiguedad_laboral: int
    endeudamiento_actual: float

    model_config = {"from_attributes": True}


class EvaluacionRDSOut(BaseModel):
    ingreso_mensual: float
    cuota_estimada: float
    deuda_actual_mensual: float
    rds: float
    semaforo: str

    model_config = {"from_attributes": True}


class AprobacionOut(BaseModel):
    nivel: str
    decision: str
    comentario: str | None
    creado_en: datetime

    model_config = {"from_attributes": True}


class SolicitudOut(BaseModel):
    id_solicitud: uuid.UUID
    id_cliente: uuid.UUID
    id_producto: int
    monto_solicitado: float
    plazo_meses: int
    canal_origen: str
    estado: str
    motivo_rechazo: str | None
    creado_en: datetime
    scoring: ScoringOut | None = None
    evaluacion_rds: EvaluacionRDSOut | None = None
    aprobaciones: list[AprobacionOut] = []

    model_config = {"from_attributes": True}


class OpinionRequest(BaseModel):
    decision: str = Field(pattern="^(APROBADO|RECHAZADO)$")
    comentario: str | None = None


class DesembolsoOut(BaseModel):
    id_credito: uuid.UUID
    monto_desembolsado: float
    fecha_desembolso: date
    numero_cuotas: int
    primera_cuota_vencimiento: date
    nuevo_saldo_cuenta: float
