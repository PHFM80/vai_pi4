# scheduler/envio_datos_sensores.py

from sqlalchemy.orm import Session
from models.sensores import SensorLectura
import requests
import time
import logging
from app.database import SessionLocal


def obtener_lecturas_sin_enviar(db: Session):
    lecturas = db.query(SensorLectura).all()
    payload = {}
    ids_a_borrar = []

    for lectura in lecturas:
        sensor_id = lectura.id_sensor
        if sensor_id not in payload:
            payload[sensor_id] = []

        payload[sensor_id].append({
            "valor": lectura.valor,
            "fecha": lectura.fecha.isoformat(),
            "hora": lectura.hora.isoformat()
        })

        ids_a_borrar.append(lectura.id)
    return payload, ids_a_borrar


# URL del servidor central (modo desarrollo: notebook)
URL_SERVIDOR = "http://192.168.1.33:8000/datos-sensor-create/"  # Reemplazar IP si cambia

logger = logging.getLogger(__name__)

def def_envio_datos_sensores():
    logger.info("⏳ Iniciando envío de datos de sensores al servidor...")
    session: Session = SessionLocal()

    try:
        payload, ids_a_borrar = obtener_lecturas_sin_enviar(session)
        if not payload:
            logger.info("No hay datos nuevos para enviar.")
            return

        intentos = 0
        max_intentos = 3
        exito = False

        while intentos < max_intentos and not exito:
            try:
                response = requests.post(URL_SERVIDOR, json=payload, timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ Datos enviados correctamente. Respuesta recibida del servidor: {response.json()}")

                    # Eliminar lecturas enviadas
                    session.query(SensorLectura).filter(SensorLectura.id.in_(ids_a_borrar)).delete(synchronize_session=False)
                    session.commit()
                    logger.info(f"🗑️ Eliminadas {len(ids_a_borrar)} lecturas locales.")
                    exito = True

                else:
                    logger.warning(f"⚠️ Error al enviar datos. Código: {response.status_code}. Respuesta recibida del servidor: {response.text}")
            except requests.RequestException as e:
                logger.error(f"🌐 Fallo en la conexión: {e}")
                time.sleep(5)  # espera antes de reintentar
            intentos += 1

        if not exito:
            logger.error("No se logró enviar los datos luego de 3 intentos.")

    finally:
        session.close()
