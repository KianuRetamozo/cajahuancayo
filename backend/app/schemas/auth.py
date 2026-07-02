import uuid

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UsuarioOut(BaseModel):
    id_usuario: uuid.UUID
    nombre_completo: str
    correo: str
    rol_codigo: str
    agencia: str | None = None

    model_config = {"from_attributes": True}
