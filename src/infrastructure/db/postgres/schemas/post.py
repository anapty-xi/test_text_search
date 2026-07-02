import uuid
from datetime import datetime

from sqlalchemy import ARRAY, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.postgres.engine import Base


class Post(Base):
    """Таблица для постов"""

    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    rubrics: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    created_date: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
    )
