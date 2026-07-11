from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from app.services.carta_natal import calcular_carta_natal
from app.services.oraculo_chat import responder_pregunta
from app.services.suscripciones import tiene_premium_activo
from app.services.auth import verificar_token
from app.services.limites import verificar_y_registrar_uso

router = APIRouter(prefix="/oraculo", tags=["Pregúntale al Oráculo"])


class TurnoConversacion(BaseModel):
    pregunta: str
    respuesta: str


class DatosPregunta(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"])
    pregunta: str = Field(..., examples=["¿Debería aceptar este nuevo trabajo?"])
    fecha: str = Field(..., examples=["1995-03-21"])
    hora: str = Field(..., examples=["14:30"])
    ciudad: str = Field(default="Medellín", examples=["Medellín"])
    historial: list[TurnoConversacion] = Field(default_factory=list)


@router.post("/preguntar")
def preguntar(datos: DatosPregunta, x_access_token: str = Header(None)):
    """
    Responde una pregunta libre de la persona, usando su carta natal como
    contexto real. Requiere identidad verificada + premium.
    """
    try:
        verificar_token(datos.usuario_id, x_access_token)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    if not tiene_premium_activo(datos.usuario_id):
        raise HTTPException(
            status_code=402,
            detail="Pregúntale al oráculo es una función premium. Esta persona no tiene una suscripción activa.",
        )

    try:
        verificar_y_registrar_uso(datos.usuario_id, "oraculo_chat")
    except RuntimeError as e:
        raise HTTPException(status_code=429, detail=str(e))

    try:
        carta = calcular_carta_natal(fecha=datos.fecha, hora=datos.hora, ciudad=datos.ciudad)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        historial_dict = [h.model_dump() for h in datos.historial]
        respuesta = responder_pregunta(datos.pregunta, carta, historial_dict)
        return {"respuesta": respuesta}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
