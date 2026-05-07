import requests

BASE_URL = "https://apis.datos.gob.ar/georef/api"


def obtener_provincias():
    response = requests.get(f"{BASE_URL}/provincias")

    response.raise_for_status()

    data = response.json()

    return data["provincias"]


def obtener_localidades(provincia: str):
    response = requests.get(
        f"{BASE_URL}/localidades",
        params={
            "provincia": provincia,
            "max": 5000
        }
    )

    response.raise_for_status()

    data = response.json()

    return data["localidades"]
