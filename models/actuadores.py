# D:\vai_pi4\models\actuadores.py
from sqlalchemy import Column, Integer, String, Date, Time
from app.database import Base 

class EventoActuador(Base):
    __tablename__ = 'evento_actuador'

    id = Column(Integer, primary_key=True, autoincrement=True)
    accion = Column(String(50), nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    actuador = Column(Integer, nullable=False)
    origen_evento = Column(String(20), nullable=False, default='plc')
    usuario = Column(Integer, nullable=True)
    controlador = Column(Integer, nullable=True)

