import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import col, func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
    Project, ProjectCreate, ProjectMember, ProjectMemberCreate, ProjectMemberPublic,
    ProjectPublic, ProjectStatus, ProjectUpdate, ProjectsPublic, UserPublic,
)
from app.schemas import Message
from app.services.notifications import notify_project_invitation

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=ProjectsPublic)
def list_projects(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = Query(50, ge=1, le=200),
    status: str | None = Query(None, description="Filter by project status"),
    search: str | None = Query(None, description="Search by name"),
    include_archived: bool = False,
) -> Any:
    """List projects the current user is a member of."""
    from app.models import ProjectMember
    count_statement = (
        select(func.count())
        .select_from(Project)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(
            Project.deleted_at == None,
            ProjectMember.user_id == current_user.id,
        )
    )
    statement = (
        select(Project)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(
            Project.deleted_at == None,
            ProjectMember.user_id == current_user.id,
        )
    )
    if status:
        count_statement = count_statement.where(Project.status == status)
        statement = statement.where(Project.status == status)
    if search:
        like = f"%{search}%"
        count_statement = count_statement.where(Project.name.like(like))
        statement = statement.where(Project.name.like(like))
    if not include_archived:
        count_statement = count_statement.where(Project.is_archived == False)
        statement = statement.where(Project.is_archived == False)
    count = session.exec(count_statement).one()
    statement = statement.order_by(col(Project.updated_at).desc()).offset(skip).limit(limit)
    projects = session.exec(statement).all()
    result = []
    for p in projects:
        project_public = ProjectPublic.model_validate(p)
        project_public.task_count = crud.project.get_project_tasks(session, p.id)[1]
        result.append(project_public)
    return ProjectsPublic(data=result, count=count)


@router.post("/", response_model=ProjectPublic)
def create_project(
    session: SessionDep, project_in: ProjectCreate, current_user: CurrentUser
) -> Any:
    """Create a new project. Creator becomes owner and a member."""
    project = crud.project.project_crud.create(
        session, obj_in=project_in, owner_id=current_user.id
    )
    from datetime import UTC, datetime
    membership = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role="admin",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    session.add(membership)
    session.commit()
    session.refresh(project)
    from app.crud.activity import log_activity
    log_activity(
        session=session,
        actor_id=current_user.id,
        action="project_created",
        entity_type="project",
        entity_id=project.id,
        metadata_={"name": project.name},
    )
    public = ProjectPublic.model_validate(project)
    public.task_count = 0
    return public


@router.get("/{project_id}", response_model=ProjectPublic)
def get_project(
    project_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """Get project details."""
    project = crud.project.get_project(session, project_id, current_user)
    public = ProjectPublic.model_validate(project)
    public.task_count = crud.project.get_project_tasks(session, project.id)[1]
    return public


@router.patch("/{project_id}", response_model=ProjectPublic)
def update_project(
    project_id: uuid.UUID,
    project_in: ProjectUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Update a project. Owner or admin only."""
    project = crud.project.get_project(session, project_id, current_user)
    if not current_user.is_superuser and project.owner_id != current_user.id:
        member_role = crud.project.get_project_member_role(session, project_id, current_user.id)
        if member_role not in ("admin", "manager"):
            raise HTTPException(status_code=403, detail="Not enough permissions")
    updated = crud.project.project_crud.update(session, db_obj=project, obj_in=project_in)
    from app.crud.activity import log_activity
    log_activity(
        session=session,
        actor_id=current_user.id,
        action="project_archived" if project_in.is_archived else "project_updated",
        entity_type="project",
        entity_id=project.id,
    )
    return ProjectPublic.model_validate(updated)


@router.delete("/{project_id}")
def delete_project(
    project_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Message:
    """Soft-delete a project. Owner only."""
    project = crud.project.get_project(session, project_id, current_user)
    if not current_user.is_superuser and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the project owner can delete it")
    crud.project.project_crud.soft_delete(session, id=project_id)
    return Message(message="Project deleted successfully")


@router.get("/{project_id}/members")
def list_members(
    project_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """List project members."""
    crud.project.get_project(session, project_id, current_user)
    statement = (
        select(ProjectMember, User)
        .join(User, User.id == ProjectMember.user_id)
        .where(
            ProjectMember.project_id == project_id,
            User.deleted_at == None,
        )
    )
    rows = session.exec(statement).all()
    result = []
    for member, user in rows:
        pm = ProjectMemberPublic.model_validate(member)
        pm.user_email = user.email
        pm.user_full_name = user.full_name
        result.append(pm)
    return result


@router.post("/{project_id}/members")
def add_member(
    project_id: uuid.UUID,
    member_in: ProjectMemberCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Add a member to the project. Owner or admin only."""
    project = crud.project.get_project(session, project_id, current_user)
    if not current_user.is_superuser and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the project owner can add members")
    target_user = crud.user.get_user_by_id(session=session, user_id=member_in.user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    member = crud.project.add_member(session, project_id, member_in)
    notify_project_invitation(
        session=session,
        recipient_id=target_user.id,
        project_name=project.name,
        project_id=project.id,
        invited_by=current_user.full_name or current_user.email,
    )
    pm = ProjectMemberPublic.model_validate(member)
    pm.user_email = target_user.email
    pm.user_full_name = target_user.full_name
    return pm


@router.delete("/{project_id}/members/{user_id}")
def remove_member(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Message:
    """Remove a member from the project. Owner only."""
    project = crud.project.get_project(session, project_id, current_user)
    if not current_user.is_superuser and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the project owner can remove members")
    crud.project.remove_member(session, project_id, user_id)
    return Message(message="Member removed successfully")
