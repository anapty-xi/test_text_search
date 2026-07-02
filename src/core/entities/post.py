import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Post(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    rubrics: list[str]
    text: str
    created_date: datetime
