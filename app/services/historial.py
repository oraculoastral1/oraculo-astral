"""
Motor de historial y patrones — Fase 6.

Guarda cada lectura diaria generada en Supabase (Postgres gratis) y
permite consultar el historial completo de una persona, además de
calcular patrones simples: qué cartas de tarot le salen más seguido,
qué aspectos se repiten, cuántas lecturas ha recibido en total.

Usa la API REST de Supabase (PostgREST) directamente por HTTP —
no requiere librerías extra de base de datos.
"""
import os
from collections import Counter
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
    }
    return f"{url_base}/rest/v1/lecturas", headers


def guardar_lectura(
    usuario_id: str,
    fecha_nacimiento: str,
    ciudad: str,
    carta_natal: dict,
    numerologia: dict,
    tarot: dict,
    lectura_texto: str,
) -> None:
    """Guarda una lectura generada en el historial de la persona."""
    url, headers = _config_supabase()

    fila = {
        "usuario_id": usuario_id,
        "fecha_nacimiento": fecha_nacimiento,
        "ciudad": ciudad,
        "sol_signo": carta_natal["planetas"]["Sol"]["signo"],
        "luna_signo": carta_natal["planetas"]["Luna"]["signo"],
        "ascendente_signo": carta_natal["ascendente"]["signo"],
        "numerologia_numero": numerologia["numero"],
        "tarot_carta": tarot["carta"],
        "tarot_orientacion": tarot["orientacion"],
        "lectura_texto": lectura_texto,
    }

    respuesta = requests.post(url, headers=headers, json=fila, timeout=15)
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo guardar la lectura en Supabase: {respuesta.text}")


def obtener_historial(usuario_id: str, limite: int = 30) -> list[dict]:
    """Devuelve las últimas lecturas de una persona, de la más reciente a la más antigua."""
    url, headers = _config_supabase()

    parametros = {
        "usuario_id": f"eq.{usuario_id}",
        "order": "fecha_lectura.desc",
        "limit": str(limite),
    }
    respuesta = requests.get(url, headers=headers, params=parametros, timeout=15)
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo consultar el historial: {respuesta.text}")

    return respuesta.json()


def calcular_patrones(usuario_id: str) -> dict:
    """
    Analiza el historial completo de una persona para detectar patrones:
    cartas de tarot repetidas, signos lunares/solares dominantes, y
    el número de numerología (que siempre es el mismo, se confirma).
    """
    historial = obtener_historial(usuario_id, limite=365)

    if not historial:
        return {
            "total_lecturas": 0,
            "mensaje": "Todavía no hay lecturas guardadas para esta persona.",
        }

    cartas = Counter(fila["tarot_carta"] for fila in historial)
    orientaciones = Counter(fila["tarot_orientacion"] for fila in historial)

    return {
        "total_lecturas": len(historial),
        "primera_lectura": historial[-1]["fecha_lectura"],
        "ultima_lectura": historial[0]["fecha_lectura"],
        "numerologia_numero": historial[0]["numerologia_numero"],
        "carta_mas_frecuente": cartas.most_common(1)[0][0] if cartas else None,
        "top_3_cartas": [{"carta": c, "veces": n} for c, n in cartas.most_common(3)],
        "proporcion_reversas": round(
            orientaciones.get("revertida", 0) / len(historial), 2
        ),
    }
