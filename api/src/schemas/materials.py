from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from api.src.schemas.base import Pagination


class CreateMaterial(BaseModel):
    url: str


class DisplayMaterial(BaseModel):
    id: int
    url: str
    message_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchMaterial(Pagination):
    course_id: int | None = None
    user_id: UUID | None = None
