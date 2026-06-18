from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.auth_service import (
    login_user,
    register_user,
    build_me_response,
    verify_email,
    forgot_password,
)
from app.schemas.auth_schema import (
    ForgotPasswordRequest,
)
from app.services.email_service import (
    send_verification_email,
    
)
from fastapi import (
    APIRouter,
    Depends,
)
from app.core.dependencies import get_current_user, get_db
from app.models.usuario import Usuario
from app.schemas.auth_schema import AuthResponse, LoginRequest, RegisterRequest, TokenResponse
from fastapi.responses import RedirectResponse


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    usuario = register_user(
        db,
        payload,
    )

    return {
        "message":
            "Cuenta creada. Revisá tu email para verificarla.",
        "email": usuario.email_us,
    }


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    _, token = login_user(db, payload)
    print("DB SESSION:", db)
    return token

@router.get("/me")
def me(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return build_me_response(db, current_user)

@router.get("/test-email")
def test_email():
    response = send_verification_email(
        "brunoo6.massocco@gmail.com",
        "token-prueba",
    )

    return {
        "ok": True,
        "response": response,
    }

@router.post("/forgot-password")
def forgot_password_endpoint(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    return forgot_password(
        db,
        request.email,
    )

@router.get("/verify-email/{token}")
def verify_email_endpoint(
    token: str,
    db: Session = Depends(get_db),
):
    return verify_email(
        db,
        token,
    )

