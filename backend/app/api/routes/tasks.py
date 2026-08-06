import uuid
from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import col, func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    LabelPublic, Task, TaskCreate, TaskPriority, TaskPublic, TaskStatus, TaskUpdate, TasksPublic,
)
from app.schemas import Message
from app.services.notifications import notify_task_assigned

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _to_task_public(session, task: Task) -> TaskPublic:
    public = TaskPublic.model_validate(task)
    public.labels = [LabelPublic.model_validate(l) for l in task.labels] if task.labels else []
    public.comment_count = crud.comment.get_task_comments(session, task.id)[1]
    return public


@router.get("/", response_model=TasksPublic)
def list_tasks(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = Query(50, ge=1, le=200),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    project_id: uuid.UUID | None = None,
    assignee_id: uuid.UUID | None = None,
    due_before: date | None = None,
    due_after: date | None = None,
    search: str | None = Query(None, description="Keyword search on title and description"),
    sort_by: str = Query("created_at", pattern="^(created_at|updated_at|due_date|priority|title)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
) -> Any:
    """List tasks with filtering, sorting, and search."""
    count_statement = (
        select(func.count())
        .select_from(Task)
        .where(Task.deleted_at == None)
    )
    statement = select(Task).where(Task.deleted_at == None)
    if status:
        count_statement = count_statement.where(Task.status == status)
        statement = statement.where(Task.status == status)
    if priority:
        count_statement = count_statement.where(Task.priority == priority)
        statement = statement.where(Task.priority == priority)
    if project_id:
        count_statement = count_statement.where(Task.project_id == project_id)
        statement = statement.where(Task.project_id == project_id)
    if assignee_id:
        count_statement = count_statement.where(Task.assignee_id == assignee_id)
        statement = statement.where(Task.assignee_id == assignee_id)
    if due_before:
        count_statement = count_statement.where(Task.due_date <= due_before)
        statement = statement.where(Task.due_date <= due_before)
    if due_after:
        count_statement = count_statement.where(Task.due_date >= due_after)
        statement = statement.where(Task.due_date >= due_after)
    if search:
        like = f"%{search}%"
        count_statement = count_statement.where(
            Task.title.like(like) | Task.description.like(like)
        )
        statement = statement.where(
            Task.title.like(like) | Task.description.like(like)
        )
    count = session.exec(count_statement).one()
    sort_col = {
        "created_at": Task.created_at,
        "updated_at": Task.updated_at,
        "due_date": Task.due_date,
        "priority": Task.priority,
        "title": Task.title,
    }[sort_by]
    order = col(sort_col).desc() if sort_dir == "desc" else col(sort_col).asc()
    if sort_by != "created_at":
        order = order.nullslast() if sort_dir == "desc" else order.nullsfirst()
        statement = statement.order_by(order, col(Task.created_at).desc())
    else:
        statement = statement.order_by(order)
    statement = statement.offset(skip).limit(limit)
    tasks = session.exec(statement).all()
    return TasksPublic(data=[_to_task_public(session, t) for t in tasks], count=count)


@router.post("/", response_model=TaskPublic)
def create_task(
    task_in: TaskCreate,
    project_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Create a task in a project."""
    crud.project.get_project(session, project_id, current_user)
    task = crud.task.create_task(session, task_in, current_user.id, project_id)
    if task.assignee_id and task.assignee_id != current_user.id:
        notify_task_assigned(
            session=session,
            recipient_id=task.assignee_id,
            task_title=task.title,
            task_id=task.id,
        )
    from app.crud.activity import log_activity
    log_activity(
        session=session,
        actor_id=current_user.id,
        action="task_created",
        entity_type="task",
        entity_id=task.id,
        metadata_={"title": task.title, "project_id": str(project_id)},
    )
    session.refresh(task)
    return _to_task_public(session, task)


@router.get("/{task_id}", response_model=TaskPublic)
def get_task(
    task_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """Get a task by ID."""
    task = crud.task.task_crud.get_active(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.project.get_project(session, task.project_id, current_user)
    return _to_task_public(session, task)


@router.patch("/{task_id}", response_model=TaskPublic)
def update_task(
    task_id: uuid.UUID,
    task_in: TaskUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Update a task."""
    task = crud.task.task_crud.get_active(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.project.get_project(session, task.project_id, current_user)
    updated = crud.task.update_task(session, task, task_in, current_user.id)
    action = "task_completed" if updated.status == TaskStatus.DONE and task.status != TaskStatus.DONE else "task_updated"
    from app.crud.activity import log_activity
    log_activity(
        session=session,
        actor_id=current_user.id,
        action=action,
        entity_type="task",
        entity_id=updated.id,
    )
    if task_in.assignee_id and task_in.assignee_id != current_user.id and task_in.assignee_id != task.assignee_id:
        notify_task_assigned(
            session=session,
            recipient_id=task_in.assignee_id,
            task_title=updated.title,
            task_id=updated.id,
        )
    session.refresh(updated)
    return _to_task_public(session, updated)


@router.delete("/{task_id}")
def delete_task(
    task_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Message:
    """Soft-delete a task."""
    task = crud.task.task_crud.get_active(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.project.get_project(session, task.project_id, current_user)
    crud.task.task_crud.soft_delete(session, id=task_id)
    from app.crud.activity import log_activity
    log_activity(
        session=session,
        actor_id=current_user.id,
        action="task_deleted",
        entity_type="task",
        entity_id=task.id,
    )
    return Message(message="Task deleted successfully")
