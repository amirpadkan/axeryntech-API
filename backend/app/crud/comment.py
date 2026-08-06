import uuid

from sqlmodel import Session, col, select

from app.models import Comment, CommentCreate, CommentUpdate
from app.crud.base import CRUDBase

comment_crud = CRUDBase[Comment, CommentCreate, CommentUpdate](Comment)


def create_comment(session: Session, comment_in: CommentCreate, task_id: uuid.UUID, author_id: uuid.UUID) -> Comment:
    db_comment = Comment.model_validate(
        comment_in, update={"task_id": task_id, "author_id": author_id}
    )
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment


def get_task_comments(session: Session, task_id: uuid.UUID) -> tuple[list[Comment], int]:
    from sqlmodel import func
    count_statement = select(func.count()).select_from(Comment).where(
        Comment.task_id == task_id,
        Comment.deleted_at == None,
    )
    count = session.exec(count_statement).one()
    statement = select(Comment).where(
        Comment.task_id == task_id,
        Comment.deleted_at == None,
    ).order_by(col(Comment.created_at).asc())
    return list(session.exec(statement).all()), count
