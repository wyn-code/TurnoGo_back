import re
import requests
from decouple import config


def formatear_telefono_whatsapp(telefono: str):

    numeros = re.sub(r"\D", "", telefono)

    # sacar 0 inicial
    if numeros.startswith("0"):
        numeros = numeros[1:]

    # si viene con 549 -> sacar el 9
    if numeros.startswith("549"):
        numeros = "54" + numeros[3:]

    # si no tiene 54 -> agregarlo
    elif not numeros.startswith("54"):
        numeros = "54" + numeros

    return numeros


def enviar_whatsapp(telefono, nombre_cliente, fecha, hora, nombre_negocio):

    token = config("TU_TOKEN")

    number_id = "1183467628172556"

    url = f"https://graph.facebook.com/v25.0/{number_id}/messages"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    telefono_limpio = formatear_telefono_whatsapp(telefono)

    data = {
            "messaging_product": "whatsapp",
            "to": telefono_limpio,
            "type": "template",
            "template": {
                "name": "appointment_reminder_2",
                "language": {
                    "code": "es_AR"
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": str(nombre_cliente)},
                            {"type": "text", "text": str(nombre_negocio)},
                            {"type": "text", "text": str(fecha)},
                            {"type": "text", "text": str(hora)},
                        ]
                    }
                ]
            }
    }

    try:

            print("Probando con:", telefono_limpio)

            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=15
            )

            if response.status_code == 200:
                print("✅ WhatsApp enviado a:", telefono_limpio)
                return response.json()

            print("❌ Falló con:", telefono_limpio)
            print(response.json())

    except requests.exceptions.RequestException as e:
            print("Error:", e)
    


    return {
        "status": "failed",
        "error": "Ninguna variante funcionó"
    }