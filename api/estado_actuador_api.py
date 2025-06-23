# api\estado_actuador_api.py

from fastapi import APIRouter, HTTPException
from datetime import datetime
from plc.connection import LOGOConnection
from app.config_reader import cargar_configuracion
from plc.marcas_utils import convertir_marca_logo_a_bytebit
from snap7.type import Areas
import asyncio

router = APIRouter()

@router.get("/estado-actuador-pi4/")
async def estado_actuador_pi4(id_actuador: int):
    # Cargar configuración
    config = cargar_configuracion()
    actuador = next((a for a in config.controlador.actuadores if a.id == id_actuador), None)

    if not actuador:
        raise HTTPException(status_code=404, detail=f"Actuador con ID {id_actuador} no encontrado")

    if not actuador.estado_plc:
        raise HTTPException(status_code=400, detail=f"El actuador con ID {id_actuador} no tiene definida una marca de estado")

    # Convertir la marca a byte y bit
    try:
        byte_dir, bit_solicitado = convertir_marca_logo_a_bytebit(actuador.estado_plc)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Conectar al PLC
    conexion = LOGOConnection(str(config.controlador.ip))
    try:
        await asyncio.to_thread(conexion.conectar)
        resultado = await asyncio.to_thread(conexion.client.read_area, Areas.MK, 0, byte_dir, 1)
        await asyncio.to_thread(conexion.desconectar)

        byte = resultado[0]
        estado_bit = (byte >> bit_solicitado) & 1

        ahora = datetime.now()
        return {
            "actuador_id": id_actuador,
            "estado": estado_bit,
            "fecha": ahora.date().isoformat(),
            "hora": ahora.time().isoformat(timespec='seconds')
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer estado del actuador: {e}")
