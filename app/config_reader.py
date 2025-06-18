# config_reader.py
from pydantic import BaseModel, Field, IPvAnyAddress
from typing import List
import yaml
from typing import Optional
import os


class Sensor(BaseModel):
    id: int
    nombre: str
    vm: int
    parametro_maximo: float
    parametro_minimo: float


class Actuador(BaseModel):
    id: int
    nombre: str
    marca_arranque: str
    nq_estado: str


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


def cargar_configuracion(path: Optional[str] = None):
    if path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))  # D:\vai_pi4\app
        path = os.path.join(base_dir, "config.yaml")            # D:\vai_pi4\app\config.yaml

    with open(path, "r", encoding="utf-8") as archivo:
        data = yaml.safe_load(archivo)
    
    return Configuracion(**data)