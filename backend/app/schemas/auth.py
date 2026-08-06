from pydantic import Field
from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshToken(SQLModel):
    refresh_token: str = Field(..., min_length=10)


class TokenPayload(SQLModel):
    sub: str | None = None
    type: str | None = None


class NewPassword(SQLModel):
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8, max_length=128)
