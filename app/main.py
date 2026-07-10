from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import carta_natal, lectura_diaria, suenos, audio, historial, compatibilidad

app = FastAPI(
    title="Oráculo Astral · API",
    description="Backend del sistema de guía espiritual diaria — Proyecto 09",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajustar a dominios reales antes de producción
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(carta_natal.router)
app.include_router(lectura_diaria.router)
app.include_router(suenos.router)
app.include_router(audio.router)
app.include_router(historial.router)
app.include_router(compatibilidad.router)


@app.get("/salud")
def salud():
    return {"estado": "ok", "servicio": "oraculo-ia-api"}
