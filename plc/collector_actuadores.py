# collector_actuadores
import asyncio
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from app.database import engine
from models.actuadores import EventoActuador
from app.config_reader import cargar_configuracion
from plc.connection import LOGOConnection

def leer_bit_vm_sync(client, direccion_vm_bit: str) -> int | None:
    try:
        if not (direccion_vm_bit.startswith("VB")or direccion_vm_bit.startswith("VRB")):
            print(f"[ERROR] Dirección VM inválida: {direccion_vm_bit}")
            return None
        byte_str, bit_str = direccion_vm_bit[2:].split(".")
        byte_index = int(byte_str)
        bit_index = int(bit_str)

        data = client.db_read(1, byte_index, 1)
        byte_val = data[0]
        bit_val = (byte_val >> bit_index) & 1
        return bit_val
    except Exception as e:
        print(f"[ERROR] Fallo al leer bit VM {direccion_vm_bit}: {e}")
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

    print("[INFO] Iniciando lectura de actuadores...")
    try:
        while True:
            for actuador in actuadores:
                bit = await asyncio.to_thread(leer_bit_vm_sync, client, actuador.nq_estado)
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
            await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("[INFO] Finalizando collector_actuadores.")
    finally:
        await asyncio.to_thread(conexion.desconectar)
        session.close()
