import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import UUIDMixin


class ActivityAction:
    TASK_CREATED: str = "task_created"
    TASK_UPDATED: str = "task_updated"
    TASK_DELETED: str = "task_deleted"
    TASK_COMPLETED: str = "task_completed"
    TASK_REOPENED: str = "task_reopened"
    TASK_ASSIGNED: str = "task_assigned"
    PROJECT_CREATED: str = "project_created"
    PROJECT_ARCHIVED: str = "project_archived"
    PROJECT_UPDATED: str = "project_updated"
    USER_LOGIN: str = "user_login"
    USER_LOGOUT: str = "user_logout"
    PASSWORD_CHANGED: str = "password_changed"
    USER_INVITED: str = "user_invited"
    USER_REMOVED: str = "user_removed"
    COMMENT_ADDED: str = "comment_added"
    COMMENT_UPDATED: str = "comment_updated"
    COMMENT_DELETED: str = "comment_deleted"
    LABEL_CREATED: str = "label_created"
    LABEL_UPDATED: str = "label_updated"
    LABEL_DELETED: str = "label_deleted"


ACTIVITY_ACTIONS = (
    ActivityAction.TASK_CREATED,
    ActivityAction.TASK_UPDATED,
    ActivityAction.TASK_DELETED,
    ActivityAction.TASK_COMPLETED,
    ActivityAction.TASK_REOPENED,
    ActivityAction.TASK_ASSIGNED,
    ActivityAction.PROJECT_CREATED,
    ActivityAction.PROJECT_ARCHIVED,
    ActivityAction.PROJECT_UPDATED,
    ActivityAction.USER_LOGIN,
    ActivityAction.USER_LOGOUT,
    ActivityAction.PASSWORD_CHANGED,
    ActivityAction.USER_INVITED,
    ActivityAction.USER_REMOVED,
    ActivityAction.COMMENT_ADDED,
    ActivityAction.COMMENT_UPDATED,
    ActivityAction.COMMENT_DELETED,
    ActivityAction.LABEL_CREATED,
    ActivityAction.LABEL_UPDATED,
    ActivityAction.LABEL_DELETED,
)


class ActivityLogBase(SQLModel):
    action: str = Field(max_length=100, index=True)
    entity_type: str | None = Field(default=None, max_length=50)
    entity_id: uuid.UUID | None = Field(default=None, index=True)
    changes: dict[str, Any] | None = Field(default=None, sa_type=JSON)
    ip_address: str | None = Field(default=None, max_length=45)
    user_agent: str | None = Field(default=None, max_length=512)


class ActivityLogCreate(ActivityLogBase):
    pass


class ActivityLog(UUIDMixin, ActivityLogBase, table=True):
    __tablename__ = "activity_log"

    actor_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(__import__("datetime").UTC))

    actor: "User" = Relationship(back_populates="activities")


class ActivityLogPublic(ActivityLogBase):
    id: uuid.UUID
    actor_id: uuid.UUID
    actor_name: str | None = None
    created_at: datetime


class ActivityLogsPublic(SQLModel):
    data: list[ActivityLogPublic]
    count: int
