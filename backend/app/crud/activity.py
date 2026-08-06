import uuid

from sqlmodel import Session, col, func, select

from app.models import ActivityLog, ActivityLogCreate
from app.crud.base import CRUDBase

activity_crud = CRUDBase[ActivityLog, ActivityLogCreate, ActivityLog](ActivityLog)


def log_activity(
    session: Session,
    *,
    actor_id: uuid.UUID,
    action: str,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    metadata_: dict | None = None,
) -> ActivityLog:
    db_activity = ActivityLog(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_=metadata_,
    )
    session.add(db_activity)
    session.commit()
    session.refresh(db_activity)
    return db_activity


def get_activities(
    session: Session,
    *,
    actor_id: uuid.UUID | None = None,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[ActivityLog], int]:
    count_statement = select(func.count()).select_from(ActivityLog)
    statement = select(ActivityLog)
    if actor_id:
        count_statement = count_statement.where(ActivityLog.actor_id == actor_id)
        statement = statement.where(ActivityLog.actor_id == actor_id)
    if entity_type:
        count_statement = count_statement.where(ActivityLog.entity_type == entity_type)
        statement = statement.where(ActivityLog.entity_type == entity_type)
    if entity_id:
        count_statement = count_statement.where(ActivityLog.entity_id == entity_id)
        statement = statement.where(ActivityLog.entity_id == entity_id)
    count = session.exec(count_statement).one()
    statement = statement.order_by(col(ActivityLog.created_at).desc()).offset(skip).limit(limit)
    return list(session.exec(statement).all()), count
