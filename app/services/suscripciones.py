"""
Motor de suscripciones — Fase 8.

Guarda y consulta el estado premium de cada persona en Supabase.
Es el punto de verdad único que usan tanto Stripe como Wompi para
marcar a alguien como premium, y que el resto de la app (o un futuro
frontend) puede consultar para saber si debe dar acceso premium.
"""
import os
from datetime import datetime, timedelta, timezone
import requests


def _config_supabase() -> tuple[str, dict]:
    url_base = os.environ.get("SUPABASE_URL", "").rstrip("/")
    clave = os.environ.get("SUPABASE_SERVICE_KEY", "")

    if not url_base or not clave:
        raise RuntimeError(
            "Faltan configurar SUPABASE_URL y SUPABASE_SERVICE_KEY en las variables de entorno."
        )

    headers = {
        "apikey": clave,
        "Authorization": f"Bearer {clave}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",  # upsert: inserta o actualiza si ya existe
    }
    return f"{url_base}/rest/v1/suscripciones", headers


def registrar_pago_pendiente(usuario_id: str, referencia_pago: str, proveedor: str) -> None:
    """
    Deja una marca de "pago en camino" ANTES de mandar a la persona a pagar,
    para poder encontrarla de nuevo cuando llegue la confirmación del webhook
    (buscar por la referencia es más confiable que tratar de extraer el
    usuario_id del texto de la referencia).
    """
    url, headers = _config_supabase()

    fila = {
        "usuario_id": usuario_id,
        "plan": "gratis",
        "proveedor": proveedor,
        "estado": "pendiente",
        "referencia_pago": referencia_pago,
        "actualizado_en": datetime.now(timezone.utc).isoformat(),
    }
    respuesta = requests.post(
        url, headers=headers, params={"on_conflict": "usuario_id"}, json=fila, timeout=15
    )
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo registrar el pago pendiente: {respuesta.text}")


def buscar_usuario_por_referencia(referencia_pago: str) -> str | None:
    """Encuentra qué usuario_id corresponde a una referencia de pago dada."""
    url, headers = _config_supabase()

    respuesta = requests.get(
        url, headers=headers, params={"referencia_pago": f"eq.{referencia_pago}"}, timeout=15
    )
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo buscar la referencia de pago: {respuesta.text}")

    filas = respuesta.json()
    return filas[0]["usuario_id"] if filas else None


def activar_premium(
    usuario_id: str, proveedor: str, referencia_pago: str, dias_validez: int | None = None
) -> None:
    """
    Marca a una persona como premium. Si dias_validez se especifica (para Wompi,
    que no maneja suscripciones recurrentes automáticas), se calcula una fecha
    de vencimiento; con Stripe, el vencimiento lo controla Stripe mismo.
    """
    url, headers = _config_supabase()

    ahora = datetime.now(timezone.utc)
    fila = {
        "usuario_id": usuario_id,
        "plan": "premium",
        "proveedor": proveedor,
        "estado": "activa",
        "fecha_inicio": ahora.isoformat(),
        "fecha_fin": (ahora + timedelta(days=dias_validez)).isoformat() if dias_validez else None,
        "referencia_pago": referencia_pago,
        "actualizado_en": ahora.isoformat(),
    }

    respuesta = requests.post(
        url, headers=headers, params={"on_conflict": "usuario_id"}, json=fila, timeout=15
    )
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo activar el premium en Supabase: {respuesta.text}")


def cancelar_premium(usuario_id: str) -> None:
    """Marca la suscripción de una persona como cancelada/vencida."""
    url, headers = _config_supabase()

    respuesta = requests.patch(
        url,
        headers=headers,
        params={"usuario_id": f"eq.{usuario_id}"},
        json={"estado": "cancelada", "actualizado_en": datetime.now(timezone.utc).isoformat()},
        timeout=15,
    )
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo cancelar el premium en Supabase: {respuesta.text}")


def obtener_estado(usuario_id: str) -> dict:
    """Consulta si una persona tiene premium activo en este momento."""
    url, headers = _config_supabase()

    respuesta = requests.get(
        url, headers=headers, params={"usuario_id": f"eq.{usuario_id}"}, timeout=15
    )
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo consultar la suscripción: {respuesta.text}")

    filas = respuesta.json()
    if not filas:
        return {"usuario_id": usuario_id, "plan": "gratis", "estado": "sin_suscripcion"}

    fila = filas[0]

    # Si es un plan de Wompi con fecha de vencimiento ya pasada, se considera vencido
    if fila.get("fecha_fin"):
        fecha_fin = datetime.fromisoformat(fila["fecha_fin"])
        if fecha_fin < datetime.now(timezone.utc) and fila["estado"] == "activa":
            fila["estado"] = "vencida"

    return fila
