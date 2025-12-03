from __future__ import annotations

from typing import Iterable

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(..., alias="BOT_TOKEN")
    database_url: str = Field(..., alias="DATABASE_URL")
    redis_url: str = Field(..., alias="REDIS_URL")
    default_language: str = Field("ru", alias="DEFAULT_LANGUAGE")
    admin_ids: set[int] = Field(default_factory=set, alias="ADMIN_IDS")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: str | Iterable[int] | None) -> set[int]:
        if value is None or value == "":
            return set()
        if isinstance(value, str):
            return {int(item.strip()) for item in value.split(",") if item.strip().isdigit()}
        return {int(item) for item in value}


def load_settings() -> Settings:
    return Settings()
