from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException
from unittest.mock import patch

from app.services import auth_service
from app.schemas.auth_schema import RegisterRequest
from app.models.usuario import Usuario
from app.core.security import verify_password, get_password_hash
from app.schemas.auth_schema import LoginRequest


def test_register_user_ok(db: auth_service.Session, monkeypatch: pytest.MonkeyPatch):
    enviado = {}

    def fake_send_email(email, token):
        enviado["email"] = email
        enviado["token"] = token

    monkeypatch.setattr(
        auth_service,
        "send_verification_email",
        fake_send_email,
    )

    data = RegisterRequest(
        usuario_us="rocco",
        email_us="rocco@test.com",
        contrasena_us="Password123!"
    )

    usuario = auth_service.register_user(db, data)

    assert usuario.id_us is not None
    assert usuario.email_us == "rocco@test.com"
    assert usuario.usuario_us == "rocco"
    assert usuario.email_verified is False
    assert usuario.verification_token is not None

    assert enviado["email"] == "rocco@test.com"
    assert enviado["token"] == usuario.verification_token


def test_register_user_email_duplicado(db: auth_service.Session):
    usuario = Usuario(
        usuario_us="rocco",
        email_us="rocco@test.com",
        contrasena_us="123",
        email_verified=True,
    )

    db.add(usuario)
    db.commit()

    data = RegisterRequest(
        usuario_us="otro",
        email_us="rocco@test.com",
        contrasena_us="Password123!"
    )

    with pytest.raises(HTTPException) as exc:
        auth_service.register_user(db, data)

    assert exc.value.status_code == 409

def test_register_user_usuario_duplicado(db: auth_service.Session):
    usuario = Usuario(
        usuario_us="rocco",
        email_us="otro@test.com",
        contrasena_us="123",
        email_verified=True,
    )

    db.add(usuario)
    db.commit()

    data = RegisterRequest(
        usuario_us="rocco",
        email_us="nuevo@test.com",
        contrasena_us="Password123!"
    )

    with pytest.raises(HTTPException) as exc:
        auth_service.register_user(db, data)

    assert exc.value.status_code == 409


def test_register_user_password_invalida(db: auth_service.Session):
    data = RegisterRequest(
        usuario_us="rocco",
        email_us="rocco@test.com",
        contrasena_us="123456"
    )

    with pytest.raises(HTTPException) as exc:
        auth_service.register_user(db, data)

    assert exc.value.status_code == 400



def test_register_user_password_hasheada(db: auth_service.Session, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        auth_service,
        "send_verification_email",
        lambda *args, **kwargs: None,
    )

    password = "Password123!"

    data = RegisterRequest(
        usuario_us="rocco",
        email_us="rocco@test.com",
        contrasena_us=password,
    )

    usuario = auth_service.register_user(db, data)

    assert usuario.contrasena_us != password
    assert verify_password(password, usuario.contrasena_us)

# ---------------- LOGIN ----------------

def test_login_user_ok_con_email(db):
    password = "Password123!"

    usuario = Usuario(
        usuario_us="rocco",
        email_us="rocco@test.com",
        contrasena_us=get_password_hash(password),
        email_verified=True,
    )

    db.add(usuario)
    db.commit()

    user, token = auth_service.login_user(
        db,
        LoginRequest(
            email_us="rocco@test.com",
            contrasena_us=password,
        ),
    )

    assert user.id_us == usuario.id_us
    assert token.access_token is not None
    assert len(token.access_token) > 0

def test_login_user_ok_con_usuario(db):
    password = "Password123!"

    usuario = Usuario(
        usuario_us="rocco",
        email_us="rocco@test.com",
        contrasena_us=get_password_hash(password),
        email_verified=True,
    )

    db.add(usuario)
    db.commit()

    user, token = auth_service.login_user(
        db,
        LoginRequest(
            email_us="rocco",
            contrasena_us=password,
        ),
    )

    assert user.usuario_us == "rocco"
    assert token.access_token

def test_login_usuario_inexistente(db):
    with pytest.raises(HTTPException) as exc:
        auth_service.login_user(
            db,
            LoginRequest(
                email_us="noexiste@test.com",
                contrasena_us="Password123!",
            ),
        )

    assert exc.value.status_code == 401

def test_login_password_incorrecta(db):
    usuario = Usuario(
        usuario_us="rocco",
        email_us="rocco@test.com",
        contrasena_us=get_password_hash("Password123!"),
        email_verified=True,
    )

    db.add(usuario)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        auth_service.login_user(
            db,
            LoginRequest(
                email_us="rocco@test.com",
                contrasena_us="OtraPassword123!",
            ),
        )

    assert exc.value.status_code == 401

