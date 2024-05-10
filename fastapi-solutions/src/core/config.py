from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dotenv import load_dotenv

from logging import config as logging_config
from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    """Конфигурация проекта"""

    PROJECT_NAME: str = "movies"

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_USER: str = "app"
    REDIS_PASSWORD: str
    CACHE_EXPIRE_IN_SECONDS: int = 300

    ELASTIC_HOST: str = "127.0.0.1"
    ELASTIC_PORT: int = 9200

    PAGE_SIZE: int = 10
    PAGE_NUMBER: int = 1

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env"
    )


@lru_cache
def get_settings():
    load_dotenv()
    return Settings()


config = get_settings()
