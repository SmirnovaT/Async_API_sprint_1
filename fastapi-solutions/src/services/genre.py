from functools import lru_cache

import uuid
from http import HTTPStatus

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, HTTPException
from redis.asyncio import Redis

from src.core.logger import a_api_logger
from src.db.elastic import get_elastic
from src.db.redis import get_redis


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_genre_name(self, genre: uuid.UUID = None) -> str:
        """Получение названия жанра по переданному uuid жанра"""

        if genre:
            try:
                genre_result = await self.elastic.get(index="genres", id=str(genre))
                return genre_result["_source"]["name"]
            except NotFoundError as e:
                a_api_logger.error(f"Жанр не найден: {e}")
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail=f"Переданный жанр не найден: {e}",
                )
        return None

    async def get_uuid_genre(self, genre_name: str) -> uuid.UUID:
        """Получение uuid жанра по переданному названию жанра"""
        query = {"query": {"match": {"name": genre_name}}}
        try:
            response = await self.elastic.search(index="genres", body=query)
            if response["hits"]["total"]["value"] > 0:
                genre_data = response["hits"]["hits"][0]["_source"]
                return genre_data["id"]
            else:
                raise NotFoundError(f"Жанр '{genre_name}' не найден")
        except NotFoundError as e:
            a_api_logger.error(f"Жанр не найден: {e}")
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Переданный жанр не найден: {e}",
            )


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
