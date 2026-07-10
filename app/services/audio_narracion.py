"""
Motor de narración de audio — Fase 5 (v2).

Usa edge-tts: el motor de voz del "Leer en voz alta" de Microsoft Edge,
accesible sin cuenta, sin tarjeta y sin clave de API. A diferencia de
ElevenLabs, sí funciona llamándolo desde un servidor (no lo bloquea
como posible VPN).

Nota honesta: es una librería no oficial que reutiliza un servicio de
Microsoft no pensado originalmente para este uso. Lleva años estable,
pero conviene saber que no tiene garantía formal de soporte.
"""
import asyncio
import edge_tts

# Voz en español neutro/colombiano, cálida y natural.
# Alternativas: "es-MX-DaliaNeural" (mexicana), "es-US-PalomaNeural" (latina neutra)
VOZ_POR_DEFECTO = "es-CO-SalomeNeural"


def narrar_texto(texto: str, voz: str = VOZ_POR_DEFECTO) -> bytes:
    """
    Convierte texto en audio (mp3) usando edge-tts.
    No requiere ninguna clave ni variable de entorno.
    """

    async def _generar() -> bytes:
        comunicacion = edge_tts.Communicate(texto, voz)
        fragmentos = bytearray()
        async for fragmento in comunicacion.stream():
            if fragmento["type"] == "audio":
                fragmentos.extend(fragmento["data"])
        return bytes(fragmentos)

    return asyncio.run(_generar())
