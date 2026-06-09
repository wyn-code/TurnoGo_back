# app/services/geocoding_service.py

from app.services.mapbox_service import obtener_coordenadas


def geocode_negocio(direccion: str, ciudad: str | None, provincia: str | None):
    if not direccion:
        return None

    return obtener_coordenadas(
        direccion=direccion,
        ciudad=ciudad,
        provincia=provincia
    )