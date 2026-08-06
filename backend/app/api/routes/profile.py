import shutil
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.models import UserPublic, UserUpdateMe

router = APIRouter(prefix="/profile", tags=["profile"])

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
MAX_BYTES = settings.MAX_AVATAR_SIZE_MB * 1024 * 1024


@router.get("/me", response_model=UserPublic)
def read_profile(current_user: CurrentUser) -> Any:
    """Get the current user's full profile."""
    return current_user


@router.patch("/me", response_model=UserPublic)
def update_profile(
    *, session: SessionDep, full_name: str | None = None, email: str | None = None, current_user: CurrentUser
) -> Any:
    """Update profile information."""
    data = UserUpdateMe(full_name=full_name, email=email)
    if data.email and data.email != current_user.email:
        from app import crud
        existing = crud.user.get_user_by_email(session=session, email=data.email)
        if existing:
            raise HTTPException(status_code=409, detail="User with this email already exists")
    current_user.sqlmodel_update(data.model_dump(exclude_unset=True))
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.post("/avatar", response_model=UserPublic)
def upload_avatar(
    *, session: SessionDep, file: UploadFile = File(...), current_user: CurrentUser
) -> Any:
    """Upload a profile avatar image."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image type. Allowed: png, jpeg, webp, gif")
    upload_dir = Path(settings.AVATAR_UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = (file.filename or "").rsplit(".", 1)[-1].lower() if file.filename else "png"
    if ext not in ("png", "jpg", "jpeg", "webp", "gif"):
        ext = "png"
    filename = f"{current_user.id}.{ext}"
    dest = upload_dir / filename
    with dest.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    size = dest.stat().st_size
    if size > MAX_BYTES:
        dest.unlink()
        raise HTTPException(status_code=400, detail=f"File too large. Max {settings.MAX_AVATAR_SIZE_MB} MB.")
    current_user.avatar_url = f"/static/avatars/{filename}"
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.get("/avatar/{user_id}")
def get_avatar(user_id: uuid.UUID) -> Any:
    """Serve a user's avatar image."""
    upload_dir = Path(settings.AVATAR_UPLOAD_DIR)
    for ext in ("png", "jpg", "jpeg", "webp", "gif"):
        candidate = upload_dir / f"{user_id}.{ext}"
        if candidate.exists():
            media_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"
            return FileResponse(str(candidate), media_type=media_type)
    raise HTTPException(status_code=404, detail="Avatar not found")
