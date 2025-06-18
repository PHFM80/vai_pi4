# scheduler/envio_eventos_actuadores.py

from sqlalchemy.orm import Session
from models.actuadores import EventoActuador
import requests
import time
import logging
from app.database import SessionLocal

# URL del servidor central (ajustar IP si es necesario)
URL_SERVIDOR = "http://192.168.1.33:8000/evento-actuador-create/"

logger = logging.getLogger(__name__)

def obtener_eventos_no_enviados(db: Session):
    eventos = db.query(EventoActuador).all()

    payload = {"eventos": {}}
    ids_a_borrar = []

    for evento in eventos:
        id_actuador = evento.actuador
        if id_actuador not in payload["eventos"]:
            payload["eventos"][id_actuador] = []

        payload["eventos"][id_actuador].append({
            "accion": evento.accion,
            "fecha": evento.fecha.isoformat(),
            "hora": evento.hora.isoformat()
        })

        ids_a_borrar.append(evento.id)
    print(f"[DEBUG] Eventos a enviar desde  obtener eventeos: {payload}")
    print(f"[DEBUG] IDs a borrar desde obtener eventos: {ids_a_borrar}")
    return payload, ids_a_borrar


def def_envio_eventos_actuadores():
    logger.info("🚀 Iniciando envío de eventos de actuadores al servidor...")
    session: Session = SessionLocal()

    try:
        payload, ids_a_borrar = obtener_eventos_no_enviados(session)

        if not payload["eventos"]:
            logger.info("No hay eventos nuevos para enviar.")
            print("[DEBUG] No hay eventos nuevos para enviar.")
            return

        intentos = 0
        max_intentos = 3
        exito = False

        while intentos < max_intentos and not exito:
            try:
                response = requests.post(URL_SERVIDOR, json=payload, timeout=10)
                if response.status_code == 200:
                    print(f"[DEBUG] Respuesta del servidor: {response.json()}")
                    logger.info(f"✅ Eventos enviados correctamente. Respuesta del servidor: {response.json()}")

                    session.query(EventoActuador).filter(EventoActuador.id.in_(ids_a_borrar)).delete(synchronize_session=False)
                    session.commit()
                    logger.info(f"🗑️ Eliminados {len(ids_a_borrar)} eventos locales.")
                    print(f"[DEBUG] Se eliminaron {len(ids_a_borrar)} eventos locales.")
                    exito = True
                else:
                    logger.warning(f"⚠️ Error al enviar eventos. Código: {response.status_code}. Respuesta: {response.text}")
            except requests.RequestException as e:
                logger.error(f"🌐 Fallo en la conexión: {e}")
                time.sleep(5)
            intentos += 1

        if not exito:
            logger.error("❌ No se logró enviar los eventos luego de 3 intentos.")
            print("[DEBUG] No se logró enviar los eventos luego de 3 intentos.")


    finally:
        session.close()
