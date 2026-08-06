import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import TimestampMixin, UUIDMixin


class WebhookEventType:
    PROJECT_CREATED: str = "project.created"
    PROJECT_UPDATED: str = "project.updated"
    PROJECT_ARCHIVED: str = "project.archived"
    PROJECT_DELETED: str = "project.deleted"
    TASK_CREATED: str = "task.created"
    TASK_UPDATED: str = "task.updated"
    TASK_COMPLETED: str = "task.completed"
    TASK_DELETED: str = "task.deleted"
    TASK_ASSIGNED: str = "task.assigned"
    COMMENT_CREATED: str = "comment.created"
    COMMENT_DELETED: str = "comment.deleted"
    MEMBER_ADDED: str = "member.added"
    MEMBER_REMOVED: str = "member.removed"


WEBHOOK_EVENT_TYPES = (
    WebhookEventType.PROJECT_CREATED,
    WebhookEventType.PROJECT_UPDATED,
    WebhookEventType.PROJECT_ARCHIVED,
    WebhookEventType.PROJECT_DELETED,
    WebhookEventType.TASK_CREATED,
    WebhookEventType.TASK_UPDATED,
    WebhookEventType.TASK_COMPLETED,
    WebhookEventType.TASK_DELETED,
    WebhookEventType.TASK_ASSIGNED,
    WebhookEventType.COMMENT_CREATED,
    WebhookEventType.COMMENT_DELETED,
    WebhookEventType.MEMBER_ADDED,
    WebhookEventType.MEMBER_REMOVED,
)


class WebhookBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    url: str = Field(max_length=512)
    events: list[str] = Field(default=[], sa_type=JSON)
    is_active: bool = Field(default=True, index=True)
    secret: str | None = Field(default=None, max_length=255)
    metadata_: dict[str, Any] | None = Field(default=None, sa_type=JSON)


class WebhookCreate(WebhookBase):
    project_id: uuid.UUID | None = None


class WebhookUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    url: str | None = Field(default=None, max_length=512)
    events: list[str] | None = None
    is_active: bool | None = None
    secret: str | None = Field(default=None, max_length=255)


class Webhook(TimestampMixin, UUIDMixin, WebhookBase, table=True):
    __tablename__ = "webhook"

    project_id: uuid.UUID | None = Field(foreign_key="project.id", nullable=True, index=True)

    project: Optional["Project"] = Relationship(back_populates="webhooks")


class WebhookPublic(WebhookBase):
    id: uuid.UUID
    project_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    last_triggered_at: datetime | None = None
    success_count: int = 0
    failure_count: int = 0


class WebhooksPublic(SQLModel):
    data: list[WebhookPublic]
    count: int
