# api/escaner_de_marcas_M.py
from fastapi import APIRouter, HTTPException
from plc.connection import LOGOConnection
from app.config_reader import cargar_configuracion
import asyncio
from snap7.type import Areas

router = APIRouter()

@router.get("/leer-marcas-pi4/")
async def leer_marcas_pi4():
    config = cargar_configuracion()
    conexion = LOGOConnection(str(config.controlador.ip))

    try:
        await asyncio.to_thread(conexion.conectar)

        todas_las_marcas = {}

        # Leer M0 a M14 (15 bytes = M0.0 a M14.7)
        for direccion in range(0, 15):
            resultado = await asyncio.to_thread(conexion.client.read_area, Areas.MK, 0, direccion, 1)
            byte = resultado[0]
            bits = [(byte >> i) & 1 for i in range(8)]

            print(f"[DEBUG] Byte leído de M{direccion}: {byte:08b}")
            for i, bit in enumerate(bits):
                nombre_bit = f"M{direccion}.{i}"
                estado = bool(bit)
                print(f"{nombre_bit} = {estado}")
                todas_las_marcas[nombre_bit] = estado

        await asyncio.to_thread(conexion.desconectar)

        return {
            "marcas": todas_las_marcas
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer marcas: {e}")

