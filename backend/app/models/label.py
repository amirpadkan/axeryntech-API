import uuid
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import TimestampMixin, UUIDMixin
from app.models.associations import TaskLabelLink


class LabelBase(SQLModel):
    name: str = Field(min_length=1, max_length=100, index=True)
    color: str = Field(default="#6366f1", max_length=7)


class LabelCreate(LabelBase):
    pass


class LabelUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, max_length=7)


class Label(TimestampMixin, UUIDMixin, LabelBase, table=True):
    __tablename__ = "label"

    project_id: uuid.UUID = Field(foreign_key="project.id", nullable=False, index=True)

    project: "Project" = Relationship(back_populates="labels")
    tasks: list["Task"] = Relationship(back_populates="labels", link_model=TaskLabelLink)


class LabelPublic(LabelBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime


class LabelsPublic(SQLModel):
    data: list[LabelPublic]
    count: int
