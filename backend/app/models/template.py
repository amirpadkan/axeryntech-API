import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import TimestampMixin, UUIDMixin


class ProjectTemplate(TimestampMixin, UUIDMixin, table=True):
    __tablename__ = "project_template"

    name: str = Field(min_length=1, max_length=255, index=True)
    description: str | None = Field(default=None, max_length=2000)
    tasks: list[dict[str, Any]] = Field(default=[], sa_type=JSON)
    labels: list[dict[str, Any]] = Field(default=[], sa_type=JSON)
    is_default: bool = Field(default=False, index=True)
    created_by_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)

    created_by_user: "User" = Relationship(back_populates="created_templates")


class ProjectTemplateBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    tasks: list[dict[str, Any]] = []
    labels: list[dict[str, Any]] = []
    is_default: bool = False


class ProjectTemplateCreate(ProjectTemplateBase):
    pass


class ProjectTemplateUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    tasks: list[dict[str, Any]] | None = None
    labels: list[dict[str, Any]] | None = None
    is_default: bool | None = None


class ProjectTemplatePublic(ProjectTemplateBase):
    id: uuid.UUID
    created_by_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ProjectTemplatesPublic(SQLModel):
    data: list[ProjectTemplatePublic]
    count: int
