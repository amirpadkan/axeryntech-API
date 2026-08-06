import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import LabelCreate, LabelPublic, LabelUpdate

router = APIRouter(prefix="/projects/{project_id}/labels", tags=["labels"])


@router.get("/")
def list_labels(
    project_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """List labels in a project."""
    crud.project.get_project(session, project_id, current_user)
    labels = crud.label.get_project_labels(session, project_id)
    return {"data": [LabelPublic.model_validate(l) for l in labels], "count": len(labels)}


@router.post("/", response_model=LabelPublic)
def create_label(
    project_id: uuid.UUID,
    label_in: LabelCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Create a label in a project."""
    crud.project.get_project(session, project_id, current_user)
    label = crud.label.create_label(session, label_in, project_id)
    return LabelPublic.model_validate(label)


@router.patch("/{label_id}", response_model=LabelPublic)
def update_label(
    project_id: uuid.UUID,
    label_id: uuid.UUID,
    label_in: LabelUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Update a label."""
    crud.project.get_project(session, project_id, current_user)
    label = crud.label.label_crud.get_active(session, label_id)
    if not label or label.project_id != project_id:
        raise HTTPException(status_code=404, detail="Label not found")
    updated = crud.label.label_crud.update(session, db_obj=label, obj_in=label_in)
    return LabelPublic.model_validate(updated)


@router.delete("/{label_id}")
def delete_label(
    project_id: uuid.UUID,
    label_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Soft-delete a label."""
    crud.project.get_project(session, project_id, current_user)
    label = crud.label.label_crud.get_active(session, label_id)
    if not label or label.project_id != project_id:
        raise HTTPException(status_code=404, detail="Label not found")
    crud.label.label_crud.soft_delete(session, id=label_id)
    from app.schemas import Message
    return Message(message="Label deleted successfully")
