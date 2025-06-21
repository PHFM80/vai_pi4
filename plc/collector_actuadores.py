# collector_actuadores
import asyncio
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from app.database import engine
from models.actuadores import EventoActuador
from app.config_reader import cargar_configuracion
from plc.connection import LOGOConnection
from snap7.util import get_bool
import snap7


def leer_bit_vm_sync(client, direccion_vm_bit: str) -> int | None:
    try:
        if not direccion_vm_bit.startswith("VRB"):
            return None

        byte_str, bit_str = direccion_vm_bit[3:].split(".")
        byte_index = int(byte_str)
        bit_index = int(bit_str)

        data = client.read_area(snap7.type.Areas['PE'], 0, byte_index, 1)

        valor = get_bool(data, 0, bit_index)
        print(f"[DEBUG] Byte completo leído: {data[0]:08b}")
        print(f"[DEBUG] Bit VRB{byte_index}.{bit_index} leído: {valor}")
        print(f"[DEBUG] Valor leído: {valor}")
        return int(valor)

    except Exception as e:
        print(f"[ERROR] Fallo al leer bit VM {direccion_vm_bit}: {e}")
        return None

def leer_marca_m_sync(client, direccion_m_bit: str) -> int | None:
    try:
        if not direccion_m_bit.startswith("M"):
            return None

        import re
        m = re.match(r'^M(\d+)(?:\.(\d))?$', direccion_m_bit.upper())
        if not m:
            return None

        byte_dir = int(m.group(1)) - 1
        bit_dir = int(m.group(2)) if m.group(2) else 0

        resultado = client.read_area(snap7.types.Areas.MK, 0, byte_dir, 1)
        byte_leido = resultado[0]
        estado = (byte_leido >> bit_dir) & 1

        print(f"[DEBUG] Byte leído de M{byte_dir+1}: {byte_leido:08b}")
        print(f"[DEBUG] M{byte_dir+1}.{bit_dir} = {estado}")

        return estado

    except Exception as e:
        print(f"[ERROR] Fallo al leer marca {direccion_m_bit}: {e}")
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
                if actuador.estado:
                    estado_marca = await asyncio.to_thread(leer_marca_m_sync, client, actuador.estado)
                    if estado_marca is not None:
                        print(f"[INFO] Estado de {actuador.nombre} desde marca {actuador.estado}: {estado_marca}")
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
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        print("[INFO] Finalizando collector_actuadores.")
    finally:
        await asyncio.to_thread(conexion.desconectar)
        session.close()













