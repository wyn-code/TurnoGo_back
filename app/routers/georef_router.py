from fastapi import APIRouter
from app.services.georef_service import (
    obtener_provincias,
    obtener_localidades
)
from app.services.mapbox_service import obtener_coordenadas

router = APIRouter(
    prefix="/georef",
    tags=["Georef"]
)


@router.get("/provincias")
def provincias():
    return obtener_provincias()


@router.get("/localidades")
def localidades(provincia: str):
    return obtener_localidades(provincia)


@router.get("/test-geocoding")
def test_geocoding():
    return obtener_coordenadas(
        "Av. Corrientes 1234",
        "Buenos Aires",
        "Buenos Aires",
    )
