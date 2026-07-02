import uuid
from datetime import datetime, date

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Numeric, Date, Integer
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

tipo_gestion_enum = ENUM(
    "LLAMADA", "SMS", "EMAIL", "VISITA", "CARTA_NOTARIAL", "ACUERDO_PAGO",
    name="tipo_gestion_cobranza", create_type=False,
)
resultado_gestion_enum = ENUM(
    "CONTACTADO", "NO_CONTACTADO", "PROMESA_PAGO", "PAGO_REALIZADO", "SE_NIEGA_PAGAR", "NUMERO_INVALIDO",
    name="resultado_gestion", create_type=False,
)
banda_mora_enum = ENUM(
    "VIGENTE", "PREVENTIVA", "TEMPRANA", "TARDIA", "JUDICIAL", "CASTIGO",
    name="banda_mora", create_type=False,
)


class GestionCobranza(Base):
    __tablename__ = "gestiones_cobranza"

    id_gestion: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_credito: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("creditos.id_credito"), nullable=False)
    id_usuario: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False)
    tipo_gestion: Mapped[str] = mapped_column(tipo_gestion_enum, nullable=False)
    resultado: Mapped[str] = mapped_column(resultado_gestion_enum, nullable=False)
    monto_prometido: Mapped[float | None] = mapped_column(Numeric(12, 2))
    fecha_promesa: Mapped[date | None] = mapped_column(Date)
    observacion: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class HistorialTransicionMora(Base):
    __tablename__ = "historial_transiciones_mora"

    id_transicion: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_credito: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("creditos.id_credito"), nullable=False)
    banda_anterior: Mapped[str] = mapped_column(banda_mora_enum, nullable=False)
    banda_nueva: Mapped[str] = mapped_column(banda_mora_enum, nullable=False)
    dias_atraso_al_cambio: Mapped[int] = mapped_column(Integer, nullable=False)
    id_usuario_autoriza: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"))
    es_automatico: Mapped[bool] = mapped_column(Boolean, default=True)
    observacion: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
