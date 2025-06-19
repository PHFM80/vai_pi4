# api/leer_marca_m8_api.py
from fastapi import APIRouter, Request, HTTPException
from plc.connection import LOGOConnection
from app.config_reader import cargar_configuracion
import asyncio

router = APIRouter()

@router.get("/leer-marca-pi4/")
async def leer_marca_pi4(marca: str):
    if not marca.startswith("M") or not marca[1:].isdigit():
        raise HTTPException(status_code=400, detail="Formato de marca inválido. Usa por ejemplo 'M8'")

    direccion = int(marca[1:])

    config = cargar_configuracion()
    conexion = LOGOConnection(str(config.controlador.ip))

    try:
        await asyncio.to_thread(conexion.conectar)
        valor = await asyncio.to_thread(conexion.read_bool, "M", direccion)
        await asyncio.to_thread(conexion.desconectar)

        return {"marca": marca, "valor": valor}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer la marca: {e}")
