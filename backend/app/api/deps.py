from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import User
from app.schemas import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/access-token"
)


def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    if token_data.type and token_data.type != security.TOKEN_TYPE_ACCESS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


def require_admin(current_user: CurrentUser) -> User:
    if not current_user.is_superuser and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user


def require_manager(current_user: CurrentUser) -> User:
    if current_user.is_superuser:
        return current_user
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Manager privileges required")
    return current_user


class ProjectPermission:
    def __init__(self, min_role: str | None = None):
        self.min_role = min_role

    def __call__(
        self,
        project_id: str,
        current_user: CurrentUser,
        session: SessionDep,
    ) -> User:
        from app.crud.project import get_project_member_role
        if current_user.is_superuser:
            return current_user
        role = get_project_member_role(session, project_id, current_user.id)
        if role is None:
            raise HTTPException(status_code=403, detail="Not a project member")
        return current_user
