# D:\vai_pi4\api\accionar_actuador_pi4_api.py
from fastapi import APIRouter, Request, HTTPException
from plc.connection import LOGOConnection
from app.config_reader import cargar_configuracion
from datetime import datetime
import asyncio
from app.database import SessionLocal
from models.actuadores import EventoActuador
from snap7.type import Areas

def guardar_evento_actuador(db_session, id_actuador, accion, id_usuario):
    ahora = datetime.now()
    evento = EventoActuador(
        accion='ON' if accion == 'activar' else 'OFF',
        fecha=ahora.date(),
        hora=ahora.time(),
        actuador=id_actuador,
        origen_evento='usuario',
        usuario=id_usuario,
        controlador=None,
    )
    db_session.add(evento)
    db_session.commit()

router = APIRouter()

@router.post("/accionar-actuador-pi4/")
async def accionar_desde_api(request: Request):
    datos = await request.json()
    id_actuador = datos.get("id_actuador")
    accion = datos.get("accion")
    id_usuario = datos.get("id_usuario")

    if accion not in ["activar", "desactivar"]:
        raise HTTPException(status_code=400, detail="Acción inválida")
    if not id_usuario:
        raise HTTPException(status_code=400, detail="Falta id_usuario")

    config = cargar_configuracion()
    actuadores = config.controlador.actuadores
    actuador = next((a for a in actuadores if a.id == id_actuador), None)

    if not actuador:
        raise HTTPException(status_code=404, detail="Actuador no encontrado")

    import re
    m = re.match(r'^M(\d+)(?:\.(\d))?$', actuador.marca_arranque.upper())
    if not m:
        raise HTTPException(status_code=400, detail="Formato de marca inválido en actuador")

    byte_dir = int(m.group(1)) - 1
    bit_dir = int(m.group(2)) if m.group(2) else 0
    valor = accion == "activar"

    conexion = LOGOConnection(str(config.controlador.ip))

    try:
        await asyncio.to_thread(conexion.conectar)
        await asyncio.to_thread(conexion.write_bool, "M", byte_dir, valor, bit=bit_dir)
        await asyncio.to_thread(conexion.desconectar)

        session = SessionLocal()
        guardar_evento_actuador(session, id_actuador, accion, id_usuario)
        session.close()

        ahora = datetime.now()
        return {
            "estado": "ON" if valor else "OFF",
            "fecha": ahora.date().isoformat(),
            "hora": ahora.time().strftime("%H:%M:%S"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al accionar actuador: {e}")
