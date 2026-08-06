from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session

from app import crud
from app.core import security
from app.core.config import settings
from app.models import User
from app.crud.activity import log_activity


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(UTC)
    expires = now + delta
    return jwt.encode(
        {"exp": expires.timestamp(), "nbf": now.timestamp(), "sub": email},
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        return str(decoded["sub"])
    except InvalidTokenError:
        return None


def generate_email_verification_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_VERIFY_TOKEN_EXPIRE_HOURS)
    now = datetime.now(UTC)
    expires = now + delta
    return jwt.encode(
        {"exp": expires.timestamp(), "nbf": now.timestamp(), "sub": email, "type": "verify"},
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )


def verify_email_token(token: str) -> str | None:
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        if decoded.get("type") != "verify":
            return None
        return str(decoded["sub"])
    except InvalidTokenError:
        return None


def verify_email(session: Session, email: str) -> bool:
    user = crud.user.get_user_by_email(session=session, email=email)
    if not user:
        return False
    user.is_verified = True
    session.add(user)
    session.commit()
    return True


def record_login(session: Session, user: User) -> None:
    log_activity(
        session=session,
        actor_id=user.id,
        action="user_login",
        entity_type="user",
        entity_id=user.id,
    )
