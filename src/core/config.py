from pydantic import Field
from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    DB_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/test_text_search",
    )


class Config(BaseSettings):
    POSTGRES: PostgresSettings = Field(default_factory=PostgresSettings)


config = Config()
