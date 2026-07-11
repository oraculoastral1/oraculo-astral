import os
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from app.services.auth import verificar_token

router = APIRouter(prefix="/resenas", tags=["Reseñas"])


def _config_supabase() -> tuple[str, dict]:
    url_base = os.environ.get("SUPABASE_URL", "").rstrip("/")
    clave = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url_base or not clave:
        raise RuntimeError("Faltan configurar SUPABASE_URL y SUPABASE_SERVICE_KEY.")
    headers = {"apikey": clave, "Authorization": f"Bearer {clave}", "Content-Type": "application/json"}
    return f"{url_base}/rest/v1/resenas", headers


class DatosResena(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"])
    calificacion: int = Field(..., ge=1, le=5, examples=[5])
    texto: str = Field(..., examples=["Lo abro apenas despierto, se ha vuelto mi ritual favorito."])


@router.post("/enviar")
def enviar_resena(datos: DatosResena, x_access_token: str = Header(None)):
    """Guarda la reseña de una persona (queda pendiente de aprobación manual antes de mostrarse)."""
    try:
        verificar_token(datos.usuario_id, x_access_token)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    import requests
    url, headers = _config_supabase()
    fila = {"usuario_id": datos.usuario_id, "calificacion": datos.calificacion, "texto": datos.texto}
    respuesta = requests.post(url, headers=headers, json=fila, timeout=15)
    if not respuesta.ok:
        raise HTTPException(status_code=500, detail=f"No se pudo guardar la reseña: {respuesta.text}")

    return {"mensaje": "¡Gracias por compartir tu experiencia! ✦"}
