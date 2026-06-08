import resend

from app.core.config import (
    RESEND_API_KEY,
    FRONTEND_URL,
)

resend.api_key = RESEND_API_KEY


def send_verification_email(
    email: str,
    token: str,
):
    print("Entró a send_verification_email")
    print("Email:", email)

    verification_link = (
        f"{FRONTEND_URL}/verify-email/{token}"
    )

    print(
        "Verification link:",
        verification_link
    )

    params = {
        "from": "onboarding@resend.dev",
        "to": [email],
        "subject": "Verificá tu cuenta",
        "html": f"""
            <h2>Bienvenido a Turnexo</h2>

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

    print("Enviando email a Resend...")

    response = resend.Emails.send(params)

    print("Respuesta Resend:")
    print(response)

    return response