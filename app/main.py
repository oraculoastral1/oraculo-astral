import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    carta_natal, lectura_diaria, suenos, audio, historial, compatibilidad,
    pagos, auth, retorno_solar, oraculo_chat, referidos, soporte,
    recordatorios, resenas, panel,
)

app = FastAPI(
    title="Oráculo Astral · API",
    description="Backend del sistema de guía espiritual diaria — Proyecto 09",
    version="0.1.0",
)

# Los orígenes permitidos se leen de una variable de entorno (ORIGENES_PERMITIDOS,
# separados por comas). Por defecto solo se permite GitHub Pages — cuando compres
# tu dominio, agrégalo ahí (ej: "https://oraculoastral.com,https://oraculoastral1.github.io")
# en vez de dejarlo abierto a cualquier sitio del mundo.
origenes_env = os.environ.get("ORIGENES_PERMITIDOS", "").strip()
origenes_permitidos = [o.strip() for o in origenes_env.split(",") if o.strip()] or [
    "https://oraculoastral1.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(carta_natal.router)
app.include_router(lectura_diaria.router)
app.include_router(suenos.router)
app.include_router(audio.router)
app.include_router(historial.router)
app.include_router(compatibilidad.router)
app.include_router(pagos.router)
app.include_router(auth.router)
app.include_router(retorno_solar.router)
app.include_router(oraculo_chat.router)
app.include_router(referidos.router)
app.include_router(soporte.router)
app.include_router(recordatorios.router)
app.include_router(resenas.router)
app.include_router(panel.router)


@app.get("/salud")
def salud():
    return {"estado": "ok", "servicio": "oraculo-ia-api"}
