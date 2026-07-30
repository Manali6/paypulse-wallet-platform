from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str = Field(..., min_length=1, max_length=100)
    default_currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    photo_url: str | None = Field(default=None, max_length=512)
    default_currency: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    default_currency: str
    photo_url: str | None = None
    created_at: str

    model_config = {"from_attributes": True}
