from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.auth import generar_token, existe_token
from app.services.recuperacion import generar_y_enviar_codigo, verificar_codigo

router = APIRouter(prefix="/auth", tags=["Autenticación"])


class DatosGenerarToken(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"])


@router.post("/generar-token")
def generar_token_acceso(datos: DatosGenerarToken):
    """
    Genera el token de acceso de una persona — SOLO la primera vez que
    usa la app. Si ya existe una cuenta con este usuario_id, este endpoint
    se niega a sobrescribirla (eso sería una puerta trasera: cualquiera que
    supiera el correo de otra persona podría robarle el acceso). Para
    recuperar el acceso a una cuenta existente, usa /auth/solicitar-recuperacion.
    """
    try:
        if existe_token(datos.usuario_id):
            raise HTTPException(
                status_code=409,
                detail="Ya existe una cuenta con este correo. Usa /auth/solicitar-recuperacion "
                       "para recibir un código y recuperar tu acceso — por tu seguridad, no se "
                       "puede generar un token nuevo sin verificar que el correo es tuyo.",
            )
        token = generar_token(datos.usuario_id)
        return {
            "token": token,
            "aviso": "Guarda este token — no se puede volver a mostrar. Todos los demás "
                     "endpoints que devuelven tus datos ahora lo exigen en el encabezado X-Access-Token.",
        }
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


class DatosSolicitarRecuperacion(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"])


@router.post("/solicitar-recuperacion")
def solicitar_recuperacion(datos: DatosSolicitarRecuperacion):
    """
    Envía un código de 6 dígitos al correo de la persona, válido por 10 minutos,
    para poder recuperar el acceso sin exponer la cuenta a cualquiera que solo
    conozca el correo.
    """
    try:
        generar_y_enviar_codigo(datos.usuario_id)
        return {"mensaje": "Si existe una cuenta con este correo, te enviamos un código de verificación."}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


class DatosVerificarRecuperacion(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"])
    codigo: str = Field(..., examples=["123456"])


@router.post("/verificar-recuperacion")
def verificar_recuperacion(datos: DatosVerificarRecuperacion):
    """
    Verifica el código recibido por email y, si es correcto, emite un
    token de acceso nuevo para la cuenta — el anterior deja de servir.
    """
    try:
        verificar_codigo(datos.usuario_id, datos.codigo)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    try:
        token = generar_token(datos.usuario_id)
        return {
            "token": token,
            "aviso": "Guarda este token — no se puede volver a mostrar.",
        }
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
