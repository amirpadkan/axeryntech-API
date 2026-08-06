import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import UUIDMixin


class NotificationType:
    TASK_ASSIGNED: str = "task_assigned"
    TASK_COMPLETED: str = "task_completed"
    TASK_OVERDUE: str = "task_overdue"
    MENTION: str = "mention"
    DEADLINE_NEAR: str = "deadline_near"
    PROJECT_INVITATION: str = "project_invitation"
    PROJECT_MEMBER_REMOVED: str = "project_member_removed"
    TASK_STATUS_CHANGED: str = "task_status_changed"
    COMMENT_ADDED: str = "comment_added"


NOTIFICATION_TYPES = (
    NotificationType.TASK_ASSIGNED,
    NotificationType.TASK_COMPLETED,
    NotificationType.TASK_OVERDUE,
    NotificationType.MENTION,
    NotificationType.DEADLINE_NEAR,
    NotificationType.PROJECT_INVITATION,
    NotificationType.PROJECT_MEMBER_REMOVED,
    NotificationType.TASK_STATUS_CHANGED,
    NotificationType.COMMENT_ADDED,
)


class NotificationBase(SQLModel):
    type: str = Field(max_length=50, index=True)
    title: str = Field(max_length=255)
    content: str | None = Field(default=None, max_length=1000)
    is_read: bool = Field(default=False, index=True)
    link: str | None = Field(default=None, max_length=512)
    metadata_: dict[str, Any] | None = Field(default=None, sa_type=JSON)


class NotificationCreate(NotificationBase):
    pass


class Notification(UUIDMixin, NotificationBase, table=True):
    __tablename__ = "notification"

    recipient_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(__import__("datetime").UTC))

    recipient: "User" = Relationship(back_populates="notifications")


class NotificationPublic(NotificationBase):
    id: uuid.UUID
    recipient_id: uuid.UUID
    created_at: datetime


class NotificationsPublic(SQLModel):
    data: list[NotificationPublic]
    count: int
