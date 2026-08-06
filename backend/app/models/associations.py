import uuid

from sqlmodel import Field, SQLModel


class TaskLabelLink(SQLModel, table=True):
    __tablename__ = "task_label_link"

    task_id: uuid.UUID = Field(foreign_key="task.id", primary_key=True)
    label_id: uuid.UUID = Field(foreign_key="label.id", primary_key=True)
