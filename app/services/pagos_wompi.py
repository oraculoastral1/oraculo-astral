"""
Motor de pagos con Wompi — Fase 8 (v2 con plan anual).

Nota honesta sobre el alcance: Wompi, a diferencia de Stripe, no maneja
"suscripciones recurrentes" automáticas de forma sencilla — su fortaleza
son los pagos únicos (tarjeta, PSE, Nequi). Por eso aquí implementamos un
pago único que da premium por un número fijo de días (30 para el plan
mensual, 365 para el anual), renovable manualmente por la persona. Es una
solución honesta para el volumen actual del proyecto; una automatización
completa de cobro recurrente con Wompi requiere su API de "Suscripciones"
con tokenización de tarjeta, un paso más avanzado para cuando crezca.
"""
import os
import hashlib
import uuid

from app.services.suscripciones import (
    activar_premium,
    registrar_pago_pendiente,
    buscar_pago_por_referencia,
)

WOMPI_CHECKOUT_URL = "https://checkout.wompi.co/p/"

PLANES = {
    "mensual": {"dias": 30, "variable_entorno": "WOMPI_MONTO_COP"},
    "anual": {"dias": 365, "variable_entorno": "WOMPI_MONTO_COP_ANUAL"},
}


def generar_link_pago(usuario_id: str, url_redireccion: str, plan: str = "mensual") -> dict:
    """
    Genera el enlace de pago de Wompi (Web Checkout) al que se redirige
    a la persona para pagar. Wompi solo acepta pesos colombianos (COP).
    plan puede ser "mensual" (30 días) o "anual" (365 días, con descuento).
    """
    if plan not in PLANES:
        raise RuntimeError(f"Plan desconocido: {plan}. Debe ser 'mensual' o 'anual'.")

    llave_publica = os.environ.get("WOMPI_PUBLIC_KEY", "").strip()
    secreto_integridad = os.environ.get("WOMPI_INTEGRITY_SECRET", "").strip()
    monto_cop = os.environ.get(PLANES[plan]["variable_entorno"], "").strip()
    dias_validez = PLANES[plan]["dias"]

    if not llave_publica or not secreto_integridad or not monto_cop:
        raise RuntimeError(
            f"Faltan configurar WOMPI_PUBLIC_KEY, WOMPI_INTEGRITY_SECRET y "
            f"{PLANES[plan]['variable_entorno']} en las variables de entorno."
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

    registrar_pago_pendiente(usuario_id, referencia, proveedor="wompi", dias_plan=dias_validez)

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
    aprobado, activa el premium por los días que correspondan al plan
    que esa persona eligió pagar (30 días mensual, 365 anual).
    """
    secreto_eventos = os.environ.get("WOMPI_EVENTS_SECRET", "").strip()
    if not secreto_eventos:
        raise RuntimeError("Falta configurar WOMPI_EVENTS_SECRET en las variables de entorno.")

    if not _verificar_checksum(datos_evento, secreto_eventos):
        raise RuntimeError("La firma del evento de Wompi no es válida — posible suplantación.")

    transaccion = datos_evento["data"]["transaction"]
    if transaccion["status"] == "APPROVED":
        pago = buscar_pago_por_referencia(transaccion["reference"])
        if pago:
            activar_premium(
                pago["usuario_id"],
                proveedor="wompi",
                referencia_pago=transaccion["id"],
                dias_validez=pago["dias_plan"],
            )

    return {"estado_transaccion": transaccion["status"], "procesado": True}
