# main.py
import asyncio
from fastapi import FastAPI
from plc.collector_sensores import run as run_sensores
from plc.collector_actuadores import run as run_actuadores
from app.database import init_db  
from api.visualizacion_sensores_bd_api import router as sensores_router
from api.visualizacion_actuadores_bd_api import router as actuadores_router


app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("[DEBUG] Inicializando base de datos...")
    init_db()  # ← Esta línea crea las tablas si no existen
    print("[DEBUG] Lanzando collector_sensores...")
    asyncio.create_task(run_sensores())
    print("[DEBUG] Lanzando collector_actuadores...")
    asyncio.create_task(run_actuadores())

app.include_router(sensores_router)
app.include_router(actuadores_router)

@app.get("/")
async def root():
    return {"message": "FastAPI con collectors corriendo en background"}
