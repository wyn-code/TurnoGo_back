from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.usuario import Usuario
from app.schemas.auth_schema import LoginRequest, RegisterRequest, TokenResponse


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

    usuario = Usuario(
        usuario_us=data.usuario_us,
        email_us=data.email_us,
        contrasena_us=get_password_hash(data.contrasena_us),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def login_user(db: Session, data: LoginRequest) -> tuple[Usuario, TokenResponse]:
    print("====== LOGIN DEBUG ======")
    print("DATA:", data)

    usuario = db.query(Usuario).filter(Usuario.email_us == data.email_us).first()

    if not usuario:
        print("❌ Usuario no encontrado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    print("------ DB DEBUG ------")
    print("HASH DB:", usuario.contrasena_us)

    print("---- VERIFY ----")
    is_valid = verify_password(data.contrasena_us, usuario.contrasena_us)
    print("VERIFY RESULT:", is_valid)

    if not is_valid:
        print("❌ Password no coincide")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    print("✅ Login correcto")

    token = create_access_token(
        subject=usuario.id_us,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return usuario, TokenResponse(access_token=token)

