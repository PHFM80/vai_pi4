from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
import logging
from scheduler.envio_datos_sensores import def_envio_datos_sensores 

# Crear scheduler de fondo
scheduler = BackgroundScheduler()

# Configurar logging para errores
logger = logging.getLogger(__name__)

def iniciar_scheduler():
    minutes = 5
    scheduler.add_job(
        def_envio_datos_sensores,
        trigger=IntervalTrigger(minutes=minutes),
        id="envio_datos_sensores",
        replace_existing=True
    )
    scheduler.start()
    print("[DEBUG] Scheduler iniciado")

    # Detener el scheduler al cerrar la app
    atexit.register(lambda: scheduler.shutdown())
