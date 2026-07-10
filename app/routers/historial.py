from fastapi import APIRouter, HTTPException, Header

from app.services.historial import obtener_historial, calcular_patrones
from app.services.auth import verificar_token

router = APIRouter(prefix="/historial", tags=["Dashboard Personal"])


@router.get("/{usuario_id}")
def historial(usuario_id: str, x_access_token: str = Header(None), limite: int = 30):
    """Devuelve las últimas lecturas guardadas de una persona. Requiere su token de acceso."""
    try:
        verificar_token(usuario_id, x_access_token)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    try:
        return {"usuario_id": usuario_id, "lecturas": obtener_historial(usuario_id, limite)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{usuario_id}/patrones")
def patrones(usuario_id: str, x_access_token: str = Header(None)):
    """Analiza el historial completo y devuelve patrones personales. Requiere token de acceso."""
    try:
        verificar_token(usuario_id, x_access_token)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    try:
        return calcular_patrones(usuario_id)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
