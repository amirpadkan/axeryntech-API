import uuid

from sqlmodel import Session, col, func, select

from app.models import Notification, NotificationCreate
from app.crud.base import CRUDBase

notification_crud = CRUDBase[Notification, NotificationCreate, Notification](Notification)


def create_notification(session: Session, notif_in: NotificationCreate) -> Notification:
    db_notif = Notification.model_validate(notif_in)
    session.add(db_notif)
    session.commit()
    session.refresh(db_notif)
    return db_notif


def get_user_notifications(
    session: Session,
    user_id: uuid.UUID,
    *,
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Notification], int]:
    count_statement = select(func.count()).select_from(Notification).where(
        Notification.recipient_id == user_id,
        Notification.deleted_at == None,
    )
    if unread_only:
        count_statement = count_statement.where(Notification.is_read == False)  # noqa: E712
    count = session.exec(count_statement).one()
    statement = select(Notification).where(
        Notification.recipient_id == user_id,
        Notification.deleted_at == None,
    )
    if unread_only:
        statement = statement.where(Notification.is_read == False)  # noqa: E712
    statement = statement.order_by(col(Notification.created_at).desc()).offset(skip).limit(limit)
    return list(session.exec(statement).all()), count


def mark_as_read(
    session: Session,
    notification_id: uuid.UUID | None,
    user_id: uuid.UUID,
    *,
    mark_all: bool = False,
) -> int:
    updated = 0
    if mark_all:
        notifs = session.exec(
            select(Notification).where(
                Notification.recipient_id == user_id,
                Notification.is_read == False,  # noqa: E712
                Notification.deleted_at == None,
            )
        ).all()
        for n in notifs:
            n.is_read = True
            session.add(n)
        updated = len(notifs)
    elif notification_id:
        notif = session.exec(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.recipient_id == user_id,
            )
        ).first()
        if notif:
            notif.is_read = True
            session.add(notif)
            updated = 1
    session.commit()
    return updated


def get_unread_count(session: Session, user_id: uuid.UUID) -> int:
    statement = (
        select(func.count())
        .select_from(Notification)
        .where(
            Notification.recipient_id == user_id,
            Notification.is_read == False,  # noqa: E712
            Notification.deleted_at == None,
        )
    )
    return session.exec(statement).one()
