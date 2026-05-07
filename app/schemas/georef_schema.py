from pydantic import BaseModel


class ProvinciaResponse(BaseModel):
    id: str
    nombre: str


class LocalidadResponse(BaseModel):
    id: str
    nombre: str