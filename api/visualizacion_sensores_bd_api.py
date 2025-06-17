# vai_pi4/api/visualizacion_sensores_bd_api.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from models.sensores import SensorLectura

router = APIRouter()

# Dependencia para obtener sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/datos/sensores")
def obtener_datos_sensores(db: Session = Depends(get_db)):
    datos = db.query(SensorLectura).order_by(SensorLectura.fecha.desc(), SensorLectura.hora.desc()).all()
    return datos
