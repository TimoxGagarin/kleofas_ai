from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateMaterial(BaseModel):
    url: str


class DisplayMaterial(BaseModel):
    id: int
    url: str
    message_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
