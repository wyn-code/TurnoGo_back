import re
from decouple import config
from twilio.rest import Client

# Cargamos las variables de entorno una sola vez
TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = config("TWILIO_WHATSAPP_NUMBER", default="whatsapp:+14155238886")


def formatear_numero_twilio(telefono: str) -> str:
    """
    Limpia el número de teléfono del cliente de la base de datos y asegura el 
    formato internacional que Twilio requiere para Argentina ('whatsapp:+549XXXXXXXXX').
    """
    numeros = re.sub(r"\D", "", telefono)

    # Quitar 0 inicial si viene con código de área (ej: 0336 -> 336)
    if numeros.startswith("0"):
        numeros = numeros[1:]

    # Remover el 15 intermedio si el usuario lo ingresó (ej: 54933615...)
    if len(numeros) == 12 and numeros.startswith("54") and numeros[5:7] == "15":
        numeros = numeros[:5] + numeros[7:]
    elif len(numeros) == 10 and numeros.startswith("15"):
        numeros = numeros[2:]

    # Asegurar el prefijo 'whatsapp:+549'
    if numeros.startswith("549"):
        return f"whatsapp:+{numeros}"
    elif numeros.startswith("54"):
        return f"whatsapp:+549{numeros[2:]}"
    else:
        return f"whatsapp:+549{numeros}"


def enviar_notificacion_turno(telefono_cliente: str, nombre_cliente: str, nombre_negocio: str, fecha: str, hora: str) -> bool:
    """
    Envía el recordatorio formateado al cliente final vía Twilio.
    Devuelve True si el mensaje se envió con éxito, False en caso contrario.
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        destino = formatear_numero_twilio(telefono_cliente)
        
        # 🛠️ BLINDAJE DE SEGURIDAD PARA EL REMITENTE
        # Nos aseguramos a nivel de código que empiece con 'whatsapp:' por si el .env no lo tiene
        remitente = TWILIO_WHATSAPP_NUMBER.strip()
        if not remitente.startswith("whatsapp:"):
            remitente = f"whatsapp:{remitente}"
        
        cuerpo_mensaje = (
            f"Hola *{nombre_cliente}*! 👋 Te recordamos tu turno en *{nombre_negocio}*\n"
            f"🗓️ Día: *{fecha}*\n"
            f"🕒 Hora: *{hora}*\n\n"
            f"¡Te esperamos!"
        )

        print(f"📱 Enviando recordatorio vía Twilio a {destino} desde {remitente}...")
        message = client.messages.create(
            from_=remitente,  # Usamos la variable blindada con el canal correcto
            body=cuerpo_mensaje,
            to=destino
        )
        
        print(f"✅ Notificación enviada. SID: {message.sid}")
        return True

    except Exception as e:
        print(f"❌ Error crítico enviando WhatsApp con Twilio: {e}")
        return False