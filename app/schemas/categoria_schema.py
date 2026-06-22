from typing import Optional
from pydantic import ConfigDict

from pydantic import BaseModel, Field


class CategoriaBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    icono: Optional[str] = Field(default=None, max_length=500)
    descripcion: Optional[str] = Field(default=None, max_length=255)


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    icono: Optional[str] = Field(default=None, max_length=500)
    descripcion: Optional[str] = Field(default=None, max_length=255)


class CategoriaResponse(CategoriaBase):
    id_categoria: int
    model_config = ConfigDict(from_attributes=True)


CategoriaRead = CategoriaResponse
