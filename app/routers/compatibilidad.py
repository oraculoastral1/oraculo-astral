from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from app.services.carta_natal import calcular_carta_natal
from app.services.compatibilidad import generar_lectura_compatibilidad
from app.services.suscripciones import tiene_premium_activo
from app.services.auth import verificar_token

router = APIRouter(prefix="/compatibilidad", tags=["Compatibilidad"])


class DatosPersona(BaseModel):
    nombre: str = Field(..., examples=["Ana"])
    fecha: str = Field(..., examples=["1995-03-21"])
    hora: str = Field(..., examples=["14:30"])
    ciudad: str = Field(default="Medellín", examples=["Medellín"])


class DatosParaComparar(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"], description="Quién está pidiendo la comparación")
    persona_a: DatosPersona
    persona_b: DatosPersona


@router.post("/comparar")
def comparar(datos: DatosParaComparar, x_access_token: str = Header(None)):
    """
    Calcula las cartas natales de dos personas, compara sus planetas entre sí
    (sinastría), y genera una lectura de compatibilidad fusionada por IA.
    Requiere identidad verificada + premium.
    """
    try:
        verificar_token(datos.usuario_id, x_access_token)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    if not tiene_premium_activo(datos.usuario_id):
        raise HTTPException(
            status_code=402,
            detail="Comparar compatibilidad es una función premium. Esta persona no tiene una suscripción activa.",
        )
    try:
        carta_a = calcular_carta_natal(
            fecha=datos.persona_a.fecha, hora=datos.persona_a.hora, ciudad=datos.persona_a.ciudad
        )
        carta_b = calcular_carta_natal(
            fecha=datos.persona_b.fecha, hora=datos.persona_b.hora, ciudad=datos.persona_b.ciudad
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        resultado = generar_lectura_compatibilidad(
            nombre_a=datos.persona_a.nombre, carta_a=carta_a,
            nombre_b=datos.persona_b.nombre, carta_b=carta_b,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "persona_a": {
            "nombre": datos.persona_a.nombre,
            "sol": carta_a["planetas"]["Sol"]["signo"],
            "luna": carta_a["planetas"]["Luna"]["signo"],
            "ascendente": carta_a["ascendente"]["signo"],
        },
        "persona_b": {
            "nombre": datos.persona_b.nombre,
            "sol": carta_b["planetas"]["Sol"]["signo"],
            "luna": carta_b["planetas"]["Luna"]["signo"],
            "ascendente": carta_b["ascendente"]["signo"],
        },
        "aspectos_cruzados": resultado["aspectos_cruzados"],
        "lectura": resultado["lectura"],
    }
