from fastapi import APIRouter, HTTPException, Response, Header
from pydantic import BaseModel, Field

from app.services.audio_narracion import narrar_texto
from app.services.carta_natal import calcular_carta_natal
from app.services.lectura_diaria import generar_lectura_diaria
from app.services.suscripciones import tiene_premium_activo
from app.services.auth import verificar_token

router = APIRouter(prefix="/audio", tags=["Audio Narrado"])


def _exigir_identidad_y_premium(usuario_id: str, token: str | None) -> None:
    """Primero confirma que es quien dice ser, luego que tiene premium."""
    try:
        verificar_token(usuario_id, token)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    if not tiene_premium_activo(usuario_id):
        raise HTTPException(
            status_code=402,
            detail="El audio narrado es una función premium. Esta persona no tiene una suscripción activa.",
        )


class TextoParaNarrar(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"])
    texto: str = Field(..., examples=["Hoy es un buen día para confiar en tu intuición."])


@router.post("/narrar")
def narrar(datos: TextoParaNarrar, x_access_token: str = Header(None)):
    """Convierte cualquier texto en audio narrado (mp3). Requiere identidad verificada + premium."""
    _exigir_identidad_y_premium(datos.usuario_id, x_access_token)

    try:
        audio_bytes = narrar_texto(datos.texto)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al narrar el audio: {e}")

    return Response(content=audio_bytes, media_type="audio/mpeg")


class DatosParaLecturaNarrada(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"])
    fecha: str = Field(..., examples=["1995-03-21"])
    hora: str = Field(..., examples=["14:30"])
    ciudad: str = Field(default="Medellín", examples=["Medellín"])


@router.post("/lectura-diaria-narrada")
def lectura_diaria_narrada(datos: DatosParaLecturaNarrada, x_access_token: str = Header(None)):
    """
    Genera la lectura diaria completa (astrología + numerología + tarot)
    y la devuelve ya convertida en audio (mp3), lista para reproducir.
    Requiere identidad verificada + premium.
    """
    _exigir_identidad_y_premium(datos.usuario_id, x_access_token)

    try:
        carta = calcular_carta_natal(fecha=datos.fecha, hora=datos.hora, ciudad=datos.ciudad)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        resultado = generar_lectura_diaria(fecha_nacimiento=datos.fecha, carta_natal=carta)
        audio_bytes = narrar_texto(resultado["lectura"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la lectura narrada: {e}")

    return Response(content=audio_bytes, media_type="audio/mpeg")
