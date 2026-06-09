from pydantic import BaseModel
from pydantic import BaseModel, ConfigDict


class ProvinciaResponse(BaseModel):
    id: str
    nombre: str
    model_config = ConfigDict(from_attributes=True)


class LocalidadResponse(BaseModel):
    id: str
    nombre: str
    model_config = ConfigDict(from_attributes=True)