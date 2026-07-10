from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.carta_natal import calcular_carta_natal

router = APIRouter(prefix="/carta-natal", tags=["Carta Natal"])


class DatosNacimiento(BaseModel):
    fecha: str = Field(..., examples=["1995-03-21"], description="Formato YYYY-MM-DD")
    hora: str = Field(..., examples=["14:30"], description="Hora local, formato HH:MM")
    lat: float = Field(..., examples=[6.2442], description="Latitud del lugar de nacimiento")
    lon: float = Field(..., examples=[-75.5812], description="Longitud del lugar de nacimiento")
    zona_horaria_utc_offset: float = Field(
        ..., examples=[-5], description="Offset horario respecto a UTC, ej: Colombia = -5"
    )


@router.post("/calcular")
def calcular(datos: DatosNacimiento):
    try:
        return calcular_carta_natal(
            fecha=datos.fecha,
            hora=datos.hora,
            lat=datos.lat,
            lon=datos.lon,
            zona_horaria_utc_offset=datos.zona_horaria_utc_offset,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Datos inválidos: {e}")
