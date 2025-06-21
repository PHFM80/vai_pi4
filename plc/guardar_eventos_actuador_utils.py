# plc\guardar_eventos_actuador_utils.py

from datetime import datetime
from models.actuadores import EventoActuador
from models.actuadores import UltimoEstadoPLC

def guardar_evento_actuador(db_session, id_actuador: int, accion: str, origen: str, usuario: int = None, controlador: int = None):
    ahora = datetime.now()
    evento = EventoActuador(
        accion=accion,
        fecha=ahora.date(),
        hora=ahora.time(),
        actuador=id_actuador,
        origen_evento=origen,
        usuario=usuario,
        controlador=controlador,
    )
    db_session.add(evento)
    db_session.commit()
    print(f"[EVENTO GUARDADO] Actuador {id_actuador} - Evento: {evento}")



def comparar_estado_plc(db_session, id_actuador: int, nuevo_estado: str) -> bool:
    """
    Verifica si el nuevo estado es diferente al último guardado.
    Retorna True si cambió, False si es igual o no hay registro.
    """
    registro = db_session.query(UltimoEstadoPLC).filter_by(actuador=id_actuador).first()
    if registro is None:
        # No hay registro previo, asumimos que cambió para guardar por primera vez
        return True
    return registro.estado != nuevo_estado


def actualizar_estado_plc(db_session, id_actuador: int, nuevo_estado: str):
    """
    Actualiza o crea el registro del último estado PLC para el actuador.
    """
    ahora = datetime.now()
    registro = db_session.query(UltimoEstadoPLC).filter_by(actuador=id_actuador).first()

    if registro is None:
        registro = UltimoEstadoPLC(
            actuador=id_actuador,
            estado=nuevo_estado,
            actualizado=ahora
        )
        db_session.add(registro)
    else:
        registro.estado = nuevo_estado
        registro.actualizado = ahora

    db_session.commit()
