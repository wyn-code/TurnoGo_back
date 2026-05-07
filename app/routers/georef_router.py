from fastapi import APIRouter
from app.services.georef_service import (
    obtener_provincias,
    obtener_localidades
)

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