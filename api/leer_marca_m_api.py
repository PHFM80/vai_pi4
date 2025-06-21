# api/leer_marca_m_api.py
from fastapi import APIRouter, HTTPException
from plc.connection import LOGOConnection
from app.config_reader import cargar_configuracion
from plc.marcas_utils import convertir_marca_logo_a_bytebit
import asyncio
from snap7.type import Areas
import re

router = APIRouter()

@router.get("/leer-marca-pi4/")
async def leer_marca_pi4(marca: str = "M1"):
    # Validar y convertir marca usando función externa
    try:
        byte_dir, bit_solicitado = convertir_marca_logo_a_bytebit(marca)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    config = cargar_configuracion()
    conexion = LOGOConnection(str(config.controlador.ip))

    try:
        await asyncio.to_thread(conexion.conectar)

        resultado = await asyncio.to_thread(conexion.client.read_area, Areas.MK, 0, byte_dir, 1)
        byte = resultado[0]
        bits = [(byte >> i) & 1 for i in range(8)]

        print(f"[DEBUG] Byte leído de M{byte_dir + 1}: {byte:08b}")
        for i, bit in enumerate(bits):
            print(f"M{byte_dir + 1}.{i} = {bool(bit)}")

        estado_bit = bool(bits[bit_solicitado])

        await asyncio.to_thread(conexion.desconectar)

        return {
            "marca": f"M{byte_dir + 1}.{bit_solicitado}",
            "estado_bit": estado_bit,
            "bits": {f"M{byte_dir + 1}.{i}": bool(bit) for i, bit in enumerate(bits)}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer marca: {e}")
