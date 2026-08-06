import uuid
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlmodel import Session, and_, col, or_, select

from app.models import Task, TaskCreate, TaskUpdate, TaskStatus, TaskPriority, Label
from app.crud.base import CRUDBase, get_or_404

task_crud = CRUDBase[Task, TaskCreate, TaskUpdate](Task)


def _apply_task_filters(
    statement,
    *,
    status: str | None = None,
    priority: str | None = None,
    project_id: uuid.UUID | None = None,
    assignee_id: uuid.UUID | None = None,
    due_before: datetime | None = None,
    due_after: datetime | None = None,
    keyword: str | None = None,
):
    if status:
        statement = statement.where(Task.status == status)
    if priority:
        statement = statement.where(Task.priority == priority)
    if project_id:
        statement = statement.where(Task.project_id == project_id)
    if assignee_id:
        statement = statement.where(Task.assignee_id == assignee_id)
    if due_before:
        statement = statement.where(Task.due_date <= due_before)  # type: ignore[attr-defined]
    if due_after:
        statement = statement.where(Task.due_date >= due_after)  # type: ignore[attr-defined]
    if keyword:
        like = f"%{keyword}%"
        statement = statement.where(or_(Task.title.like(like), Task.description.like(like)))
    return statement


def create_task(session: Session, task_in: TaskCreate, created_by_id: uuid.UUID, project_id: uuid.UUID) -> Task:
    db_task = Task.model_validate(
        task_in,
        update={
            "project_id": project_id,
            "created_by_id": created_by_id,
            "updated_by_id": created_by_id,
        },
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    if task_in.label_ids:
        _set_task_labels(session, db_task.id, task_in.label_ids)
        session.refresh(db_task)
    return db_task


def _set_task_labels(session: Session, task_id: uuid.UUID, label_ids: list[uuid.UUID]) -> None:
    from app.models.task import TaskLabelLink
    for lid in label_ids:
        link = TaskLabelLink(task_id=task_id, label_id=lid)
        session.merge(link)


def update_task(session: Session, db_task: Task, task_in: TaskUpdate, updated_by_id: uuid.UUID) -> Task:
    update_data = task_in.model_dump(exclude_unset=True)
    label_ids = update_data.pop("label_ids", None)
    update_data["updated_by_id"] = updated_by_id
    if task_in.status == TaskStatus.DONE and db_task.status != TaskStatus.DONE:
        update_data["completed_at"] = datetime.now(UTC)
    elif task_in.status and task_in.status != TaskStatus.DONE:
        update_data["completed_at"] = None
    db_task.sqlmodel_update(update_data)
    session.add(db_task)
    if label_ids is not None:
        _set_task_labels(session, db_task.id, label_ids)
    session.commit()
    session.refresh(db_task)
    return db_task


def get_task_with_labels(session: Session, task_id: uuid.UUID) -> Task | None:
    task = task_crud.get_active(session, task_id)
    return task
