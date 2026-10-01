from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field


class EspacioBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    numero: Optional[int] = Field(default=None, ge=0)
    descripcion: Optional[str] = None


class EspacioCreate(EspacioBase):
    """Body de POST /espacios."""

    id_negocio: int


class EspacioCreateNested(EspacioBase):
    """Espacio incluido dentro del onboarding del negocio."""


class EspacioUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    numero: Optional[int] = Field(default=None, ge=0)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class EspacioResponse(EspacioBase):
    id_espacio: int
    id_negocio: int
    activo: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @computed_field  # alias legado para clientes que aún leen `id_cancha`
    @property
    def id_cancha(self) -> int:
        return self.id_espacio
