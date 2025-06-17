# vai_pi4/api/visualizacion_actuadores_bd_api.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from models.actuadores import EventoActuador

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/datos/actuadores")
def obtener_datos_actuadores(db: Session = Depends(get_db)):
    eventos = db.query(EventoActuador).order_by(EventoActuador.fecha.desc(), EventoActuador.hora.desc()).all()
    return eventos
