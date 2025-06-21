# app/config_reader.py
from pydantic import BaseModel, Field, IPvAnyAddress
from typing import List, Optional
import yaml
import os
from plc.marcas_utils import convertir_marca_logo_a_bytebit


class Sensor(BaseModel):
    id: int
    nombre: str
    vm: int
    parametro_maximo: float
    parametro_minimo: float
    actuadores_asociados: Optional[List[int]] = [] 


class Actuador(BaseModel):
    id: int
    nombre: str
    marca_arranque: str
    estado: str
    estado_plc: str

    marca_arranque_bytebit: Optional[tuple[int, int]] = None
    estado_bytebit: Optional[tuple[int, int]] = None
    estado_pcl_bytebit: Optional[tuple[int, int]] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.marca_arranque:
            self.marca_arranque_bytebit = convertir_marca_logo_a_bytebit(self.marca_arranque)
        if self.estado:
            self.estado_bytebit = convertir_marca_logo_a_bytebit(self.estado)
        if self.estado_plc:
            self.estado_plc_bytebit = convertir_marca_logo_a_bytebit(self.estado_plc)   


class Controlador(BaseModel):
    id: int
    ip: IPvAnyAddress
    sensores: List[Sensor]
    actuadores: List[Actuador]


class Raspberry(BaseModel):
    ip_eth: IPvAnyAddress
    ip_wlan: IPvAnyAddress
    ip_wireguard: IPvAnyAddress
    ip_router: IPvAnyAddress


class Configuracion(BaseModel):
    controlador: Controlador
    raspberry: Raspberry


def cargar_configuracion(path: Optional[str] = None) -> Configuracion:
    if path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "config.yaml")

    with open(path, "r", encoding="utf-8") as archivo:
        data = yaml.safe_load(archivo)

    return Configuracion(**data)
