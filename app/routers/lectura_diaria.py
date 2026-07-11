from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from app.services.carta_natal import calcular_carta_natal
from app.services.lectura_diaria import generar_lectura_diaria
from app.services.historial import guardar_lectura
from app.services.auth import verificar_token
from app.services.limites import verificar_y_registrar_uso
from app.services.perfiles import guardar_perfil

router = APIRouter(prefix="/lectura", tags=["Lectura Diaria"])


class DatosParaLectura(BaseModel):
    usuario_id: str = Field(
        ..., examples=["ana@correo.com"],
        description="Identificador de la persona (por ahora, su correo o cualquier texto único)",
    )
    nombre: str = Field(default="", examples=["Ana"])
    fecha: str = Field(..., examples=["1995-03-21"])
    hora: str = Field(..., examples=["14:30"])
    ciudad: str = Field(default="Medellín", examples=["Medellín"])


@router.post("/diaria")
def lectura_diaria(datos: DatosParaLectura, x_access_token: str = Header(None)):
    """
    Calcula la carta natal y genera la lectura diaria completa:
    astrología + numerología + tarot, fusionadas por IA en un solo mensaje.
    La lectura queda guardada automáticamente en el historial de la persona.
    Requiere el token de acceso de esa persona. Límite: 5 por día.
    """
    try:
        verificar_token(datos.usuario_id, x_access_token)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    try:
        verificar_y_registrar_uso(datos.usuario_id, "lectura_diaria")
    except RuntimeError as e:
        raise HTTPException(status_code=429, detail=str(e))

    try:
        carta = calcular_carta_natal(fecha=datos.fecha, hora=datos.hora, ciudad=datos.ciudad)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        resultado = generar_lectura_diaria(fecha_nacimiento=datos.fecha, carta_natal=carta)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    guardado_ok = True
    error_guardado = None
    try:
        guardar_lectura(
            usuario_id=datos.usuario_id,
            fecha_nacimiento=datos.fecha,
            ciudad=datos.ciudad,
            carta_natal=carta,
            numerologia=resultado["numerologia"],
            tarot=resultado["tarot"],
            lectura_texto=resultado["lectura"],
        )
    except RuntimeError as e:
        guardado_ok = False
        error_guardado = str(e)

    try:
        guardar_perfil(datos.usuario_id, datos.nombre, datos.fecha, datos.hora, datos.ciudad)
    except RuntimeError:
        pass  # el perfil es solo para el recordatorio diario — no debe romper la lectura si falla

    return {
        "carta_natal_resumen": {
            "sol": carta["planetas"]["Sol"],
            "luna": carta["planetas"]["Luna"],
            "ascendente": carta["ascendente"],
        },
        "numerologia": resultado["numerologia"],
        "tarot": resultado["tarot"],
        "transitos": resultado["transitos"],
        "lectura": resultado["lectura"],
        "guardado_en_historial": guardado_ok,
        "error_guardado": error_guardado,
    }
