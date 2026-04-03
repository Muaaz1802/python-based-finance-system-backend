from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import Role


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: Role = Role.viewer


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: Role
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
