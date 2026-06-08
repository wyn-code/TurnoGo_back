import requests

from app.core.config import MAPBOX_ACCESS_TOKEN


def obtener_coordenadas(direccion: str) -> tuple[float, float]:
    url = (
        f"https://api.mapbox.com/geocoding/v5/mapbox.places/"
        f"{direccion}.json"
    )

    params = {
        "access_token": MAPBOX_ACCESS_TOKEN,
        "limit": 1,
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    features = data.get("features", [])
    if not features:
        raise ValueError(
            f"No se encontraron coordenadas para: {direccion}"
        )

    longitud, latitud = features[0]["center"]

    return latitud, longitud