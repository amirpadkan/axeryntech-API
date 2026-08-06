from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Project, Task, TaskStatus, User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/")
def get_dashboard(session: SessionDep, current_user: CurrentUser) -> Any:
    """Get dashboard statistics for the current user."""
    from app.models import ProjectMember
    project_ids_subquery = (
        select(ProjectMember.project_id)
        .where(ProjectMember.user_id == current_user.id)
    )
    project_count = session.exec(
        select(func.count()).select_from(Project).where(
            Project.deleted_at == None,
            Project.id.in_(project_ids_subquery),
        )
    ).one()

    task_count = session.exec(
        select(func.count()).select_from(Task).where(
            Task.deleted_at == None,
            Task.project_id.in_(project_ids_subquery),
        )
    ).one()
    completed_count = session.exec(
        select(func.count()).select_from(Task).where(
            Task.deleted_at == None,
            Task.status == TaskStatus.DONE,
            Task.project_id.in_(project_ids_subquery),
        )
    ).one()
    pending_count = task_count - completed_count
    today = date.today()
    overdue_count = session.exec(
        select(func.count()).select_from(Task).where(
            Task.deleted_at == None,
            Task.status != TaskStatus.DONE,
            Task.due_date < today,
            Task.project_id.in_(project_ids_subquery),
        )
    ).one()
    completion_rate = round((completed_count / task_count) * 100, 1) if task_count > 0 else 0.0
    active_users = session.exec(
        select(func.count()).select_from(User).where(
            User.is_active == True,
            User.deleted_at == None,
        )
    ).one()
    tasks_per_project = []
    if not current_user.is_superuser:
        from sqlmodel import col
        projects = session.exec(
            select(Project).where(
                Project.deleted_at == None,
                Project.id.in_(project_ids_subquery),
            ).order_by(col(Project.name).asc())
        ).all()
        for p in projects:
            tc = session.exec(
                select(func.count()).select_from(Task).where(
                    Task.deleted_at == None,
                    Task.project_id == p.id,
                )
            ).one()
            tasks_per_project.append({"project_id": str(p.id), "name": p.name, "task_count": tc})
    return {
        "total_projects": project_count,
        "total_tasks": task_count,
        "completed_tasks": completed_count,
        "pending_tasks": pending_count,
        "overdue_tasks": overdue_count,
        "completion_rate": completion_rate,
        "active_users": active_users,
        "tasks_per_project": tasks_per_project,
    }
