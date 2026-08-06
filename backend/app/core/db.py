from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.models import User, UserCreate
from app.core.security import get_password_hash

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    from app.models import SQLModel
    SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            is_verified=True,
        )
        user = User.model_validate(
            user_in, update={"hashed_password": get_password_hash(user_in.password)}
        )
        session.add(user)
        session.commit()
