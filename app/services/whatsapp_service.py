import re
import requests


def formatear_telefono_argentina(telefono_sucio: str) -> str:
    """Elimina caracteres no numéricos y asegura el formato estricto de Meta (54 + área sin 0 + número sin 15)."""
    # Deja solo los números
    numeros = re.sub(r"\D", "", telefono_sucio)

    # Si empieza con 549 (formato común que la gente confunde), le removemos el 9
    if numeros.startswith("549") and len(numeros) > 11:
        return "54" + numeros[3:]

    # Si ya empieza con 54 (y no tiene un 9 colgado), lo devolvemos directo
    if numeros.startswith("54"):
        return numeros

    # Si el usuario metió el número con el '0' inicial (ej: 0336...), se lo quitamos
    if numeros.startswith("0"):
        numeros = numeros[1:]

    # Quitamos el '15' si quedó en el medio del código de área
    # Para características de 3 dígitos (ej: 336)
    if len(numeros) >= 10 and numeros[3:5] == "15":
        numeros = numeros[:3] + numeros[5:]
    # Para características de 2 dígitos (ej: 11)
    elif len(numeros) >= 10 and numeros[2:4] == "15":
        numeros = numeros[:2] + numeros[4:]

    # Le anteponemos el código de Argentina correcto para la API de Meta (54)
    return f"54{numeros}"


def enviar_whatsapp(telefono: str, nombre_cliente: str, fecha: str, hora: str, nombre_negocio: str):
    token = "EAAb0qeeKSJEBRhrbnRPo2ZAaPhWU5RjX5KAk6TNP5zWyQoorJRvhGRj1SvKf6ai5ohC5QWfgtvAg25rfMQx29tY25aJEbEgB0mOpUF10swa5jyaQW0ZBKFcxvJfu384KGD5Hp8Iy5nNdlCzfx2NNlAAubJOoXdvTtjOzIf3l5EK1e2dn6hNbFHlXwV06T6JI1kTaZCUIVbti4bJkZCxlDGbTOWDZBmovnxfmZBJIyxrqbq7an8IZB8DBSoFmxHdBPwDt8UqCQfSGmU1zPZBtdHgpshi1"  # <-- TU TOKEN REAL ACÁ
    number_id = "1183467628172556"
    url = f"https://graph.facebook.com/v18.0/{number_id}/messages"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Limpiamos el teléfono antes de enviarlo
    telefono_limpio = formatear_telefono_argentina(telefono)

    # ... (todo el resto de tu función queda igual) ...
    # 1. Cambiamos los datos del template por tu plantilla aprobada en español
    data = {
        "messaging_product": "whatsapp",
        "to": telefono_limpio,  # Teléfono dinámico del cliente
        "type": "template",
        "template": {
            "name": "appointment_reminder_2",  # <-- El nombre exacto de tu plantilla aprobada
            "language": {
                "code": "es_AR"           # <-- El idioma en el que la creaste
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        # Variable {{1}}: Nombre del cliente
                        {"type": "text", "text": nombre_cliente},
                        
                        # Variable {{2}}: Nombre del negocio
                       {"type": "text", "text": nombre_negocio},
                        
                        # Variable {{3}}: Fecha del turno (ej: "19/05/2026")
                        {"type": "text", "text": fecha},
                        
                        # Variable {{4}}: Hora del turno (ej: "15:30")
                        {"type": "text", "text": hora},
                        
                    ]
                }
            ]
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)

        # Si da error, imprimimos el JSON de Meta ANTES de que explote el raise_for_status
        if response.status_code != 200:
            print(f"❌ DETALLE DEL REBOTE DE META: {response.json()}")

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error crítico al enviar WhatsApp: {e}")
        return {"error": str(e), "status": "failed"}
