from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import SessionLocal
from models.sensores import SensorLectura

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/datos/sensores")
def obtener_datos_sensores(id_sensor: Optional[int] = Query(None), db: Session = Depends(get_db)):
    query = db.query(SensorLectura)
    if id_sensor is not None:
        query = query.filter(SensorLectura.id_sensor == id_sensor)
    datos = query.order_by(SensorLectura.fecha.desc(), SensorLectura.hora.desc()).all()
    return datos
