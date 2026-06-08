from datetime import datetime, timedelta
import secrets
import re
from app.services.email_service import (
    send_verification_email,
)
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)

from app.models.negocio import Negocio
from app.models.usuario import Usuario

from app.schemas.auth_schema import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)


PASSWORD_REGEX = (
    r"^(?=.*[a-z])"
    r"(?=.*[A-Z])"
    r"(?=.*\d)"
    r"(?=.*[@$!%*?&.#_-])"
    r"[A-Za-z\d@$!%*?&.#_-]{12,16}$"
)

def register_user(db: Session, data: RegisterRequest) -> Usuario:
    
    existing_user = (
        db.query(Usuario)
        .filter(
            or_(
                Usuario.email_us == data.email_us,
                Usuario.usuario_us == data.usuario_us,
            )
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email o nombre de usuario ya existe",
        )

    if not re.match(PASSWORD_REGEX, data.contrasena_us):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "La contraseña debe tener entre 12 y 16 caracteres, "
                "incluyendo al menos una mayúscula, una minúscula, "
                "un número y un carácter especial"
            ),
        )

    verification_token = (
    secrets.token_urlsafe(32)
)

    usuario = Usuario(
        usuario_us=data.usuario_us.strip(),
        email_us=data.email_us.strip(),
        contrasena_us=get_password_hash(data.contrasena_us),

        email_verified=False,
        verification_token=verification_token,
        verification_token_expiration=(
            datetime.utcnow() + timedelta(hours=24)
        ),
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    send_verification_email(
        usuario.email_us,
        verification_token,
    )

    return usuario


def login_user(db: Session, data: LoginRequest) -> tuple[Usuario, TokenResponse]:
    usuario = (
        db.query(Usuario)
        .filter(
            or_(
                Usuario.email_us == data.email_us,
                Usuario.usuario_us == data.email_us,
            )
        )
        .first()
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    if not verify_password(
        data.contrasena_us,
        usuario.contrasena_us,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )
    
    if not usuario.email_verified:
        raise HTTPException(
            status_code=403,
            detail="Debes verificar tu email antes de iniciar sesión",
    )

    token = create_access_token(
        subject=usuario.id_us,
        expires_delta=timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    )

    return usuario, TokenResponse(
        access_token=token
    )


def build_me_response(db: Session, current_user: Usuario) -> dict:
    negocio = db.query(Negocio).filter(
        Negocio.usuario_id == current_user.id_us
    ).first()

    return {
        "id_us": current_user.id_us,
        "email_us": current_user.email_us,
        "usuario_us": current_user.usuario_us,
        "has_business": negocio is not None,
        "role": current_user.role,
    }

'''
def forgot_password(
    db: Session,
    email: str,
):
    print("Entró a forgot_password")
    print("Email recibido:", email)

    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.email_us == email
        )
        .first()
    )

    print("Usuario encontrado:", usuario)

    if not usuario:
        print("NO EXISTE EL USUARIO")
        return {
            "message": (
                "Si el email existe, se enviará un enlace"
            )
        }

    token = secrets.token_urlsafe(32)

    print("Token generado:", token)

    usuario.reset_token = token
    usuario.reset_token_expiration = (
        datetime.utcnow() + timedelta(hours=1)
    )

    db.commit()

    print("Antes de enviar email")

    send_reset_password_email(
        usuario.email_us,
        token,
    )

    print("Después de enviar email")

    return {
        "message": (
            "Si el email existe, se enviará un enlace"
        )
    }

'''

def reset_password(
    db: Session,
    token: str,
    new_password: str,
):
    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.reset_token == token
        )
        .first()
    )

    if not usuario:
        raise HTTPException(
            status_code=400,
            detail="Token inválido",
        )

    if (
        usuario.reset_token_expiration is None
        or usuario.reset_token_expiration
        < datetime.utcnow()
    ):
        raise HTTPException(
            status_code=400,
            detail="Token expirado",
        )

    if not re.match(
        PASSWORD_REGEX,
        new_password,
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "La contraseña debe tener "
                "entre 10 y 20 caracteres, "
                "incluyendo mayúscula, "
                "minúscula y número"
            ),
        )

    usuario.contrasena_us = (
        get_password_hash(new_password)
    )

    usuario.reset_token = None
    usuario.reset_token_expiration = None

    db.commit()

    return {
        "message": "Contraseña actualizada"
    }

def verify_email(
    db: Session,
    token: str,
):
    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.verification_token == token
        )
        .first()
    )

    if not usuario:
        raise HTTPException(
            status_code=400,
            detail="Token inválido",
        )

    if (
        usuario.verification_token_expiration is None
        or usuario.verification_token_expiration
        < datetime.utcnow()
    ):
        raise HTTPException(
            status_code=400,
            detail="Token expirado",
        )

    usuario.email_verified = True
    usuario.verification_token = None
    usuario.verification_token_expiration = None

    db.commit()

    return {
        "message": "Email verificado correctamente"
    }