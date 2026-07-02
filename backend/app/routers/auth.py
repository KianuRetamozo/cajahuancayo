from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.database import get_db
from app.models.rbac import Usuario, Rol
from app.schemas.auth import LoginRequest, TokenResponse, UsuarioOut

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.correo == payload.correo).first()

    if usuario is None or not usuario.activo or not verify_password(payload.password, usuario.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )

    rol = db.get(Rol, usuario.id_rol)
    token_data = {"sub": str(usuario.id_usuario), "rol": rol.codigo}

    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.get("/me", response_model=UsuarioOut)
def obtener_perfil(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    rol = db.get(Rol, usuario.id_rol)
    return UsuarioOut(
        id_usuario=usuario.id_usuario,
        nombre_completo=usuario.nombre_completo,
        correo=usuario.correo,
        rol_codigo=rol.codigo,
        agencia=usuario.agencia,
    )
