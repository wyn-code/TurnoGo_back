from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NegocioBase(BaseModel):
    nombre: str
    rubro: str
    wsp: str
    telefono: Optional[str] = None
    direccion: str
    ciudad: str
    id_localidad: Optional[int] = None
    id_provincia: Optional[int] = None
    ig_url: Optional[str] = None
    slug: str
    logo: Optional[str] = None
    activo: bool = True


class NegocioCreate(NegocioBase):
    pass


class NegocioResponse(NegocioBase):
    id_negocio: int
    creado_at: datetime
    model_config = ConfigDict(from_attributes=True)