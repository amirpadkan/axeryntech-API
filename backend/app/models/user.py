import uuid
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import TimestampMixin, UUIDMixin

RoleEnum = ("admin", "manager", "member")
ThemeEnum = ("light", "dark", "system")
LanguageEnum = ("en", "es", "fr", "de", "pt", "ja", "zh")


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = Field(default=None, max_length=512)
    language: str = Field(default="en", max_length=10)
    timezone: str = Field(default="UTC", max_length=50)
    theme: str = Field(default="system", max_length=20)
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    role: str = Field(default="member", max_length=50)
    last_login: datetime | None = Field(default=None)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None
    full_name: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=500)
    role: str | None = Field(default=None, max_length=50)
    avatar_url: str | None = Field(default=None, max_length=512)
    language: str | None = Field(default=None, max_length=10)
    timezone: str | None = Field(default=None, max_length=50)
    theme: str | None = Field(default=None, max_length=20)
    last_login: datetime | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=500)
    language: str | None = Field(default=None, max_length=10)
    timezone: str | None = Field(default=None, max_length=50)
    theme: str | None = Field(default=None, max_length=20)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class User(TimestampMixin, UUIDMixin, UserBase, table=True):
    __tablename__ = "user"  # type: ignore[assignment]

    hashed_password: str

    owned_projects: list["Project"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"foreign_keys": "Project.owner_id"},
    )
    memberships: list["ProjectMember"] = Relationship(back_populates="user")
    assigned_tasks: list["Task"] = Relationship(
        back_populates="assignee",
        sa_relationship_kwargs={"foreign_keys": "Task.assignee_id"},
    )
    created_tasks: list["Task"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "Task.created_by_id"},
    )
    updated_tasks: list["Task"] = Relationship(
        back_populates="updater",
        sa_relationship_kwargs={"foreign_keys": "Task.updated_by_id"},
    )
    comments: list["Comment"] = Relationship(back_populates="author")
    notifications: list["Notification"] = Relationship(back_populates="recipient")
    activities: list["ActivityLog"] = Relationship(back_populates="actor")
    sessions: list["UserSession"] = Relationship(back_populates="user")
    created_templates: list["ProjectTemplate"] = Relationship(back_populates="created_by_user")

    @property
    def projects(self) -> list["Project"]:
        return [m.project for m in self.memberships if m.project and not m.project.deleted_at]


class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int
