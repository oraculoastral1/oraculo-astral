from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.interpretacion_suenos import interpretar_sueño

router = APIRouter(prefix="/suenos", tags=["Interpretación de Sueños"])


class DescripcionSueño(BaseModel):
    descripcion: str = Field(
        ...,
        examples=["Soñé que caminaba por una casa desconocida y encontraba una puerta que llevaba a un jardín con una serpiente."],
        description="Describe el sueño con tus propias palabras, lo más detallado posible",
    )


@router.post("/interpretar")
def interpretar(datos: DescripcionSueño):
    try:
        return interpretar_sueño(datos.descripcion)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
