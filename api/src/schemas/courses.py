from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
