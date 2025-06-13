#sensores.py
from sqlalchemy import Column, Integer, Float, Date, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SensorLectura(Base):
    __tablename__ = 'sensor_lecturas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_sensor = Column(Integer, nullable=False)
    valor = Column(Float, nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
