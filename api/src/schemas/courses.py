from datetime import datetime

from pydantic import BaseModel, ConfigDict

from api.src.schemas.base import Pagination


class CreateCourse(BaseModel):
    title: str
    description: str
    default_prompt: str


class UpdateCourse(BaseModel):
    title: str | None = None
    description: str | None = None
    default_prompt: str | None = None


class DisplayCourse(BaseModel):
    id: int
    title: str
    description: str
    default_prompt: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchCourse(Pagination):
    id: int | None = None
    title: str | None = None
