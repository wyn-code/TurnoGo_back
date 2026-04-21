from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.cliente import Cliente
from app.schemas.cliente_schema import ClienteCreate, ClienteResponse
from app.services.cliente_service import (
    obtener_cliente_por_id,
    obtener_o_crear_cliente,
)

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/{cliente_id}", response_model=ClienteResponse)
def obtener(cliente_id: int, db: Session = Depends(get_db)):
    cliente = obtener_cliente_por_id(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@router.get("/", response_model=list[ClienteResponse])
def listar(db: Session = Depends(get_db)):
    return db.query(Cliente).all()

@router.post("/get-or-create", response_model=ClienteResponse, status_code=200)
def get_or_create(datos: ClienteCreate, db: Session = Depends(get_db)):
    return obtener_o_crear_cliente(db, datos)


