"""Initial TaskPilot schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_index(op.f("ix_user_deleted_at"), "user", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.create_index(op.f("ix_user_id"), "user", ["id"], unique=False)

    op.create_table(
        "activity_log",
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=True),
        sa.Column("entity_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("actor_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_index(op.f("ix_activity_log_action"), "activity_log", ["action"], unique=False)
    op.create_index(op.f("ix_activity_log_actor_id"), "activity_log", ["actor_id"], unique=False)
    op.create_index(op.f("ix_activity_log_entity_id"), "activity_log", ["entity_id"], unique=False)
    op.create_index(op.f("ix_activity_log_id"), "activity_log", ["id"], unique=False)

    op.create_table(
        "project",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("is_archived", sa.Boolean(), nullable=False),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("owner_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"]),
    )
    op.create_index(op.f("ix_project_deleted_at"), "project", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_project_id"), "project", ["id"], unique=False)
    op.create_index(op.f("ix_project_is_archived"), "project", ["is_archived"], unique=False)
    op.create_index(op.f("ix_project_name"), "project", ["name"], unique=False)
    op.create_index(op.f("ix_project_owner_id"), "project", ["owner_id"], unique=False)
    op.create_index(op.f("ix_project_status"), "project", ["status"], unique=False)

    op.create_table(
        "notification",
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.String(length=1000), nullable=True),
        sa.Column("resource_type", sa.String(length=50), nullable=True),
        sa.Column("resource_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("recipient_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.ForeignKeyConstraint(["recipient_id"], ["user.id"]),
    )
    op.create_index(op.f("ix_notification_deleted_at"), "notification", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_notification_id"), "notification", ["id"], unique=False)
    op.create_index(op.f("ix_notification_is_read"), "notification", ["is_read"], unique=False)
    op.create_index(op.f("ix_notification_recipient_id"), "notification", ["recipient_id"], unique=False)
    op.create_index(op.f("ix_notification_resource_id"), "notification", ["resource_id"], unique=False)
    op.create_index(op.f("ix_notification_type"), "notification", ["type"], unique=False)

    op.create_table(
        "project_member",
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("project_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
    )
    op.create_index(op.f("ix_project_member_id"), "project_member", ["id"], unique=False)
    op.create_index(op.f("ix_project_member_project_id"), "project_member", ["project_id"], unique=False)
    op.create_index(op.f("ix_project_member_user_id"), "project_member", ["user_id"], unique=False)

    op.create_table(
        "label",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=False),
        sa.Column("project_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
    )
    op.create_index(op.f("ix_label_deleted_at"), "label", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_label_id"), "label", ["id"], unique=False)
    op.create_index(op.f("ix_label_name"), "label", ["name"], unique=False)
    op.create_index(op.f("ix_label_project_id"), "label", ["project_id"], unique=False)

    op.create_table(
        "task",
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=5000), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.String(length=50), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("estimated_hours", sa.Float(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("project_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("assignee_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("created_by_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("updated_by_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.ForeignKeyConstraint(["assignee_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
        sa.ForeignKeyConstraint(["updated_by_id"], ["user.id"]),
    )
    op.create_index(op.f("ix_task_assignee_id"), "task", ["assignee_id"], unique=False)
    op.create_index(op.f("ix_task_created_by_id"), "task", ["created_by_id"], unique=False)
    op.create_index(op.f("ix_task_deleted_at"), "task", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_task_due_date"), "task", ["due_date"], unique=False)
    op.create_index(op.f("ix_task_id"), "task", ["id"], unique=False)
    op.create_index(op.f("ix_task_priority"), "task", ["priority"], unique=False)
    op.create_index(op.f("ix_task_project_id"), "task", ["project_id"], unique=False)
    op.create_index(op.f("ix_task_status"), "task", ["status"], unique=False)
    op.create_index(op.f("ix_task_title"), "task", ["title"], unique=False)

    op.create_table(
        "comment",
        sa.Column("content", sa.String(length=5000), nullable=False),
        sa.Column("task_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("author_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"]),
    )
    op.create_index(op.f("ix_comment_author_id"), "comment", ["author_id"], unique=False)
    op.create_index(op.f("ix_comment_deleted_at"), "comment", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_comment_id"), "comment", ["id"], unique=False)
    op.create_index(op.f("ix_comment_task_id"), "comment", ["task_id"], unique=False)

    op.create_table(
        "task_label_link",
        sa.Column("task_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("label_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.PrimaryKeyConstraint("task_id", "label_id"),
        sa.ForeignKeyConstraint(["label_id"], ["label.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"]),
    )


def downgrade() -> None:
    op.drop_table("task_label_link")
    op.drop_table("comment")
    op.drop_table("task")
    op.drop_table("label")
    op.drop_table("project_member")
    op.drop_table("notification")
    op.drop_table("project")
    op.drop_table("activity_log")
    op.drop_index(op.f("ix_user_id"), table_name="user")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_index(op.f("ix_user_deleted_at"), table_name="user")
    op.drop_table("user")
