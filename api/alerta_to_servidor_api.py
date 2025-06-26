# alerta_to_servidor_api.py
import requests
from datetime import datetime
import logging
from app.config_reader import cargar_configuracion

# Configurá esta URL con la IP o dominio correcto del servidor central
config = cargar_configuracion()
ip_servidor = str(config.raspberry.ip_servidor)
URL_ALERTA = f"http://{ip_servidor}:8000/dalerta-from-controlador/"


logger = logging.getLogger(__name__)

def alerta_desde_collector(controlador_id: int, sensor_id: int, valor: float):
    ahora = datetime.now()
    payload = {
        "controlador": controlador_id,
        "sensor": sensor_id,
        "fecha": ahora.strftime("%Y-%m-%d"),
        "hora": ahora.strftime("%H:%M:%S"),
        "valor": valor    }
    try:
        response = requests.post(URL_ALERTA, json=payload, timeout=5)
        if response.status_code == 201:
            logger.info("[ALERTA] Enviada correctamente al servidor")
            #print("[ALERTA] Enviada correctamente al servidor")
        else:
            logger.warning(f"[ALERTA] Error al enviar alerta: {response.status_code} - {response.text}")
            #print(f"[ALERTA] Error al enviar alerta: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"[ALERTA] Fallo en el envío de alerta: {e}")
