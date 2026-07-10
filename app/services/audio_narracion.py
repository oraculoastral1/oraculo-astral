"""
Motor de narración de audio — Fase 5.

Convierte el texto de una lectura (diaria o de sueños) en audio narrado,
usando ElevenLabs. Empezamos en su nivel gratis (10,000 caracteres/mes,
sin tarjeta) — apto para pruebas. Antes de cobrar suscripciones reales,
hay que subir al plan Starter ($6/mes) para tener licencia comercial.
"""
import os
import requests

ELEVENLABS_URL_BASE = "https://api.elevenlabs.io/v1/text-to-speech"

# "Rachel" — voz multilingüe de ElevenLabs, incluida en la biblioteca gratis.
# Es una voz genérica de muestra; en la Fase 6/7 conviene elegir o clonar
# una voz más alineada con la identidad de marca de Oráculo Astral.
VOZ_ID_POR_DEFECTO = "21m00Tcm4TlvDq8ikWAM"


def narrar_texto(texto: str, voz_id: str = VOZ_ID_POR_DEFECTO) -> bytes:
    """
    Convierte texto en audio (formato mp3) usando ElevenLabs.
    Requiere la variable de entorno ELEVENLABS_API_KEY (gratis en elevenlabs.io).
    Devuelve los bytes crudos del archivo mp3.
    """
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Falta configurar ELEVENLABS_API_KEY en las variables de entorno del servidor."
        )

    if len(texto) > 9000:
        # margen de seguridad bajo el límite gratis de 10,000 caracteres/mes
        texto = texto[:9000]

    respuesta = requests.post(
        f"{ELEVENLABS_URL_BASE}/{voz_id}",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "text": texto,
            "model_id": "eleven_multilingual_v2",  # necesario para que narre bien en español
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        },
        timeout=60,
    )
    respuesta.raise_for_status()
    return respuesta.content
