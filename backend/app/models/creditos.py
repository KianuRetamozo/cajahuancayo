import uuid
from datetime import datetime, date

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Numeric, Date, Integer
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

estado_solicitud_enum = ENUM(
    "PENDIENTE", "EN_EVALUACION", "OPINION_ADMINISTRADOR", "OPINION_JEFE_REGIONAL",
    "OPINION_RIESGOS", "COMITE", "APROBADA", "RECHAZADA", "DESEMBOLSADA", "ANULADA",
    name="estado_solicitud", create_type=False,
)
semaforo_rds_enum = ENUM("VERDE", "AMARILLO", "ROJO", name="semaforo_rds", create_type=False)
canal_origen_enum = ENUM("HOMEBANKING", "AGENCIA", "CORE", "SISTEMA", name="canal_origen", create_type=False)
estado_credito_enum = ENUM(
    "VIGENTE", "EN_MORA", "JUDICIAL", "CASTIGADO", "CANCELADO",
    name="estado_credito", create_type=False,
)
banda_mora_enum = ENUM(
    "VIGENTE", "PREVENTIVA", "TEMPRANA", "TARDIA", "JUDICIAL", "CASTIGO",
    name="banda_mora", create_type=False,
)


class ProductoCredito(Base):
    __tablename__ = "productos_credito"

    id_producto: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    tasa_interes_anual: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    monto_minimo: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    monto_maximo: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    plazo_min_meses: Mapped[int] = mapped_column(Integer, nullable=False)
    plazo_max_meses: Mapped[int] = mapped_column(Integer, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class SolicitudCredito(Base):
    __tablename__ = "solicitudes_credito"

    id_solicitud: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_cliente: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clientes.id_cliente"), nullable=False)
    id_producto: Mapped[int] = mapped_column(ForeignKey("productos_credito.id_producto"), nullable=False)
    monto_solicitado: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    plazo_meses: Mapped[int] = mapped_column(Integer, nullable=False)
    canal_origen: Mapped[str] = mapped_column(canal_origen_enum, default="HOMEBANKING")
    estado: Mapped[str] = mapped_column(estado_solicitud_enum, default="PENDIENTE")
    id_asesor_asignado: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"))
    motivo_rechazo: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    scoring: Mapped["ScoringCrediticio"] = relationship(back_populates="solicitud", uselist=False)
    evaluacion_rds: Mapped["EvaluacionRDS"] = relationship(back_populates="solicitud", uselist=False)
    aprobaciones: Mapped[list["Aprobacion"]] = relationship(back_populates="solicitud")


class ScoringCrediticio(Base):
    __tablename__ = "scoring_crediticio"

    id_scoring: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_solicitud: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("solicitudes_credito.id_solicitud"), unique=True, nullable=False)
    puntaje: Mapped[int] = mapped_column(Integer, nullable=False)
    historial_pagos: Mapped[int] = mapped_column(Integer, default=0)
    antiguedad_laboral: Mapped[int] = mapped_column(Integer, default=0)
    endeudamiento_actual: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    calculado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    solicitud: Mapped["SolicitudCredito"] = relationship(back_populates="scoring")


class EvaluacionRDS(Base):
    __tablename__ = "evaluaciones_rds"

    id_evaluacion: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_solicitud: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("solicitudes_credito.id_solicitud"), unique=True, nullable=False)
    ingreso_mensual: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    cuota_estimada: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    deuda_actual_mensual: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    rds: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    semaforo: Mapped[str] = mapped_column(semaforo_rds_enum, nullable=False)
    calculado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    solicitud: Mapped["SolicitudCredito"] = relationship(back_populates="evaluacion_rds")


class MatrizAprobacion(Base):
    __tablename__ = "matriz_aprobacion"

    id_regla: Mapped[int] = mapped_column(Integer, primary_key=True)
    monto_desde: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    monto_hasta: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    requiere_admin: Mapped[bool] = mapped_column(Boolean, default=True)
    requiere_jefe_regional: Mapped[bool] = mapped_column(Boolean, default=False)
    requiere_riesgos: Mapped[bool] = mapped_column(Boolean, default=False)
    requiere_comite: Mapped[bool] = mapped_column(Boolean, default=False)


class Aprobacion(Base):
    __tablename__ = "aprobaciones"

    id_aprobacion: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_solicitud: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("solicitudes_credito.id_solicitud"), nullable=False)
    id_usuario: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False)
    nivel: Mapped[str] = mapped_column(String(30), nullable=False)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    comentario: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    solicitud: Mapped["SolicitudCredito"] = relationship(back_populates="aprobaciones")


class Credito(Base):
    __tablename__ = "creditos"

    id_credito: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_solicitud: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("solicitudes_credito.id_solicitud"), unique=True, nullable=False)
    id_cliente: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clientes.id_cliente"), nullable=False)
    id_cuenta_desembolso: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cuentas.id_cuenta"), nullable=False)
    monto_desembolsado: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    tasa_interes_anual: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    plazo_meses: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_desembolso: Mapped[date] = mapped_column(Date, default=date.today)
    estado: Mapped[str] = mapped_column(estado_credito_enum, default="VIGENTE")
    banda_mora_actual: Mapped[str] = mapped_column(banda_mora_enum, default="VIGENTE")
    dias_atraso: Mapped[int] = mapped_column(Integer, default=0)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    cronograma: Mapped[list["CuotaCronograma"]] = relationship(back_populates="credito")


class CuotaCronograma(Base):
    __tablename__ = "cronograma_pagos"

    id_cuota: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_credito: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("creditos.id_credito"), nullable=False)
    numero_cuota: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_vencimiento: Mapped[date] = mapped_column(Date, nullable=False)
    monto_cuota: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    monto_capital: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    monto_interes: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    pagado: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_pago: Mapped[date | None] = mapped_column(Date)

    credito: Mapped["Credito"] = relationship(back_populates="cronograma")
