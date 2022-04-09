from pydantic import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    TG_TOKEN: str = ""
    DATABASE_URL: str = "sqlite:///app.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
