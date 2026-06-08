from pydantic import BaseModel, EmailStr, Field

from app.schemas.usuario_schema import UsuarioResponse


class RegisterRequest(BaseModel):
    usuario_us: str = Field(min_length=3, max_length=30)
    email_us: EmailStr
    contrasena_us: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email_us: str
    contrasena_us: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    usuario: UsuarioResponse
    token: TokenResponse

class ForgotPasswordRequest(BaseModel):
    email_us: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(
        min_length=10,
        max_length=20
    )

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(
        min_length=10,
        max_length=20
    )
    confirm_password: str = Field(
        min_length=10,
        max_length=20
    )
