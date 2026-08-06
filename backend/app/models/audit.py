import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import UUIDMixin


class AuditLogBase(SQLModel):
    action: str = Field(max_length=100, index=True)
    resource_type: str = Field(max_length=50, index=True)
    resource_id: uuid.UUID | None = Field(default=None, index=True)
    previous_value: dict[str, Any] | None = Field(default=None, sa_type=JSON)
    new_value: dict[str, Any] | None = Field(default=None, sa_type=JSON)
    metadata_: dict[str, Any] | None = Field(default=None, sa_type=JSON)
    ip_address: str | None = Field(default=None, max_length=45)


class AuditLog(UUIDMixin, AuditLogBase, table=True):
    __tablename__ = "audit_log"

    user_id: uuid.UUID | None = Field(foreign_key="user.id", nullable=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(__import__("datetime").UTC))

    user: Optional["User"] = Relationship()


class AuditLogPublic(AuditLogBase):
    id: uuid.UUID
    user_id: uuid.UUID | None
    user_name: str | None = None
    created_at: datetime


class AuditLogsPublic(SQLModel):
    data: list[AuditLogPublic]
    count: int
