from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
import logging

from scheduler.envio_datos_sensores import def_envio_datos_sensores
from scheduler.envio_eventos_actuadores import def_envio_eventos_actuadores  # NUEVO

scheduler = BackgroundScheduler()
logger = logging.getLogger(__name__)

def iniciar_scheduler():
    minutes = 3

    scheduler.add_job(
        def_envio_datos_sensores,
        trigger=IntervalTrigger(minutes=minutes),
        id="envio_datos_sensores",
        replace_existing=True
    )

    scheduler.add_job(  # NUEVO
        def_envio_eventos_actuadores,
        trigger=IntervalTrigger(minutes=minutes),
        id="envio_eventos_actuadores",
        replace_existing=True
    )

    scheduler.start()
    print("[DEBUG] Scheduler iniciado")

    atexit.register(lambda: scheduler.shutdown())
