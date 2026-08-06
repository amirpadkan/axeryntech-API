import uuid
from typing import Any

from fastapi import APIRouter, Depends

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import NotificationPublic

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/")
def list_notifications(
    session: SessionDep,
    current_user: CurrentUser,
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 50,
) -> Any:
    """List current user's notifications."""
    notifs, count = crud.notification.get_user_notifications(
        session, current_user.id, unread_only=unread_only, skip=skip, limit=limit
    )
    return {"data": [NotificationPublic.model_validate(n) for n in notifs], "count": count}


@router.get("/unread-count")
def unread_count(session: SessionDep, current_user: CurrentUser) -> Any:
    """Get the count of unread notifications."""
    count = crud.notification.get_unread_count(session, current_user.id)
    return {"unread_count": count}


@router.post("/read")
def mark_read(
    session: SessionDep,
    current_user: CurrentUser,
    notification_id: uuid.UUID | None = None,
    mark_all: bool = False,
) -> Any:
    """Mark notifications as read."""
    updated = crud.notification.mark_as_read(
        session, notification_id, current_user.id, mark_all=mark_all
    )
    return {"updated": updated}
