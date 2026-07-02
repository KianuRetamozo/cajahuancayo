import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Rol(Base):
    __tablename__ = "roles"

    id_rol: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)

    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="rol")
    permisos: Mapped[list["Permiso"]] = relationship(
        secondary="roles_permisos", back_populates="roles"
    )


class Permiso(Base):
    __tablename__ = "permisos"

    id_permiso: Mapped[int] = mapped_column(Integer, primary_key=True)
    recurso: Mapped[str] = mapped_column(String(60), nullable=False)
    accion: Mapped[str] = mapped_column(String(30), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)

    roles: Mapped[list["Rol"]] = relationship(
        secondary="roles_permisos", back_populates="permisos"
    )


class RolPermiso(Base):
    __tablename__ = "roles_permisos"

    id_rol: Mapped[int] = mapped_column(ForeignKey("roles.id_rol"), primary_key=True)
    id_permiso: Mapped[int] = mapped_column(ForeignKey("permisos.id_permiso"), primary_key=True)


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    id_rol: Mapped[int] = mapped_column(ForeignKey("roles.id_rol"), nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    correo: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    hash_password: Mapped[str] = mapped_column(String(255), nullable=False)
    dni: Mapped[str | None] = mapped_column(String(15), unique=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    agencia: Mapped[str | None] = mapped_column(String(80))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ultimo_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    rol: Mapped["Rol"] = relationship(back_populates="usuarios")
