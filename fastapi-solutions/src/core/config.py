import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dotenv import load_dotenv

from logging import config as logging_config
from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    """Конфигурация проекта"""

    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "movies")

    REDIS_HOST: str = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_USER: str = os.getenv("REDIS_USER", "app")
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD")
    CACHE_EXPIRE_IN_SECONDS: int = int(os.getenv("CACHE_EXPIRE_IN_SECONDS", 300))

    ELASTIC_HOST: str = os.getenv("ELASTIC_HOST", "127.0.0.1")
    ELASTIC_PORT: int = int(os.getenv("ELASTIC_PORT", 9200))

    PAGE_SIZE: int = int(os.getenv("PAGE_SIZE", 10))
    PAGE_NUMBER: int = int(os.getenv("PAGE_NUMBER", 1))

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env"
    )


@lru_cache
def get_settings():
    load_dotenv()
    return Settings()


config = get_settings()
