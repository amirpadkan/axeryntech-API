from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.core import security
from app.core.config import settings
from app.models import User, UserCreate, UserPublic, UserRegister, UserUpdate
from app.schemas import Message, Token
from app.schemas import NewPassword, RefreshToken
from app.services.auth import (
    generate_email_verification_token,
    generate_password_reset_token,
    verify_email_token,
    verify_password_reset_token,
)
from app.utils import generate_new_account_email, generate_reset_password_email, send_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """OAuth2 compatible token login, returns access and refresh tokens."""
    user = crud.user.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access = security.create_access_token(user.id, expires_delta=access_token_expires)
    refresh = security.create_refresh_token(user.id)
    return Token(access_token=access, refresh_token=refresh)


@router.post("/refresh-token")
def refresh_access_token(session: SessionDep, body: RefreshToken) -> Token:
    """Exchange a refresh token for a new access token pair."""
    try:
        payload = security.decode_token(body.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if payload.get("type") != security.TOKEN_TYPE_REFRESH:
        raise HTTPException(status_code=401, detail="Invalid token type")
    user = crud.user.get_user_by_id(session=session, user_id=payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access = security.create_access_token(user.id, expires_delta=access_token_expires)
    refresh = security.create_refresh_token(user.id)
    return Token(access_token=access, refresh_token=refresh)


@router.post("/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """Test access token validity."""
    return current_user


@router.post("/register", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """Register a new user account."""
    user = crud.user.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user_create.is_verified = False
    user = crud.user.create_user(session=session, user_create=user_create)
    if settings.emails_enabled and user_in.email:
        verify_token = generate_email_verification_token(user_in.email)
        email_data = generate_new_account_email(
            email_to=user_in.email,
            username=user_in.email,
            password=user_in.password,
            verify_link=f"{settings.FRONTEND_HOST}/verify-email?token={verify_token}",
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.get("/verify-email")
def verify_email(session: SessionDep, token: str) -> Message:
    """Verify a user's email address."""
    email = verify_email_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    user = crud.user.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        return Message(message="Email already verified")
    user.is_verified = True
    session.add(user)
    session.commit()
    return Message(message="Email verified successfully")


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    """Request a password recovery email."""
    user = crud.user.get_user_by_email(session=session, email=email)
    if user:
        password_reset_token = generate_password_reset_token(email=email)
        email_data = generate_reset_password_email(
            email_to=user.email, email=email, token=password_reset_token
        )
        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return Message(
        message="If that email is registered, we sent a password recovery link"
    )


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """Reset password using a recovery token."""
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.user.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    user_in_update = UserUpdate(password=body.new_password)
    crud.user.update_user(session=session, db_user=user, user_in=user_in_update)
    return Message(message="Password updated successfully")
