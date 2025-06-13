# D:\vai_pi4\models\actuadores.py
from sqlalchemy import Column, Integer, String, Date, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class EventoActuador(Base):
    __tablename__ = 'evento_actuador'

    id = Column(Integer, primary_key=True, autoincrement=True)
    accion = Column(String(50), nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    actuador = Column(Integer, nullable=False)
    origen_evento = Column(String(20), nullable=False, default='plc')
    usuario = Column(Integer, nullable=True)      # puede ser None si es origen plc
    controlador = Column(Integer, nullable=True) # puede ser None si es origen usuario
