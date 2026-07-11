from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from app.services.referidos import obtener_o_crear_codigo, canjear_codigo
from app.services.auth import verificar_token

router = APIRouter(prefix="/referidos", tags=["Programa de Referidos"])


@router.get("/mi-codigo/{usuario_id}")
def mi_codigo(usuario_id: str, x_access_token: str = Header(None)):
    """Devuelve el código de invitación de la persona (lo genera la primera vez)."""
    try:
        verificar_token(usuario_id, x_access_token)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    try:
        codigo = obtener_o_crear_codigo(usuario_id)
        return {"codigo": codigo}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


class DatosCanje(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"])
    codigo: str = Field(..., examples=["LUIS4K92"])


@router.post("/canjear")
def canjear(datos: DatosCanje, x_access_token: str = Header(None)):
    """
    Canjea un código de invitación: da días de premium gratis tanto a
    quien se une como a quien invitó.
    """
    try:
        verificar_token(datos.usuario_id, x_access_token)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    try:
        resultado = canjear_codigo(datos.usuario_id, datos.codigo)
        return {
            "mensaje": f"¡Listo! Ganaste {resultado['dias_otorgados']} días de premium gratis, "
                       f"y la persona que te invitó también.",
            **resultado,
        }
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
