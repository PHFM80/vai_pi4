# main.py
import asyncio
from fastapi import FastAPI
from plc.collector_sensores import run as run_sensores
from plc.collector_actuadores import run as run_actuadores

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_sensores())
    asyncio.create_task(run_actuadores())

@app.get("/")
async def root():
    return {"message": "FastAPI con collectors corriendo en background"}
