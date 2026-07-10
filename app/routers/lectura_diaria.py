from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.carta_natal import calcular_carta_natal
from app.services.lectura_diaria import generar_lectura_diaria

router = APIRouter(prefix="/lectura", tags=["Lectura Diaria"])


class DatosParaLectura(BaseModel):
    fecha: str = Field(..., examples=["1995-03-21"])
    hora: str = Field(..., examples=["14:30"])
    ciudad: str = Field(default="Medellín", examples=["Medellín"])


@router.post("/diaria")
def lectura_diaria(datos: DatosParaLectura):
    """
    Calcula la carta natal y genera la lectura diaria completa:
    astrología + numerología + tarot, fusionadas por IA en un solo mensaje.
    """
    try:
        carta = calcular_carta_natal(fecha=datos.fecha, hora=datos.hora, ciudad=datos.ciudad)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        resultado = generar_lectura_diaria(fecha_nacimiento=datos.fecha, carta_natal=carta)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "carta_natal_resumen": {
            "sol": carta["planetas"]["Sol"],
            "luna": carta["planetas"]["Luna"],
            "ascendente": carta["ascendente"],
        },
        "numerologia": resultado["numerologia"],
        "tarot": resultado["tarot"],
        "lectura": resultado["lectura"],
    }
