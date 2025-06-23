# plc\collector_sensores.py
import asyncio
from datetime import datetime
import requests
from sqlalchemy.orm import sessionmaker
from app.database import engine
from models.sensores import SensorLectura
from app.config_reader import cargar_configuracion
from plc.connection import LOGOConnection
from api.alerta_to_servidor_api import alerta_desde_collector
from plc.modificar_marca_desde_collector_utils import desactivar_actuadores_de_sensor
from plc.estado_actuador_utils import obtener_estado_actuador

def leer_valor_vm_sync(client, direccion_vm):
    try:
        data = client.db_read(1, direccion_vm, 2)
        valor = int.from_bytes(data, byteorder='big')
        return valor
    except Exception as e:
        print(f"[ERROR] Fallo al leer VM {direccion_vm}: {e}")
        return None

async def run():
    config = cargar_configuracion()
    sensores = config.controlador.sensores
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

    try:
        while True:
            for sensor in sensores:
                valor = await asyncio.to_thread(leer_valor_vm_sync, client, sensor.vm)
                if valor is not None:
                    ahora = datetime.now()
                    lectura = SensorLectura(
                        id_sensor=sensor.id,
                        valor=valor,
                        fecha=ahora.date(),
                        hora=ahora.time()
                    )
                    session.add(lectura)
                    await asyncio.to_thread(session.commit)
                    print(f"[{ahora.strftime('%H:%M:%S')}] Sensor {sensor.nombre}: {valor}")
                    if valor > sensor.parametro_maximo:
                        #print(f"[ALERTA] Valor fuera de rango detectado en {sensor.nombre}: {valor}")
                        alerta_desde_collector(controlador_id=config.controlador.id, sensor_id=sensor.id, valor=valor)
                    if valor < sensor.parametro_minimo:
                        for id_actuador in sensor.actuadores_asociados:
                            estado_actuador = await obtener_estado_actuador(id_actuador)
                            if estado_actuador == 1:
                                desactivar_actuadores_de_sensor(sensor, client, config, session)

            await asyncio.sleep(30)
    except asyncio.CancelledError:
        print("[INFO] Finalizando collector_sensores.")
    finally:
        await asyncio.to_thread(conexion.desconectar)
        session.close()

if __name__ == "__main__":
    asyncio.run(run())
