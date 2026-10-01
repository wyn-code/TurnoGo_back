from typing import Optional
from pydantic import ConfigDict

from pydantic import BaseModel, Field


class CategoriaBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    icono: Optional[str] = Field(default=None, max_length=500)
    descripcion: Optional[str] = Field(default=None, max_length=255)


class CategoriaCreate(CategoriaBase):
    parent_id: Optional[int] = None


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    icono: Optional[str] = Field(default=None, max_length=500)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    parent_id: Optional[int] = None


class CategoriaResponse(CategoriaBase):
    id_categoria: int
    parent_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class CategoriaTop(CategoriaResponse):
    """Categoría con la cantidad de negocios activos (GET /categorias/top)."""

    cantidad_negocios: int


class CategoriaTree(CategoriaResponse):
    """Categoría con sus hijos anidados (GET /categorias/tree)."""

    children: list["CategoriaTree"] = Field(default_factory=list)


CategoriaRead = CategoriaResponse
