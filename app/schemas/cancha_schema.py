"""Alias legados: `Cancha*` pasó a llamarse `Espacio*` (ver espacio_schema.py)."""

from app.schemas.espacio_schema import (  # noqa: F401
    EspacioBase as CanchaBase,
    EspacioBase as CanchaCreate,  # el id_negocio viene del path legado
    EspacioCreateNested as CanchaCreateNested,
    EspacioResponse as CanchaResponse,
    EspacioUpdate as CanchaUpdate,
)
