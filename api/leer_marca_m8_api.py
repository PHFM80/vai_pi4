# api/leer_marca_m8_api.py
from fastapi import APIRouter, Request, HTTPException
from plc.connection import LOGOConnection
from app.config_reader import cargar_configuracion
import asyncio
'''
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
        print(f"Estado leído de {marca}: {valor}")  # <-- Esto imprime en consola
        return {"marca": marca, "valor": valor}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer la marca: {e}")

'''
from snap7.type import Areas


router = APIRouter()

@router.get("/leer-marca-pi4/")
async def leer_marca_pi4(marca: str):
    if not marca.startswith("M") or not marca[1:].isdigit():
        raise HTTPException(status_code=400, detail="Formato de marca inválido. Usa por ejemplo 'M8'")

    direccion = int(marca[1:])  # Ej: "M8" → 8

    config = cargar_configuracion()
    conexion = LOGOConnection(str(config.controlador.ip))

    try:
        await asyncio.to_thread(conexion.conectar)
        resultado = await asyncio.to_thread(conexion.client.read_area, Areas.MK, 0, direccion, 1)
        await asyncio.to_thread(conexion.desconectar)

        byte = resultado[0]
        bits = [(byte >> i) & 1 for i in range(8)]

        print(f"[DEBUG] Byte leído de {marca}: {byte:08b}")
        for i, bit in enumerate(bits):
            print(f"{marca}.{i} = {bool(bit)}")

        # Buscar actuador con esa marca_arranque
        actuadores = config.controlador.actuadores
        actuador = next((a for a in actuadores if a.marca_arranque.lower() == marca.lower()), None)

        estado_actuador = None
        nombre_actuador = None
        if actuador:
            nombre_actuador = actuador.nombre
            # Asumo que estado ON si algún bit está en 1 (true), OFF si todos 0
            estado_actuador = "ON" if any(bits) else "OFF"

        respuesta = {
            "marca": marca,
            "bits": {f"{marca}.{i}": bool(bit) for i, bit in enumerate(bits)},
        }

        if actuador:
            respuesta["nombre_actuador"] = nombre_actuador
            respuesta["estado_actuador"] = estado_actuador

        return respuesta

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer la marca: {e}")