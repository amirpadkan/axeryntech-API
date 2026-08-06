import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import TimestampMixin, UUIDMixin


class CommentBase(SQLModel):
    content: str = Field(min_length=1, max_length=5000)


class CommentCreate(CommentBase):
    parent_comment_id: uuid.UUID | None = None


class CommentUpdate(SQLModel):
    content: str = Field(min_length=1, max_length=5000)


class Comment(TimestampMixin, UUIDMixin, CommentBase, table=True):
    __tablename__ = "comment"

    task_id: uuid.UUID = Field(foreign_key="task.id", nullable=False, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    parent_comment_id: uuid.UUID | None = Field(foreign_key="comment.id", nullable=True, index=True)

    task: "Task" = Relationship(back_populates="comments")
    author: "User" = Relationship(back_populates="comments")
    parent_comment: Optional["Comment"] = Relationship(
        back_populates="replies",
        sa_relationship_kwargs={"remote_side": "Comment.id"},
    )
    replies: list["Comment"] = Relationship(back_populates="parent_comment", cascade_delete=True)


class CommentPublic(CommentBase):
    id: uuid.UUID
    task_id: uuid.UUID
    author_id: uuid.UUID
    author_name: str | None = None
    author_avatar: str | None = None
    parent_comment_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    reply_count: int = 0


class CommentsPublic(SQLModel):
    data: list[CommentPublic]
    count: int
