import uuid
from datetime import date, datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import TimestampMixin, UUIDMixin
from app.models.associations import TaskLabelLink

if TYPE_CHECKING:
    from app.models.label import LabelPublic


class TaskStatus:
    TODO: str = "todo"
    IN_PROGRESS: str = "in_progress"
    REVIEW: str = "review"
    DONE: str = "done"
    BLOCKED: str = "blocked"
    BACKLOG: str = "backlog"


TASK_STATUSES = (
    TaskStatus.TODO,
    TaskStatus.IN_PROGRESS,
    TaskStatus.REVIEW,
    TaskStatus.DONE,
    TaskStatus.BLOCKED,
    TaskStatus.BACKLOG,
)


class TaskPriority:
    LOW: str = "low"
    MEDIUM: str = "medium"
    HIGH: str = "high"
    URGENT: str = "urgent"
    CRITICAL: str = "critical"


TASK_PRIORITIES = (
    TaskPriority.LOW,
    TaskPriority.MEDIUM,
    TaskPriority.HIGH,
    TaskPriority.URGENT,
    TaskPriority.CRITICAL,
)


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255, index=True)
    description: str | None = Field(default=None, max_length=5000)
    status: str = Field(default=TaskStatus.TODO, max_length=50, index=True)
    priority: str = Field(default=TaskPriority.MEDIUM, max_length=50, index=True)
    due_date: date | None = Field(default=None, index=True)
    estimated_hours: float | None = Field(default=None, ge=0, le=10000)
    completed_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    order_index: int = Field(default=0, index=True)


class TaskCreate(TaskBase):
    assignee_id: uuid.UUID | None = None
    label_ids: list[uuid.UUID] = []
    parent_task_id: uuid.UUID | None = None


class TaskUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    status: str | None = Field(default=None, max_length=50)
    priority: str | None = Field(default=None, max_length=50)
    due_date: date | None = None
    assignee_id: uuid.UUID | None = None
    estimated_hours: float | None = Field(default=None, ge=0, le=10000)
    label_ids: list[uuid.UUID] | None = None
    order_index: int | None = None


class Task(TimestampMixin, UUIDMixin, TaskBase, table=True):
    __tablename__ = "task"

    project_id: uuid.UUID = Field(foreign_key="project.id", nullable=False, index=True)
    assignee_id: uuid.UUID | None = Field(foreign_key="user.id", nullable=True, index=True)
    created_by_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    updated_by_id: uuid.UUID | None = Field(foreign_key="user.id", nullable=True)
    parent_task_id: uuid.UUID | None = Field(foreign_key="task.id", nullable=True, index=True)

    project: "Project" = Relationship(back_populates="tasks")
    assignee: "User" = Relationship(
        back_populates="assigned_tasks",
        sa_relationship_kwargs={"foreign_keys": "Task.assignee_id"},
    )
    creator: "User" = Relationship(
        back_populates="created_tasks",
        sa_relationship_kwargs={"foreign_keys": "Task.created_by_id"},
    )
    updater: "User" = Relationship(
        back_populates="updated_tasks",
        sa_relationship_kwargs={"foreign_keys": "Task.updated_by_id"},
    )
    parent_task: Optional["Task"] = Relationship(
        back_populates="subtasks",
        sa_relationship_kwargs={"remote_side": "Task.id"},
    )
    subtasks: list["Task"] = Relationship(back_populates="parent_task", cascade_delete=True)
    comments: list["Comment"] = Relationship(back_populates="task", cascade_delete=True)
    labels: list["Label"] = Relationship(back_populates="tasks", link_model=TaskLabelLink)


class TaskPublic(TaskBase):
    id: uuid.UUID
    project_id: uuid.UUID
    assignee_id: uuid.UUID | None
    created_by_id: uuid.UUID
    updated_by_id: uuid.UUID | None
    parent_task_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    labels: list = []
    comment_count: int = 0


class TasksPublic(SQLModel):
    data: list[TaskPublic]
    count: int
