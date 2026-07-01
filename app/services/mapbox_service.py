import requests
from urllib.parse import quote

from app.core.config import MAPBOX_ACCESS_TOKEN


def obtener_coordenadas(
        
    direccion: str,
    ciudad: str | None = None,
    provincia: str | None = None,
) -> tuple[float, float] | None:
    try:
        query_parts = [direccion]

        if ciudad:
            query_parts.append(ciudad)

        if provincia:
            query_parts.append(provincia)

        query = ", ".join(query_parts)
        print(f"[GEOCODING] Query: {query}")  # 👈 1

        query_encoded = quote(query)
        print(MAPBOX_ACCESS_TOKEN)
        url = (
            f"https://api.mapbox.com/geocoding/v5/mapbox.places/"
            f"{query_encoded}.json"
        )

        params = {
            "access_token": MAPBOX_ACCESS_TOKEN,
            "limit": 1,
            "country": "AR"
        }

        response = requests.get(url, params=params, timeout=10)

        print("STATUS:", response.status_code)
        print("URL:", response.url)
        print("BODY:", response.text)

        response.raise_for_status()

        data = response.json()   # ← primero crear la variable

        print("[GEOCODING] Respuesta:", data)   # ← recién acá usarla

        features = data.get("features", [])

        if not features:
            print("[GEOCODING] No se encontraron resultados")  # 👈 3
            return None

        longitud, latitud = features[0]["center"]

        print(f"[GEOCODING] Lat: {latitud} Lng: {longitud}")  # 👈 4

        return latitud, longitud

    except Exception as e:
        print(f"[GEOCODING ERROR] {e}")
        return None