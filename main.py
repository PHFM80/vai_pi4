# main.py
import asyncio
from fastapi import FastAPI
from plc.collector_sensores import run as run_sensores
from plc.collector_actuadores import run as run_actuadores
from app.database import init_db  
from api.visualizacion_sensores_bd_api import router as sensores_router
from api.visualizacion_actuadores_bd_api import router as actuadores_router
from scheduler.scheduler import iniciar_scheduler  
from api.tiempo_real_api import router as tiempo_real_router
from api.accionar_actuador_pi4_api import router as actuador_router
from api.leer_marca_m_api import router as marca_router



app = FastAPI()

@app.on_event("startup")
async def startup_event():
    init_db()  
    asyncio.create_task(run_sensores())
    asyncio.create_task(run_actuadores())
    #iniciar_scheduler()  

app.include_router(sensores_router)
app.include_router(actuadores_router)
app.include_router(tiempo_real_router)
app.include_router(actuador_router)
app.include_router(marca_router)

@app.get("/")
async def root():
    return {"message": "FastAPI con collectors corriendo en background"}
