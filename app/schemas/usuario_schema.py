from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UsuarioBase(BaseModel):
    usuario_us: str
    email_us: EmailStr


class UsuarioCreate(UsuarioBase):
    contrasena_us: str


class UsuarioUpdate(BaseModel):
    usuario_us: Optional[str] = None
    email_us: Optional[EmailStr] = None
    contrasena_us: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    id_us: int
    created_at: Optional[datetime] = None
    role: str 
    model_config = ConfigDict(from_attributes=True)