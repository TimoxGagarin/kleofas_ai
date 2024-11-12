from datetime import datetime

from pydantic import BaseModel, ConfigDict

from api.src.db.models import TypeEnum
from api.src.schemas.materials import CreateMaterial, DisplayMaterial
from api.src.schemas.tests import CreateTest, DisplayTest


class CreateMessage(BaseModel):
    text: str
    type: TypeEnum
    course_id: int
    test: CreateTest | None = None
    materials: list[CreateMaterial] | None = None


class DisplayMessage(BaseModel):
    id: int
    text: str
    type: TypeEnum
    course_id: int
    user_id: int
    materials: list[DisplayMaterial] | None
    test: DisplayTest | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
