import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.schemas.cliente_schema import ClienteCreate


def obtener_cliente_por_id(db: Session, cliente_id: int):
    return db.query(Cliente).filter(Cliente.id_cliente == cliente_id).first()


def obtener_cliente_por_telefono(db: Session, telefono: str):
    return db.query(Cliente).filter(Cliente.telefono == telefono).first()


def normalizar_telefono(telefono: str) -> str:
    telefono = telefono.strip()
    telefono = re.sub(r"\s+", "", telefono)
    telefono = re.sub(r"[^\d+]", "", telefono)
    return telefono


def validar_cliente(datos: ClienteCreate):
    telefono = normalizar_telefono(datos.telefono)

    if not telefono:
        raise HTTPException(status_code=400, detail="El teléfono es obligatorio")

    if len(re.sub(r"\D", "", telefono)) < 8:
        raise HTTPException(status_code=400, detail="El teléfono no es válido")

    if not datos.nombre.strip():
        raise HTTPException(status_code=400, detail="El nombre es obligatorio")

    if not datos.apellido.strip():
        raise HTTPException(status_code=400, detail="El apellido es obligatorio")

    return telefono


def obtener_o_crear_cliente(db: Session, datos: ClienteCreate):
    telefono_normalizado = validar_cliente(datos)

    cliente_existente = obtener_cliente_por_telefono(db, telefono_normalizado)
    if cliente_existente:
        return cliente_existente

    nuevo_cliente = Cliente(
        telefono=telefono_normalizado,
        nombre=datos.nombre.strip(),
        apellido=datos.apellido.strip(),
    )

    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)

    return nuevo_cliente