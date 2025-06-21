# D:\vai_pi4\models\actuadores.py
from sqlalchemy import Column, DateTime, Integer, String, Date, Time
from app.database import Base 

class EventoActuador(Base):
    __tablename__ = 'evento_actuador'

    id = Column(Integer, primary_key=True, autoincrement=True)
    accion = Column(String(50), nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    actuador = Column(Integer, nullable=False)
    origen_evento = Column(String(20), nullable=False)
    usuario = Column(Integer, nullable=True)
    controlador = Column(Integer, nullable=True)


class UltimoEstadoPLC(Base):
    __tablename__ = 'ultimo_estado_plc'

    id = Column(Integer, primary_key=True, autoincrement=True)
    actuador = Column(Integer, unique=True, nullable=False)
    estado = Column(String(3), nullable=False)  # "ON" o "OFF"
    actualizado = Column(DateTime, nullable=False)
