import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import UUIDMixin


class UserSession(UUIDMixin, table=True):
    __tablename__ = "user_session"

    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    access_token_hash: str = Field(max_length=255, index=True)
    refresh_token_hash: str = Field(max_length=255, index=True)
    device_info: dict[str, Any] | None = Field(default=None, sa_type=JSON)
    ip_address: str | None = Field(default=None, max_length=45)
    user_agent: str | None = Field(default=None, max_length=512)
    is_active: bool = Field(default=True, index=True)
    expires_at: datetime = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(__import__("datetime").UTC))
    last_active_at: datetime | None = None

    user: "User" = Relationship(back_populates="sessions")


class UserSessionPublic(SQLModel):
    id: uuid.UUID
    device_info: dict[str, Any] | None
    ip_address: str | None
    is_active: bool
    created_at: datetime
    last_active_at: datetime | None
    expires_at: datetime


class UserSessionsPublic(SQLModel):
    data: list[UserSessionPublic]
    count: int
