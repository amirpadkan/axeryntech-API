import uuid
from datetime import date, datetime

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import TimestampMixin, UUIDMixin


class ProjectStatus:
    PLANNING: str = "planning"
    ACTIVE: str = "active"
    ON_HOLD: str = "on_hold"
    COMPLETED: str = "completed"
    ARCHIVED: str = "archived"


PROJECT_STATUSES = (
    ProjectStatus.PLANNING,
    ProjectStatus.ACTIVE,
    ProjectStatus.ON_HOLD,
    ProjectStatus.COMPLETED,
    ProjectStatus.ARCHIVED,
)


class MemberRole:
    ADMIN: str = "admin"
    MANAGER: str = "manager"
    MEMBER: str = "member"
    VIEWER: str = "viewer"


MEMBER_ROLES = (
    MemberRole.ADMIN,
    MemberRole.MANAGER,
    MemberRole.MEMBER,
    MemberRole.VIEWER,
)


class ProjectBase(SQLModel):
    name: str = Field(min_length=1, max_length=255, index=True)
    description: str | None = Field(default=None, max_length=2000)
    status: str = Field(default=ProjectStatus.ACTIVE, max_length=50, index=True)
    is_archived: bool = Field(default=False, index=True)
    deadline: date | None = Field(default=None)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    status: str | None = Field(default=None, max_length=50)
    is_archived: bool | None = None
    deadline: date | None = None


class Project(TimestampMixin, UUIDMixin, ProjectBase, table=True):
    __tablename__ = "project"

    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    owner: "User" = Relationship(back_populates="owned_projects")

    members: list["ProjectMember"] = Relationship(back_populates="project", cascade_delete=True)
    tasks: list["Task"] = Relationship(back_populates="project", cascade_delete=True)
    labels: list["Label"] = Relationship(back_populates="project", cascade_delete=True)
    webhooks: list["Webhook"] = Relationship(back_populates="project", cascade_delete=True)


class ProjectPublic(ProjectBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    task_count: int = 0
    completed_task_count: int = 0
    member_count: int = 0


class ProjectsPublic(SQLModel):
    data: list[ProjectPublic]
    count: int


class ProjectMemberBase(SQLModel):
    role: str = Field(default=MemberRole.MEMBER, max_length=50)


class ProjectMemberCreate(ProjectMemberBase):
    user_id: uuid.UUID


class ProjectMember(TimestampMixin, UUIDMixin, ProjectMemberBase, table=True):
    __tablename__ = "project_member"

    project_id: uuid.UUID = Field(foreign_key="project.id", nullable=False, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)

    project: "Project" = Relationship(back_populates="members")
    user: "User" = Relationship(back_populates="memberships")


class ProjectMemberPublic(ProjectMemberBase):
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    user_email: str | None = None
    user_full_name: str | None = None
    joined_at: datetime | None = None
