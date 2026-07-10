from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel, Field

from app.services.pagos_wompi import generar_link_pago, procesar_webhook as procesar_webhook_wompi
from app.services.suscripciones import obtener_estado
from app.services.auth import verificar_token

router = APIRouter(prefix="/pagos", tags=["Pagos y Suscripción"])

# Nota: Stripe se deja fuera por ahora a propósito (no configurado todavía).
# Cuando se quiera activar, se restauran las importaciones y rutas de Stripe aquí.


# --- Wompi ---

class DatosCheckoutWompi(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"])
    url_redireccion: str = Field(..., examples=["https://tu-frontend.com/pago-completado"])


@router.post("/wompi/crear-link")
def wompi_crear_link(datos: DatosCheckoutWompi, x_access_token: str = Header(None)):
    """Genera el link de pago de Wompi (PSE, Nequi, tarjetas) por 30 días de premium."""
    try:
        verificar_token(datos.usuario_id, x_access_token)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    try:
        return generar_link_pago(datos.usuario_id, datos.url_redireccion)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wompi/webhook")
async def wompi_webhook(request: Request):
    """Recibe los eventos de Wompi y activa el premium si el pago fue aprobado."""
    datos_evento = await request.json()

    try:
        return procesar_webhook_wompi(datos_evento)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Estado de suscripción (usado por ambos proveedores) ---

@router.get("/estado/{usuario_id}")
def estado_suscripcion(usuario_id: str, x_access_token: str = Header(None)):
    """Consulta si una persona tiene premium activo ahora mismo. Requiere su token de acceso."""
    try:
        verificar_token(usuario_id, x_access_token)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))

    try:
        return obtener_estado(usuario_id)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
