import uuid
from datetime import datetime, date

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

canal_origen_enum = ENUM(
    "HOMEBANKING", "AGENCIA", "CORE", "SISTEMA",
    name="canal_origen", create_type=False,
)
tipo_movimiento_enum = ENUM(
    "DEPOSITO", "RETIRO", "DESEMBOLSO_CREDITO", "PAGO_CUOTA", "CARGO_MORA", "AJUSTE",
    name="tipo_movimiento", create_type=False,
)


class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), unique=True)
    tipo_documento: Mapped[str] = mapped_column(String(10), default="DNI")
    numero_documento: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    correo: Mapped[str | None] = mapped_column(String(150))
    telefono: Mapped[str | None] = mapped_column(String(20))
    direccion: Mapped[str | None] = mapped_column(Text)
    ingreso_mensual: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    ocupacion: Mapped[str | None] = mapped_column(String(100))
    es_sujeto_credito: Mapped[bool] = mapped_column(Boolean, default=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    cuentas: Mapped[list["Cuenta"]] = relationship(back_populates="cliente")


class Cuenta(Base):
    __tablename__ = "cuentas"

    id_cuenta: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_cliente: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clientes.id_cliente"), nullable=False)
    numero_cuenta: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    tipo_cuenta: Mapped[str] = mapped_column(String(30), default="AHORROS")
    moneda: Mapped[str] = mapped_column(String(3), default="PEN")
    saldo_disponible: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    estado: Mapped[str] = mapped_column(String(20), default="ACTIVA")
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    cliente: Mapped["Cliente"] = relationship(back_populates="cuentas")
    movimientos: Mapped[list["Movimiento"]] = relationship(back_populates="cuenta")


class Movimiento(Base):
    __tablename__ = "movimientos"

    id_movimiento: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_cuenta: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cuentas.id_cuenta"), nullable=False)
    tipo_movimiento: Mapped[str] = mapped_column(tipo_movimiento_enum, nullable=False)
    monto: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    saldo_posterior: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    canal_origen: Mapped[str] = mapped_column(canal_origen_enum, nullable=False)
    referencia: Mapped[str | None] = mapped_column(String(100))
    descripcion: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    cuenta: Mapped["Cuenta"] = relationship(back_populates="movimientos")
