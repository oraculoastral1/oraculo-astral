from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.auth import generar_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])


class DatosGenerarToken(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"])


@router.post("/generar-token")
def generar_token_acceso(datos: DatosGenerarToken):
    """
    Genera (o renueva) el token de acceso de una persona. GUÁRDALO —
    solo se muestra esta vez, y hace falta para leer cualquier dato
    personal (historial, lecturas, estado de la suscripción).
    """
    try:
        token = generar_token(datos.usuario_id)
        return {
            "token": token,
            "aviso": "Guarda este token — no se puede volver a mostrar. Todos los demás "
                     "endpoints que devuelven tus datos ahora lo exigen en el encabezado X-Access-Token.",
        }
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
