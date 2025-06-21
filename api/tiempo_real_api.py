# api/tiempo_real_api.py

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.config_reader import cargar_configuracion
from plc.connection import LOGOConnection
from plc.collector_sensores import leer_valor_vm_sync

router = APIRouter()

@router.get("/leer-sensor-pi4/")
async def leer_sensor_tiempo_real(sensor_id: int, request: Request):
    try:
        config = cargar_configuracion()
        sensor = next((s for s in config.controlador.sensores if s.id == sensor_id), None)

        if not sensor:
            return JSONResponse({"error": "Sensor no encontrado"}, status_code=404)

        conexion = LOGOConnection(str(config.controlador.ip))
        conexion.conectar()
        valor = leer_valor_vm_sync(conexion.client, sensor.vm)
        conexion.desconectar()

        if valor is None:
            return JSONResponse({"error": "Error al leer el valor del PLC"}, status_code=500)

        return JSONResponse({
            "sensor_id": sensor_id,
            "valor": valor
        })

    except Exception as e:
        return JSONResponse({"error": f"Excepción en la Pi: {str(e)}"}, status_code=500)
