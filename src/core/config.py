from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/test_text_search",
    )


class ElasticSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ELASTIC_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    CLIENT: str = Field(
        default="http://elasticsearch:9200",
    )
    INDEX_NAME: str = Field(
        default="posts",
    )


class Config(BaseSettings):
    POSTGRES: PostgresSettings = Field(default_factory=PostgresSettings)
    ELASTIC: ElasticSettings = Field(default_factory=ElasticSettings)


config = Config()
