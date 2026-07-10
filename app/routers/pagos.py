from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.services.pagos_stripe import crear_sesion_checkout, procesar_webhook as procesar_webhook_stripe
from app.services.pagos_wompi import generar_link_pago, procesar_webhook as procesar_webhook_wompi
from app.services.suscripciones import obtener_estado

router = APIRouter(prefix="/pagos", tags=["Pagos y Suscripción"])


# --- Stripe ---

class DatosCheckoutStripe(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"])
    email: str = Field(..., examples=["ana@correo.com"])
    url_exito: str = Field(..., examples=["https://tu-frontend.com/pago-exitoso"])
    url_cancelado: str = Field(..., examples=["https://tu-frontend.com/pago-cancelado"])


@router.post("/stripe/crear-sesion")
def stripe_crear_sesion(datos: DatosCheckoutStripe):
    """Crea el link de pago de Stripe para la suscripción premium mensual."""
    try:
        url = crear_sesion_checkout(
            datos.usuario_id, datos.email, datos.url_exito, datos.url_cancelado
        )
        return {"url_pago": url}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Recibe los eventos de Stripe (pago exitoso, cancelación, etc.)."""
    payload = await request.body()
    firma = request.headers.get("stripe-signature", "")

    try:
        return procesar_webhook_stripe(payload, firma)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Wompi ---

class DatosCheckoutWompi(BaseModel):
    usuario_id: str = Field(..., examples=["ana@correo.com"])
    url_redireccion: str = Field(..., examples=["https://tu-frontend.com/pago-completado"])


@router.post("/wompi/crear-link")
def wompi_crear_link(datos: DatosCheckoutWompi):
    """Genera el link de pago de Wompi (PSE, Nequi, tarjetas) por 30 días de premium."""
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
def estado_suscripcion(usuario_id: str):
    """Consulta si una persona tiene premium activo ahora mismo."""
    try:
        return obtener_estado(usuario_id)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