def test_login_email_no_verificado(db):
    usuario = Usuario(
        usuario_us="rocco",
        email_us="rocco@test.com",
        contrasena_us=get_password_hash("Password123!"),
        email_verified=False,
    )

    db.add(usuario)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        auth_service.login_user(
            db,
            LoginRequest(
                email_us="rocco@test.com",
                contrasena_us="Password123!",
            ),
        )

    assert exc.value.status_code == 403

def test_login_devuelve_token_string(db):
    usuario = Usuario(
        usuario_us="rocco",
        email_us="rocco@test.com",
        contrasena_us=get_password_hash("Password123!"),
        email_verified=True,
    )

    db.add(usuario)
    db.commit()

    _, token = auth_service.login_user(
        db,
        LoginRequest(
            email_us="rocco@test.com",
            contrasena_us="Password123!",
        ),
    )

    assert isinstance(token.access_token, str)

# ---------------- PASSWORD ----------------

def test_forgot_password_flow(db, seed_data):

    usuario = seed_data["usuario_1"]

    with patch(
        "app.services.auth_service.send_reset_password_email"
    ) as mock_mail:

        response = auth_service.forgot_password(
            db,
            usuario.email_us,
        )

    db.refresh(usuario)

    assert response == {
        "message": "Si el email existe, se enviará un enlace"
    }

    assert usuario.reset_token is not None
    assert usuario.reset_token_expiration is not None

    mock_mail.assert_called_once_with(
        usuario.email_us,
        usuario.reset_token,
    )


def test_reset_password_success(db):

    usuario = Usuario(
        usuario_us="usuario_test",
        email_us="usuario@test.com",
        contrasena_us=get_password_hash("OldPassword123"),
        email_verified=True,
        reset_token="abc123",
        reset_token_expiration=(
            datetime.now()
            + timedelta(hours=1)
        ),
    )

    db.add(usuario)
    db.commit()


    response = auth_service.reset_password(
        db,
        "abc123",
        "NuevoPass123!",
    )


    assert response == {
        "message": "Contraseña actualizada"
    }


    usuario_db = (
        db.query(Usuario)
        .filter(
            Usuario.email_us == "usuario@test.com"
        )
        .first()
    )


    assert usuario_db.reset_token is None
    assert usuario_db.reset_token_expiration is None


    assert verify_password(
        "NuevoPass123!",
        usuario_db.contrasena_us
    )

def test_forgot_password_email_no_existe(db):

    response = auth_service.forgot_password(
        db,
        "fake@test.com"
    )

    assert response == {
        "message": "Si el email existe, se enviará un enlace"
    }

def test_reset_password_token_invalido(db):

    with pytest.raises(HTTPException) as exc:

        auth_service.reset_password(
            db,
            "token-falso",
            "NuevaPassword123!"
        )

    assert exc.value.status_code == 400


# ---------------- EMAIL  ----------------

def test_verify_email_success(db):

    usuario = Usuario(
        usuario_us="usuario_test",
        email_us="usuario@test.com",
        contrasena_us=get_password_hash("OldPass123!"),
        email_verified=False,
        verification_token="verify123",
        verification_token_expiration=(
            datetime.now()
            + timedelta(hours=1)
        ),
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)


    response = auth_service.verify_email(
        db,
        "verify123",
    )


    assert response["message"] == (
        "Email verificado correctamente"
    )

    assert response["access_token"] is not None
    assert response["token_type"] == "bearer"
    assert response["usuario_id"] == usuario.id_us


    usuario_db = (
        db.query(Usuario)
        .filter(
            Usuario.email_us == "usuario@test.com"
        )
        .first()
    )


    assert usuario_db.email_verified is True
    assert usuario_db.verification_token is None
    assert usuario_db.verification_token_expiration is None



def test_verify_email_token_invalido(db):

    with pytest.raises(HTTPException) as exc:

        auth_service.verify_email(
            db,
            "token-falso",
        )


    assert exc.value.status_code == 400
    assert exc.value.detail == "Token inválido"



def test_verify_email_token_expirado(db):

    usuario = Usuario(
        usuario_us="usuario_test",
        email_us="usuario@test.com",
        contrasena_us=get_password_hash("OldPass123!"),
        email_verified=False,
        verification_token="expired123",
        verification_token_expiration=(
            datetime.now()
            - timedelta(hours=1)
        ),
    )

    db.add(usuario)
    db.commit()


    with pytest.raises(HTTPException) as exc:

        auth_service.verify_email(
            db,
            "expired123",
        )


    assert exc.value.status_code == 400
    assert exc.value.detail == "Token expirado"