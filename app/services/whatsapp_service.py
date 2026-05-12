# import requests

# def enviar_whatsapp(telefono: str, nombre_cliente: str, fecha: str, hora: str):
#     # El ID del número y el Token deben estar en tu .env
#     token = "TU_ACCESS_TOKEN"
#     number_id = "TU_PHONE_NUMBER_ID"
#     url = f"https://graph.facebook.com/v18.0/{number_id}/messages"
    
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Content-Type": "application/json"
#     }
    
#     # Estructura para una plantilla (Template) de Meta
#     data = {
#         "messaging_product": "whatsapp",
#         "to": telefono,
#         "type": "template",
#         "template": {
#             "name": "recordatorio_24hs", # Nombre de tu plantilla aprobada
#             "language": { "code": "es_AR" },
#             "components": [
#                 {
#                     "type": "body",
#                     "parameters": [
#                         {"type": "text", "text": nombre_cliente},
#                         {"type": "text", "text": fecha},
#                         {"type": "text", "text": hora}
#                     ]
#                 }
#             ]
#         }
#     }
    
#     response = requests.post(url, headers=headers, json=data)
#     return response.json()