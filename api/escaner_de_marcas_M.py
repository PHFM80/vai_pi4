# api/leer_marca_m8_api.py
from fastapi import APIRouter, Request, HTTPException
from plc.connection import LOGOConnection
from app.config_reader import cargar_configuracion
import asyncio
from snap7.type import Areas

router = APIRouter()
@router.get("/leer-marcas-pi4/")
async def leer_marcas_pi4(id_actuador: int = None):
    config = cargar_configuracion()
    conexion = LOGOConnection(str(config.controlador.ip))

    try:
        await asyncio.to_thread(conexion.conectar)

        todas_las_marcas = {}

        # Leer M1 a M7
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

        # Leer estado del actuador si se especificó
        estado_actuador = None
        nombre_actuador = None
        if id_actuador is not None:
            actuadores = config.controlador.actuadores
            actuador = next((a for a in actuadores if a.id == id_actuador), None)

            if actuador:
                nombre_actuador = actuador.nombre
                vrb_str = actuador.nq_estado  # Ej: "VRB0.7"
                if vrb_str.startswith("VRB"):
                    partes = vrb_str[3:].split(".")
                    byte_vrb = int(partes[0])
                    bit_vrb = int(partes[1])
                    resultado_vrb = await asyncio.to_thread(conexion.client.read_area, Areas.PE, 0, byte_vrb, 1)
                    byte_leido = resultado_vrb[0]
                    estado_actuador = bool((byte_leido >> bit_vrb) & 1)
                    print(f"[DEBUG] Estado leído de {vrb_str} ({nombre_actuador}): {estado_actuador}")
                else:
                    print(f"[WARN] nq_estado no válido: {vrb_str}")

        await asyncio.to_thread(conexion.desconectar)

        return {
            "marcas": todas_las_marcas,
            "estado_actuador": estado_actuador,
            "nombre_actuador": nombre_actuador
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer marcas: {e}")
