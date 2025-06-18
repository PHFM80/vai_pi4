from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
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
def obtener_datos_actuadores(id_actuador: Optional[int] = Query(None), db: Session = Depends(get_db)):
    query = db.query(EventoActuador)
    if id_actuador is not None:
        query = query.filter(EventoActuador.actuador == id_actuador)
    eventos = query.order_by(EventoActuador.fecha.desc(), EventoActuador.hora.desc()).all()
    return eventos
