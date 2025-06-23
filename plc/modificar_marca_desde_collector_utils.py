# plc\modificar_marca_desde_collector_utils.py

from plc.marcas_utils import convertir_marca_logo_a_bytebit
import snap7
from plc.guardar_eventos_actuador_utils import guardar_evento_actuador

def desactivar_actuadores_de_sensor(sensor, client, config, db_session):

    """
    Desactiva las marcas de arranque de los actuadores asociados a un sensor,
    escribiendo False en su marca correspondiente.
    """
    actuadores = config.controlador.actuadores

    if not sensor.actuadores_asociados:
        return  # No hay actuadores asociados

    for act_id in sensor.actuadores_asociados:
        # Buscar el actuador por ID
        actuador = next((a for a in actuadores if a.id == act_id), None)
        if not actuador or not actuador.marca_arranque:
            continue

        try:
            byte, bit = convertir_marca_logo_a_bytebit(actuador.marca_arranque)
            client.write_area(snap7.type.Areas.MK, 0, byte, bytes([0b00000000 | ~(1 << bit) & 0xFF]))
            guardar_evento_actuador(
                db_session=db_session,
                id_actuador=actuador.id,
                accion="OFF",
                origen="plc",
                usuario=None,
                controlador=config.controlador.id)
            print(f"[ACTUADOR DESACTIVADO] Marca {actuador.marca_arranque} (actuador {act_id}) desactivada por sensor {sensor.id}")
        except Exception as e:
            print(f"[ERROR] No se pudo desactivar marca {actuador.marca_arranque} del actuador {act_id}: {e}")
