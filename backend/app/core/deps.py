"""
Dependencias de autorización. CLAVE del Criterio 3: el control de acceso
se valida aquí, en el backend, no solo ocultando botones en el frontend.
Cualquier rol que no tenga el permiso recibe 403, sin excepción.
"""
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.database import get_db
from app.models.rbac import Usuario, Rol, Permiso

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    usuario = db.get(Usuario, uuid.UUID(user_id))
    if usuario is None or not usuario.activo:
        raise credentials_exception
    return usuario


def require_permiso(recurso: str, accion: str):
    """
    Devuelve una dependencia que exige que el rol del usuario actual
    tenga asignado el permiso (recurso, accion). Uso:

        @router.post("/comite/resolver", dependencies=[Depends(require_permiso("comite", "resolver"))])
    """

    def _checker(
        usuario: Usuario = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Usuario:
        tiene_permiso = (
            db.query(Permiso)
            .join(Permiso.roles)
            .filter(Rol.id_rol == usuario.id_rol, Permiso.recurso == recurso, Permiso.accion == accion)
            .first()
        )
        if tiene_permiso is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"El rol no tiene permiso para '{accion}' sobre '{recurso}'",
            )
        return usuario

    return _checker


def require_rol(*codigos_rol: str):
    """Alternativa más simple cuando basta con restringir por código de rol."""

    def _checker(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)) -> Usuario:
        rol = db.get(Rol, usuario.id_rol)
        if rol is None or rol.codigo not in codigos_rol:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Esta acción requiere uno de estos roles: {', '.join(codigos_rol)}",
            )
        return usuario

    return _checker
