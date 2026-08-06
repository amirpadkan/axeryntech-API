import uuid
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Project, Task
from app.services.csv_export import export_projects_to_csv, export_tasks_to_csv

router = APIRouter(prefix="/exports", tags=["exports"])


@router.get("/projects.csv")
def export_projects(session: SessionDep, current_user: CurrentUser) -> Any:
    """Export all user's projects to CSV."""
    from app.models import ProjectMember
    project_ids_subquery = select(ProjectMember.project_id).where(ProjectMember.user_id == current_user.id)
    projects = session.exec(
        select(Project).where(
            Project.deleted_at == None,
            Project.id.in_(project_ids_subquery),
        )
    ).all()
    csv_data = export_projects_to_csv(list(projects))
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=projects.csv"},
    )


@router.get("/tasks.csv")
def export_tasks(
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID | None = None,
) -> Any:
    """Export tasks to CSV, optionally filtered by project."""
    from app.models import ProjectMember
    project_ids_subquery = select(ProjectMember.project_id).where(ProjectMember.user_id == current_user.id)
    statement = select(Task).where(
        Task.deleted_at == None,
        Task.project_id.in_(project_ids_subquery),
    )
    if project_id:
        statement = statement.where(Task.project_id == project_id)
    tasks = session.exec(statement).all()
    csv_data = export_tasks_to_csv(list(tasks))
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=tasks.csv"},
    )
