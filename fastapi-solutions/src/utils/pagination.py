from fastapi import Query

from src.core.config import config


class Paginator:
    def __init__(
        self,
        page_size: int = Query(default=config.PAGE_SIZE, ge=1, le=100),
        page_number: int = Query(default=config.PAGE_NUMBER, ge=1),
    ):
        self.page_size = page_size
        self.page_number = page_number
