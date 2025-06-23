# plc\estado_actuador_utils.py


from datetime import datetime
from plc.connection import LOGOConnection
from app.config_reader import cargar_configuracion
from plc.marcas_utils import convertir_marca_logo_a_bytebit
from snap7.type import Areas
import asyncio

async def obtener_estado_actuador(id_actuador: int) -> int:
    config = cargar_configuracion()
    actuador = next((a for a in config.controlador.actuadores if a.id == id_actuador), None)

    if not actuador:
        raise ValueError(f"Actuador con ID {id_actuador} no encontrado")

    if not actuador.estado_plc:
        raise ValueError(f"Actuador con ID {id_actuador} no tiene definida una marca de estado")

    try:
        byte_dir, bit_solicitado = convertir_marca_logo_a_bytebit(actuador.estado)
    except ValueError as e:
        raise ValueError(f"Error al convertir marca: {e}")

    conexion = LOGOConnection(str(config.controlador.ip))
    try:
        await asyncio.to_thread(conexion.conectar)
        resultado = await asyncio.to_thread(conexion.client.read_area, Areas.MK, 0, byte_dir, 1)
        await asyncio.to_thread(conexion.desconectar)

        print(f"[DEBUG] Leyendo estado de actuador {id_actuador}, marca PLC: {actuador.estado}")
        print(f"[DEBUG] byte_dir: {byte_dir}, bit_solicitado: {bit_solicitado}")
        print(f"[DEBUG] Resultado raw byte leído: {resultado}")

        byte = resultado[0]
        estado_bit = (byte >> bit_solicitado) & 1

        print(f"[DEBUG] Estado bit calculado: {estado_bit}")

        return estado_bit

    except Exception as e:
        raise RuntimeError(f"Error al leer estado del actuador: {e}")
