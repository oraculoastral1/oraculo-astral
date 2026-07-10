from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.carta_natal import calcular_carta_natal
from app.services.ciudades import listar_ciudades

router = APIRouter(prefix="/carta-natal", tags=["Carta Natal"])


class DatosNacimiento(BaseModel):
    fecha: str = Field(..., examples=["1995-03-21"], description="Formato YYYY-MM-DD")
    hora: str = Field(..., examples=["14:30"], description="Hora local, formato HH:MM")
    ciudad: str | None = Field(
        default="Medellín",
        examples=["Medellín"],
        description="Nombre de la ciudad de nacimiento (recomendado)",
    )
    lat: float | None = Field(default=None, description="Solo si no envías 'ciudad'")
    lon: float | None = Field(default=None, description="Solo si no envías 'ciudad'")
    zona_horaria: str | None = Field(
        default=None,
        examples=["America/Bogota"],
        description="Solo si no envías 'ciudad'. Nombre de zona horaria IANA.",
    )


@router.post("/calcular")
def calcular(datos: DatosNacimiento):
    try:
        return calcular_carta_natal(
            fecha=datos.fecha,
            hora=datos.hora,
            ciudad=datos.ciudad,
            lat=datos.lat,
            lon=datos.lon,
            zona_horaria=datos.zona_horaria,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ciudades")
def ciudades_disponibles():
    """Lista las ciudades que la app ya reconoce automáticamente."""
    return {"ciudades": listar_ciudades()}
