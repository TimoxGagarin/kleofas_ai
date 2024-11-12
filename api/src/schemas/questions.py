from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateQuestion(BaseModel):
    text: str
    is_correct: bool = False


class DisplayQuestion(BaseModel):
    id: int
    text: str
    is_correct: bool
    test_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
