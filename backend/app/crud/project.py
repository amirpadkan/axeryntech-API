import uuid

from fastapi import HTTPException
from sqlmodel import Session, col, select

from app.models import Project, ProjectCreate, ProjectMember, ProjectMemberCreate, ProjectUpdate, Task, User
from app.crud.base import CRUDBase, get_or_404

project_crud = CRUDBase[Project, ProjectCreate, ProjectUpdate](Project)
member_crud = CRUDBase[ProjectMember, ProjectMemberCreate, ProjectMember](ProjectMember)


def get_project(session: Session, project_id: uuid.UUID, user: User) -> Project:
    project = project_crud.get_active(session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not user.is_superuser and not is_project_member(session, project_id, user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return project


def is_project_member(session: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    statement = select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
    )
    return session.exec(statement).first() is not None


def get_project_member_role(session: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> str | None:
    statement = select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
    )
    member = session.exec(statement).first()
    return member.role if member else None


def add_member(session: Session, project_id: uuid.UUID, member_data: ProjectMemberCreate) -> ProjectMember:
    existing = session.exec(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == member_data.user_id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="User is already a member of this project")
    member = ProjectMember.model_validate(member_data, update={"project_id": project_id})
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


def remove_member(session: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
    statement = select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
    )
    member = session.exec(statement).first()
    if member:
        session.delete(member)
        session.commit()


def get_project_tasks(session: Session, project_id: uuid.UUID) -> tuple[list[Task], int]:
    from sqlmodel import func
    count_statement = (
        select(func.count()).select_from(Task).where(
            Task.project_id == project_id,
            Task.deleted_at == None,
        )
    )
    count = session.exec(count_statement).one()
    statement = select(Task).where(
        Task.project_id == project_id,
        Task.deleted_at == None,
    ).order_by(col(Task.created_at).desc())
    return list(session.exec(statement).all()), count


def get_member_count(session: Session, project_id: uuid.UUID) -> int:
    from sqlmodel import func
    statement = (
        select(func.count())
        .select_from(ProjectMember)
        .where(ProjectMember.project_id == project_id)
    )
    return session.exec(statement).one()
