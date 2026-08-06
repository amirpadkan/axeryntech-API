from typing import Any

from fastapi import APIRouter, Depends, Query

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import ActivityLogPublic

router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("/")
def list_activities(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = Query(50, ge=1, le=200),
) -> Any:
    """List activity logs. Admins see all, regular users see their own."""
    actor_id = None if current_user.is_superuser else current_user.id
    activities, count = crud.activity.get_activities(
        session, actor_id=actor_id, skip=skip, limit=limit
    )
    result = []
    for a in activities:
        public = ActivityLogPublic.model_validate(a)
        if a.actor:
            public.actor_name = a.actor.full_name or a.actor.email
        result.append(public)
    return {"data": result, "count": count}
