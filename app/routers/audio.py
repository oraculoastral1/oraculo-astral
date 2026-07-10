from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

from app.services.audio_narracion import narrar_texto
from app.services.carta_natal import calcular_carta_natal
from app.services.lectura_diaria import generar_lectura_diaria

router = APIRouter(prefix="/audio", tags=["Audio Narrado"])


class TextoParaNarrar(BaseModel):
    texto: str = Field(..., examples=["Hoy es un buen día para confiar en tu intuición."])


@router.post("/narrar")
def narrar(datos: TextoParaNarrar):
    """Convierte cualquier texto en audio narrado (mp3)."""
    try:
        audio_bytes = narrar_texto(datos.texto)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return Response(content=audio_bytes, media_type="audio/mpeg")


class DatosParaLecturaNarrada(BaseModel):
    fecha: str = Field(..., examples=["1995-03-21"])
    hora: str = Field(..., examples=["14:30"])
    ciudad: str = Field(default="Medellín", examples=["Medellín"])


@router.post("/lectura-diaria-narrada")
def lectura_diaria_narrada(datos: DatosParaLecturaNarrada):
    """
    Genera la lectura diaria completa (astrología + numerología + tarot)
    y la devuelve ya convertida en audio (mp3), lista para reproducir.
    """
    try:
        carta = calcular_carta_natal(fecha=datos.fecha, hora=datos.hora, ciudad=datos.ciudad)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        resultado = generar_lectura_diaria(fecha_nacimiento=datos.fecha, carta_natal=carta)
        audio_bytes = narrar_texto(resultado["lectura"])
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return Response(content=audio_bytes, media_type="audio/mpeg")
