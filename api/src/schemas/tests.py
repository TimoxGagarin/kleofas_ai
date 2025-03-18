from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from api.src.schemas.base import Pagination
from api.src.schemas.questions import CreateQuestion, DisplayQuestion


class CreateTest(BaseModel):
    title: str
    questions: list[CreateQuestion]


class DisplayTest(BaseModel):
    id: int
    title: str
    message_id: int
    questions: list[DisplayQuestion]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchTest(Pagination):
    course_id: int | None = None
    user_id: UUID | None = None
