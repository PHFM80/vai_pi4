# plc\collector_actuadores.py

import asyncio
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from app.database import engine
from models.actuadores import EventoActuador
from app.config_reader import cargar_configuracion
from plc.connection import LOGOConnection
import snap7


def leer_bit(client, byte_dir: int, bit_dir: int) -> int | None:
    try:
        resultado = client.read_area(snap7.type.Areas.MK, 0, byte_dir, 1)
        byte_leido = resultado[0]
        estado = (byte_leido >> bit_dir) & 1

        print(f"[DEBUG] Byte leído de byte {byte_dir}: {byte_leido:08b}")
        print(f"[DEBUG] Bit {byte_dir}.{bit_dir} = {estado}")

        return estado

    except Exception as e:
        print(f"[ERROR] Fallo al leer byte {byte_dir} bit {bit_dir}: {e}")
        return None


async def run():
    config = cargar_configuracion()
    actuadores = config.controlador.actuadores
    controlador_id = config.controlador.id
    plc_ip = str(config.controlador.ip)

    conexion = LOGOConnection(plc_ip)
    try:
        await asyncio.to_thread(conexion.conectar)
        client = conexion.client
    except Exception as e:
        print(f"[ERROR] No se pudo conectar al PLC: {e}")
        return

    Session = sessionmaker(bind=engine)
    session = Session()

    #print("[INFO] Iniciando lectura de actuadores...")
    try:
        while True:
            for actuador in actuadores:
                # Leer estado (marca)
                if actuador.estado_bytebit:
                    byte_dir, bit_dir = actuador.estado_bytebit
                    estado_marca = await asyncio.to_thread(leer_bit, client, byte_dir, bit_dir)
                    if estado_marca is not None:
                        print(f"[INFO] Estado de {actuador.nombre} desde marca byte {byte_dir} bit {bit_dir}: {estado_marca}")

                # Leer marca de arranque si querés registrar también
                if actuador.marca_arranque_bytebit:
                    byte_dir, bit_dir = actuador.marca_arranque_bytebit
                    bit = await asyncio.to_thread(leer_bit, client, byte_dir, bit_dir)
                else:
                    bit = None

                if bit is not None:
                    ahora = datetime.now()
                    accion = "ON" if bit == 1 else "OFF"
                    evento = EventoActuador(
                        accion=accion,
                        fecha=ahora.date(),
                        hora=ahora.time(),
                        actuador=actuador.id,
                        origen_evento="plc",
                        usuario=None,
                        controlador=controlador_id
                    )
                    session.add(evento)
                    await asyncio.to_thread(session.commit)
                    print(f"[{ahora.strftime('%H:%M:%S')}] Actuador {actuador.nombre} (id:{actuador.id}): {accion}")

            await asyncio.sleep(30)
    except asyncio.CancelledError:
        print("[INFO] Finalizando collector_actuadores.")
    finally:
        await asyncio.to_thread(conexion.desconectar)
        session.close()

