from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.usuario import Usuario
from app.schemas.auth_schema import AuthResponse, LoginRequest, RegisterRequest
from app.schemas.auth_schema import TokenResponse
from app.schemas.usuario_schema import UsuarioResponse
from app.services.auth_service import login_user, register_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    usuario = register_user(db, payload)
    _, token = login_user(
        db,
        LoginRequest(email_us=payload.email_us, contrasena_us=payload.contrasena_us),
    )
    return {"usuario": usuario, "token": token}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    _, token = login_user(db, payload)
    return token


@router.get("/me", response_model=UsuarioResponse)
def me(current_user: Usuario = Depends(get_current_user)):
    return current_user

