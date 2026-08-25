from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """
    Pydantic Schema for Authentication Token response.
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Pydantic Schema for parsed JWT token payload.
    """
    sub: Optional[str] = None
