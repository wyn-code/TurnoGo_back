class EstadoSimple(BaseModel):
    id_estado: int
    nombre_estado: str

    model_config = ConfigDict(from_attributes=True)
