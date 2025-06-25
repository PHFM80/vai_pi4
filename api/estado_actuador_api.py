from fastapi import APIRouter, HTTPException
from datetime import datetime
from plc.estado_actuador_utils import obtener_estado_actuador

router = APIRouter()

@router.get("/estado-actuador-pi4/")
async def estado_actuador_pi4(id_actuador: int):
    try:
        estado_num = await obtener_estado_actuador(id_actuador)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    estado_str = "ON" if estado_num == 1 else "OFF"

    ahora = datetime.now()
    fecha_str = ahora.strftime("%d/%m/%Y")
    hora_str = ahora.strftime("%H:%M:%S")

    return {
        "actuador_id": id_actuador,
        "estado": estado_str,
        "fecha": fecha_str,
        "hora": hora_str
    }
