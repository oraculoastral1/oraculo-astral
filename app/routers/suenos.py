from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from app.services.interpretacion_suenos import interpretar_sueño
from app.services.auth import verificar_token
from app.services.limites import verificar_y_registrar_uso

router = APIRouter(prefix="/suenos", tags=["Interpretación de Sueños"])


class DescripcionSueño(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"])
    descripcion: str = Field(
        ...,
        examples=["Soñé que caminaba por una casa desconocida y encontraba una puerta que llevaba a un jardín con una serpiente."],
        description="Describe el sueño con tus propias palabras, lo más detallado posible",
    )


@router.post("/interpretar")
def interpretar(datos: DescripcionSueño, x_access_token: str = Header(None)):
    """Interpreta un sueño. Requiere identidad verificada. Límite: 10 por día."""
    try:
        verificar_token(datos.usuario_id, x_access_token)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    try:
        verificar_y_registrar_uso(datos.usuario_id, "suenos")
    except RuntimeError as e:
        raise HTTPException(status_code=429, detail=str(e))

    try:
        return interpretar_sueño(datos.descripcion)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
