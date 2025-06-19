# api/leer_marca_m8_api.py
from fastapi import APIRouter, Request, HTTPException
from plc.connection import LOGOConnection
from app.config_reader import cargar_configuracion
import asyncio
from snap7.type import Areas

router = APIRouter()
@router.get("/leer-marcas-pi4/")
async def leer_marcas_pi4(marca: str = "M1", id_actuador: int = None):
    # Validar formato básico marca: puede ser "M1" o "M1.3"
    import re
    m = re.match(r'^M(\d+)(?:\.(\d))?$', marca.upper())
    if not m:
        raise HTTPException(status_code=400, detail="Formato de marca inválido. Ej: 'M1' o 'M1.3'")
    
    num = int(m.group(1))
    bit_solicitado = int(m.group(2)) if m.group(2) else 0

    # Mapear M1 → byte 0, M2 → byte 1, etc (M1 es M0.0)
    byte_dir = num - 1  # porque M1 es byte 0

    config = cargar_configuracion()
    conexion = LOGOConnection(str(config.controlador.ip))

    try:
        await asyncio.to_thread(conexion.conectar)

        # Leer byte completo
        resultado = await asyncio.to_thread(conexion.client.read_area, Areas.MK, 0, byte_dir, 1)
        byte = resultado[0]
        bits = [(byte >> i) & 1 for i in range(8)]

        print(f"[DEBUG] Byte leído de M{byte_dir}: {byte:08b}")
        for i, bit in enumerate(bits):
            print(f"M{byte_dir + 1}.{i} = {bool(bit)}")  # Mostrar como M1.0, M1.1 ...

        # Estado específico del bit solicitado
        estado_bit = bool(bits[bit_solicitado])

        # Leer estado del actuador si se especificó
        estado_actuador = None
        nombre_actuador = None
        if id_actuador is not None:
            actuadores = config.controlador.actuadores
            actuador = next((a for a in actuadores if a.id == id_actuador), None)

            if actuador:
                nombre_actuador = actuador.nombre
                vrb_str = actuador.nq_estado  # Ej: "VRB0.7"
                if vrb_str.startswith("VRB"):
                    partes = vrb_str[3:].split(".")
                    byte_vrb = int(partes[0])
                    bit_vrb = int(partes[1])
                    resultado_vrb = await asyncio.to_thread(conexion.client.read_area, Areas.PE, 0, byte_vrb, 1)
                    byte_leido = resultado_vrb[0]
                    estado_actuador = bool((byte_leido >> bit_vrb) & 1)
                    print(f"[DEBUG] Estado leído de {vrb_str} ({nombre_actuador}): {estado_actuador}")
                else:
                    print(f"[WARN] nq_estado no válido: {vrb_str}")

        await asyncio.to_thread(conexion.desconectar)

        return {
            "marca": f"M{num}.{bit_solicitado}",
            "estado_bit": estado_bit,
            "bits": {f"M{num}.{i}": bool(bit) for i, bit in enumerate(bits)},
            "estado_actuador": estado_actuador,
            "nombre_actuador": nombre_actuador
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer marcas: {e}")
