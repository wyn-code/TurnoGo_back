from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.servicio import Servicio

router = APIRouter(prefix="/servicios", tags=["Servicios"])

# 📄 LISTAR


@router.get("/")
def listar_servicios(db: Session = Depends(get_db)):
    return db.query(Servicio).all()


# ➕ CREAR
@router.post("/")
def crear_servicio(data: dict, db: Session = Depends(get_db)):
    nuevo = Servicio(
        nombre_servicio=data["nombre_servicio"],
        precio=data["precio"],
        requiere_aprobacion=data.get("requiere_aprobacion", False),
        duracion_min=data.get("duracion_min"),
        duracion_max=data.get("duracion_max"),
        activo=data.get("activo", True)
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


# ❌ ELIMINAR
@router.delete("/{id_servicio}")
def eliminar_servicio(id_servicio: int, db: Session = Depends(get_db)):
    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == id_servicio
    ).first()

    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    db.delete(servicio)
    db.commit()

    return {"mensaje": "Servicio eliminado"}
