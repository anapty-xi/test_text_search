import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(
        examples=["550e8400-e29b-41d4-a716-446655440000"], description="Post uuid"
    )
    rubrics: list[str] = Field(
        examples=[["cars", "animals"]],
        description="List of rubrics that describes post",
    )
    text: str = Field(
        examples=[
            "Слив информации на пассивки: • Булл (Блокировка боли) • Джесси (Массовый шок) • Поко (Звукотерапия) • Дэррил (Перезарядка на ходу) • Карл (Разгром) • Биби (Липкая жвачка и Полная готовность) • Мортис (Свернувшаяся змея и Неуловимый) • Леон (Тайное лекарство) • Ворон (Стервятник) • Джин (Рука помощи) Включай уведомления чтобы не пропускать много полезной информации! ✅"
        ],
        description="Post text",
    )
    created_date: datetime = Field(
        examples=["2019-07-25 12:42:13"], description="Post created date"
    )
