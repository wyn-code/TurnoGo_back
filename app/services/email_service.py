import resend

from app.core.config import (
    RESEND_API_KEY,
    FRONTEND_URL,
    BACKEND_URL,

)

resend.api_key = RESEND_API_KEY


def send_verification_email(
    email: str,
    token: str,
):
    verification_link = (
    f"{FRONTEND_URL}/verify-email/{token}"
    )   

    params = {
        "from": "Turnogo <contacto@turnogo.app>",
        "to": [email],
        "subject": "Verificá tu cuenta",
        "html": f"""
            <h2>Bienvenido a Turnogo</h2>

            <p>
                Hacé click en el siguiente enlace
                para verificar tu cuenta:
            </p>

            <a href="{verification_link}">
                Verificar cuenta
            </a>

            <p>
                Este enlace expirará en 24 horas.
            </p>
        """,
    }

    response = resend.Emails.send(params)

    return response


def send_reset_password_email(
    email: str,
    token: str,
):
    reset_link = (
        f"{FRONTEND_URL}/restablecer-contrasena/{token}"
    )

    params = {
        "from": "Turnogo <contacto@turnogo.app>",
        "to": [email],
        "subject": "Restablecer contraseña",
        "html": f"""
            <h2>Restablecer contraseña</h2>

            <p>
                Recibimos una solicitud para cambiar
                la contraseña de tu cuenta.
            </p>

            <p>
                Hacé click en el siguiente enlace:
            </p>

            <a href="{reset_link}">
                Restablecer contraseña
            </a>

            <p>
                Este enlace expirará en 1 hora.
            </p>
        """,
    }

    print("=== ENVIANDO EMAIL RESET PASSWORD ===")
    print("Destinatario:", email)
    print("Link:", reset_link)

    try:
        response = resend.Emails.send(params)
        print("=== RESPUESTA RESEND ===")
        print(response)
        return response
    except Exception as e:
        print(f"=== ERROR ENVIANDO EMAIL RESET PASSWORD ===")
        print(f"Error: {e}")
        raise