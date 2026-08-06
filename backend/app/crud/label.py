import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import Label, LabelCreate, LabelUpdate
from app.crud.base import CRUDBase

label_crud = CRUDBase[Label, LabelCreate, LabelUpdate](Label)


def create_label(session: Session, label_in: LabelCreate, project_id: uuid.UUID) -> Label:
    existing = session.exec(
        select(Label).where(
            Label.project_id == project_id,
            Label.name == label_in.name,
            Label.deleted_at == None,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Label with this name already exists in the project")
    db_label = Label.model_validate(label_in, update={"project_id": project_id})
    session.add(db_label)
    session.commit()
    session.refresh(db_label)
    return db_label


def get_project_labels(session: Session, project_id: uuid.UUID) -> list[Label]:
    statement = select(Label).where(
        Label.project_id == project_id,
        Label.deleted_at == None,
    ).order_by(Label.name)
    return list(session.exec(statement).all())
