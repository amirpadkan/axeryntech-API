from sqlmodel import SQLModel


class Message(SQLModel):
    message: str


class PaginatedResponse(SQLModel):
    count: int
    page: int
    page_size: int
