from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from app.services.carta_natal import calcular_carta_natal
from app.services.ciudades import buscar_ciudad
from app.services.retorno_solar import generar_lectura_retorno_solar
from app.services.suscripciones import tiene_premium_activo
from app.services.auth import verificar_token

router = APIRouter(prefix="/retorno-solar", tags=["Retorno Solar"])


class DatosRetornoSolar(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"])
    nombre: str = Field(default="", examples=["Ana"])
    fecha: str = Field(..., examples=["1995-03-21"])
    hora: str = Field(..., examples=["14:30"])
    ciudad: str = Field(default="Medellín", examples=["Medellín"])


@router.post("/generar")
def generar_retorno_solar(datos: DatosRetornoSolar, x_access_token: str = Header(None)):
    """
    Calcula el retorno solar de la persona (el momento exacto en que el Sol
    vuelve a su posición de nacimiento) y genera la lectura de su año astral.
    Requiere identidad verificada + premium.
    """
    try:
        verificar_token(datos.usuario_id, x_access_token)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    if not tiene_premium_activo(datos.usuario_id):
        raise HTTPException(
            status_code=402,
            detail="El retorno solar es una función premium. Esta persona no tiene una suscripción activa.",
        )

    try:
        carta = calcular_carta_natal(fecha=datos.fecha, hora=datos.hora, ciudad=datos.ciudad)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    info_ciudad = buscar_ciudad(datos.ciudad)
    lat, lon = (info_ciudad["lat"], info_ciudad["lon"]) if info_ciudad else (carta["coordenadas"]["lat"], carta["coordenadas"]["lon"])

    try:
        nombre = datos.nombre.strip() or "esta persona"
        resultado = generar_lectura_retorno_solar(nombre, carta, lat, lon)
        return resultado
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
