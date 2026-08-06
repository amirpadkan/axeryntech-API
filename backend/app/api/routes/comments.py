import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import Comment, CommentCreate, CommentPublic, CommentUpdate, CommentsPublic

router = APIRouter(prefix="/tasks/{task_id}/comments", tags=["comments"])


def _to_public(comment: Comment) -> CommentPublic:
    public = CommentPublic.model_validate(comment)
    if comment.author:
        public.author_name = comment.author.full_name or comment.author.email
        public.author_avatar = comment.author.avatar_url
    return public


@router.get("/")
def list_comments(
    task_id: uuid.UUID, session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 50
) -> Any:
    """List comments for a task."""
    task = crud.task.task_crud.get_active(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.project.get_project(session, task.project_id, current_user)
    comments, count = crud.comment.get_task_comments(session, task_id)
    return {
        "data": [_to_public(c) for c in comments],
        "count": count,
    }


@router.post("/", response_model=CommentPublic)
def create_comment(
    task_id: uuid.UUID,
    comment_in: CommentCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Add a comment to a task."""
    task = crud.task.task_crud.get_active(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.project.get_project(session, task.project_id, current_user)
    comment = crud.comment.create_comment(session, comment_in, task_id, current_user.id)
    session.refresh(comment)
    return _to_public(comment)


@router.patch("/{comment_id}", response_model=CommentPublic)
def update_comment(
    task_id: uuid.UUID,
    comment_id: uuid.UUID,
    comment_in: CommentUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Update a comment. Author only."""
    comment = crud.comment.comment_crud.get_active(session, comment_id)
    if not comment or comment.task_id != task_id:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    updated = crud.comment.comment_crud.update(session, db_obj=comment, obj_in=comment_in)
    session.refresh(updated)
    return _to_public(updated)


@router.delete("/{comment_id}")
def delete_comment(
    task_id: uuid.UUID,
    comment_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Soft-delete a comment."""
    comment = crud.comment.comment_crud.get_active(session, comment_id)
    if not comment or comment.task_id != task_id:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.comment.comment_crud.soft_delete(session, id=comment_id)
    from app.schemas import Message
    return Message(message="Comment deleted successfully")
