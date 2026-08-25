from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """
    Base properties shared across user schemas.
    """
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """
    Properties required to register a new User (POST /users).
    """
    password: str


class UserLogin(BaseModel):
    """
    Properties required to log in (POST /auth/login).
    """
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """
    Properties returned to the client (excludes sensitive hashed_password).
    """
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
