from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from app.services.soporte import enviar_mensaje_soporte
from app.services.auth import verificar_token

router = APIRouter(prefix="/soporte", tags=["Soporte"])


class DatosSoporte(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"])
    asunto: str = Field(..., examples=["No puedo escuchar el audio de mi lectura"])
    mensaje: str = Field(..., examples=["Cuando toco el botón de audio no pasa nada..."])


@router.post("/enviar")
def enviar(datos: DatosSoporte, x_access_token: str = Header(None)):
    """Envía un mensaje de soporte al equipo de Oráculo Astral. Requiere identidad verificada."""
    try:
        verificar_token(datos.usuario_id, x_access_token)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    try:
        enviar_mensaje_soporte(datos.usuario_id, datos.asunto, datos.mensaje)
        return {"mensaje": "Tu mensaje fue enviado. Te responderemos a tu correo pronto."}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
