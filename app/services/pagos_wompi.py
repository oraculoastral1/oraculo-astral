"""
Motor de pagos con Wompi — Fase 8.

Nota honesta sobre el alcance: Wompi, a diferencia de Stripe, no maneja
"suscripciones recurrentes" automáticas de forma sencilla — su fortaleza
son los pagos únicos (tarjeta, PSE, Nequi). Por eso aquí implementamos un
pago único que da 30 días de premium, renovable manualmente cada mes por
la persona. Es una solución honesta para el volumen actual del proyecto;
una automatización completa de cobro recurrente con Wompi requiere su API
de "Suscripciones" con tokenización de tarjeta, que es un paso más
avanzado para cuando el proyecto crezca.
"""
import os
import hashlib
import uuid

from app.services.suscripciones import (
    activar_premium,
    registrar_pago_pendiente,
    buscar_usuario_por_referencia,
)

WOMPI_CHECKOUT_URL = "https://checkout.wompi.co/p/"
DIAS_DE_PREMIUM_POR_PAGO = 30


def generar_link_pago(usuario_id: str, url_redireccion: str) -> dict:
    """
    Genera el enlace de pago de Wompi (Web Checkout) al que se redirige
    a la persona para pagar. Wompi solo acepta pesos colombianos (COP).
    """
    llave_publica = os.environ.get("WOMPI_PUBLIC_KEY", "").strip()
    secreto_integridad = os.environ.get("WOMPI_INTEGRITY_SECRET", "").strip()
    monto_cop = os.environ.get("WOMPI_MONTO_COP", "").strip()

    if not llave_publica or not secreto_integridad or not monto_cop:
        raise RuntimeError(
            "Faltan configurar WOMPI_PUBLIC_KEY, WOMPI_INTEGRITY_SECRET y WOMPI_MONTO_COP "
            "en las variables de entorno. WOMPI_MONTO_COP es el precio en pesos colombianos "
            "equivalente a $14.99 USD — ajústalo según la tasa de cambio actual."
        )

    monto_en_centavos = str(int(monto_cop) * 100)  # Wompi pide el monto en centavos de peso
    referencia = f"oraculo-astral-{usuario_id}-{uuid.uuid4().hex[:8]}"

    # Fórmula exacta exigida por Wompi (el orden importa, sin separadores):
    # referencia + monto_en_centavos + moneda + secreto_integridad
    cadena = f"{referencia}{monto_en_centavos}COP{secreto_integridad}"
    firma = hashlib.sha256(cadena.encode("utf-8")).hexdigest()

    parametros = (
        f"?public-key={llave_publica}"
        f"&currency=COP"
        f"&amount-in-cents={monto_en_centavos}"
        f"&reference={referencia}"
        f"&signature:integrity={firma}"
        f"&redirect-url={url_redireccion}"
    )

    registrar_pago_pendiente(usuario_id, referencia, proveedor="wompi")

    return {"url_pago": WOMPI_CHECKOUT_URL + parametros, "referencia": referencia}


def _verificar_checksum(datos_evento: dict, secreto_eventos: str) -> bool:
    """Reconstruye el checksum del evento y lo compara con el que envió Wompi."""
    propiedades = datos_evento["signature"]["properties"]
    timestamp = datos_evento["timestamp"]

    valores = []
    for ruta in propiedades:
        nodo = datos_evento["data"]
        for parte in ruta.split("."):
            nodo = nodo[parte]
        valores.append(str(nodo))

    cadena = "".join(valores) + str(timestamp) + secreto_eventos
    checksum_calculado = hashlib.sha256(cadena.encode("utf-8")).hexdigest()

    return checksum_calculado.lower() == datos_evento["signature"]["checksum"].lower()


def procesar_webhook(datos_evento: dict) -> dict:
    """
    Verifica que el evento venga realmente de Wompi, y si el pago fue
    aprobado, activa 30 días de premium para la persona.
    """
    secreto_eventos = os.environ.get("WOMPI_EVENTS_SECRET", "").strip()
    if not secreto_eventos:
        raise RuntimeError("Falta configurar WOMPI_EVENTS_SECRET en las variables de entorno.")

    if not _verificar_checksum(datos_evento, secreto_eventos):
        raise RuntimeError("La firma del evento de Wompi no es válida — posible suplantación.")

    transaccion = datos_evento["data"]["transaction"]
    if transaccion["status"] == "APPROVED":
        usuario_id = buscar_usuario_por_referencia(transaccion["reference"])
        if usuario_id:
            activar_premium(
                usuario_id,
                proveedor="wompi",
                referencia_pago=transaccion["id"],
                dias_validez=DIAS_DE_PREMIUM_POR_PAGO,
            )

    return {"estado_transaccion": transaccion["status"], "procesado": True}
