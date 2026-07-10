from fastapi import APIRouter, HTTPException

from app.services.historial import obtener_historial, calcular_patrones

router = APIRouter(prefix="/historial", tags=["Dashboard Personal"])


@router.get("/{usuario_id}")
def historial(usuario_id: str, limite: int = 30):
    """Devuelve las últimas lecturas guardadas de una persona, de más reciente a más antigua."""
    try:
        return {"usuario_id": usuario_id, "lecturas": obtener_historial(usuario_id, limite)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{usuario_id}/patrones")
def patrones(usuario_id: str):
    """
    Analiza el historial completo y devuelve patrones personales:
    cartas de tarot que más se repiten, proporción de cartas reversas,
    y el rango de fechas cubierto por las lecturas guardadas.
    """
    try:
        return calcular_patrones(usuario_id)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
