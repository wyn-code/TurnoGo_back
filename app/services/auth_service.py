from datetime import timedelta
import re
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.negocio import Negocio
from app.models.usuario import Usuario
from app.schemas.auth_schema import LoginRequest, RegisterRequest, TokenResponse

PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{10,20}$"

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
                "La contraseña debe tener entre 10 y 20 caracteres, "
                "incluyendo al menos una mayúscula, una minúscula, "
                "un número"
            ),
        )

    usuario = Usuario(
        usuario_us=data.usuario_us.strip(),
        email_us=data.email_us.strip(),
        contrasena_us=get_password_hash(data.contrasena_us),
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
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
    usuarios = db.query(Usuario).all()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    if not verify_password(data.contrasena_us, usuario.contrasena_us):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    token = create_access_token(
        subject=usuario.id_us,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return usuario, TokenResponse(access_token=token)


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
