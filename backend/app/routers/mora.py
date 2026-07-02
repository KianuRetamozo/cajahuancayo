import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_permiso
from app.database import get_db
from app.models.creditos import Credito
from app.models.mora import HistorialTransicionMora
from app.models.rbac import Usuario

router = APIRouter(prefix="/mora", tags=["Recuperaciones / Mora"])


@router.get("/kpis")
def kpis_mora(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_permiso("mora", "leer")),
):
    """R1: consulta por bandas de mora con KPIs. Usa la vista creada en 05_mora_cobranza.sql."""
    filas = db.execute(text("SELECT * FROM vista_kpis_mora")).mappings().all()
    return list(filas)


@router.post("/{id_credito}/derivar-judicial")
def derivar_judicial(
    id_credito: uuid.UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_permiso("mora", "derivar_judicial")),
):
    """
    R3: solo RIESGOS (según la matriz de permisos sembrada) puede confirmar
    la derivación judicial. Cualquier otro rol recibe 403 automáticamente
    por el require_permiso, sin necesidad de chequeos manuales aquí.
    """
    credito = db.get(Credito, id_credito)
    if credito is None:
        raise HTTPException(404, "Crédito no encontrado")
    if credito.dias_atraso < 121:
        raise HTTPException(400, "El crédito no cumple el umbral de 121 días para derivación judicial")

    banda_anterior = credito.banda_mora_actual
    credito.banda_mora_actual = "JUDICIAL"
    credito.estado = "JUDICIAL"

    db.add(HistorialTransicionMora(
        id_credito=credito.id_credito,
        banda_anterior=banda_anterior,
        banda_nueva="JUDICIAL",
        dias_atraso_al_cambio=credito.dias_atraso,
        id_usuario_autoriza=usuario.id_usuario,
        es_automatico=False,
        observacion="Derivación judicial confirmada manualmente",
    ))
    db.commit()
    return {"mensaje": "Crédito derivado a judicial", "id_credito": str(id_credito)}
