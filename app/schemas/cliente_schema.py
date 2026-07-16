from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ClienteBase(BaseModel):
    telefono: str
    nombre: str 
    apellido: str
    email: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id_cliente: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)