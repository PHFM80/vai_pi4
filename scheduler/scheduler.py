from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
import logging
from scheduler.envio_datos_sensores import def_envio_datos_sensores
from scheduler.envio_eventos_actuadores import def_envio_eventos_actuadores 
from app.config_reader import cargar_configuracion

scheduler = BackgroundScheduler()
logger = logging.getLogger(__name__)

def iniciar_scheduler():
    config = cargar_configuracion()
    intervalo_sensores = config.intervalos.intervalo_schedulerS
    intervalo_actuadores = config.intervalos.intervalo_schedulerA

    scheduler.add_job(
        def_envio_datos_sensores,
        trigger=IntervalTrigger(seconds=intervalo_sensores),
        id="envio_datos_sensores",
        replace_existing=True
    )

    scheduler.add_job( 
        def_envio_eventos_actuadores,
        trigger=IntervalTrigger(seconds=intervalo_actuadores),
        id="envio_eventos_actuadores",
        replace_existing=True
    )

    scheduler.start()
    #print("[DEBUG] Scheduler iniciado")

    atexit.register(lambda: scheduler.shutdown())
