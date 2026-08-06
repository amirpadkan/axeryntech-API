import uuid
from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from fastapi import HTTPException
from sqlmodel import Session, SQLModel, col, select

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    def get(self, session: Session, id: uuid.UUID) -> ModelType | None:
        return session.get(self.model, id)

    def get_active(self, session: Session, id: uuid.UUID) -> ModelType | None:
        statement = (
            select(self.model)
            .where(self.model.id == id)  # type: ignore[attr-defined]
            .where(self.model.deleted_at == None)  # type: ignore[attr-defined]
        )
        return session.exec(statement).first()

    def get_multi(
        self,
        session: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Any = None,
    ) -> tuple[list[ModelType], int]:
        count_statement = (
            select(__import__("sqlmodel").func.count())
            .select_from(self.model)
            .where(self.model.deleted_at == None)  # type: ignore[attr-defined]
        )
        count = session.exec(count_statement).one()
        statement = (
            select(self.model)
            .where(self.model.deleted_at == None)  # type: ignore[attr-defined]
            .offset(skip)
            .limit(limit)
        )
        if order_by is not None:
            statement = statement.order_by(order_by)
        return list(session.exec(statement).all()), count

    def create(self, session: Session, *, obj_in: CreateSchemaType, **kwargs: Any) -> ModelType:
        db_obj = self.model.model_validate(obj_in, update=kwargs)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(
        self,
        session: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(UTC)
        db_obj.sqlmodel_update(update_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def soft_delete(self, session: Session, *, id: uuid.UUID) -> ModelType | None:
        obj = session.get(self.model, id)
        if not obj:
            return None
        obj.deleted_at = datetime.now(UTC)  # type: ignore[attr-defined]
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def hard_delete(self, session: Session, *, id: uuid.UUID) -> None:
        obj = session.get(self.model, id)
        if obj:
            session.delete(obj)
            session.commit()


def get_or_404(crud: CRUDBase[Any, Any, Any], session: Session, id: uuid.UUID) -> Any:
    obj = crud.get_active(session, id)
    if not obj:
        raise HTTPException(status_code=404, detail=f"{crud.model.__name__} not found")
    return obj
