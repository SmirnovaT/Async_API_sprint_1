import uuid
from functools import lru_cache
from http import HTTPStatus
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, HTTPException
from redis.asyncio import Redis

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
        except NotFoundError:
            return None
        return Film(**doc["_source"])

    # Todo Добавить проверку на кеш в редисе
    async def get_films(
        self,
        genre: uuid.UUID = None,
        sort: str = "-imdb_rating",
        page_size: int = 10,
        page_number: int = 1,
    ) -> list[Film]:
        films = await self._get_all_films_from_elastic(
            genre=genre, sort=sort, page_size=page_size, page_number=page_number
        )
        return films

    async def _get_all_films_from_elastic(
        self,
        genre: uuid.UUID = None,
        sort: str = "-imdb_rating",
        page_size: int = 10,
        page_number: int = 1,
    ) -> list[Film]:
        """Получение всех фильмов с возможностью фильтрации по uuid жанра.
        По умолчанию остортированы по убыванию imdb_rating"""

        try:
            query = await self.construct_query(genre, sort, page_size, page_number)
            result = await self.elastic.search(index="movies", body=query)
            films = [Film(**doc["_source"]) for doc in result["hits"]["hits"]]
            return films
        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Произошла непредвиденная ошибка {e}",
            )

    async def construct_query(
        self,
        genre: uuid.UUID = None,
        sort: str = "-imdb_rating",
        page_size: int = 10,
        page_number: int = 1,
    ) -> dict:
        """Создание запроса для выполнения к индексу Elasticsearch"""

        sort_direction = "asc" if not sort.startswith("-") else "desc"
        sort_field = sort[1:] if sort_direction == "desc" else sort
        query = {
            "query": {"match_all": {}},
            "sort": [{sort_field: {"order": sort_direction}}],
            "from": (page_number - 1) * page_size,
            "size": page_size,
        }
        genre_name = await self.get_genre_name(genre)
        if genre_name:
            query["query"] = {"terms": {"genres": [str(genre_name)]}}
        return query

    async def get_genre_name(self, genre: uuid.UUID = None) -> str:
        """Получение названия жанра по переданному uuid жанра"""

        if genre:
            try:
                genre_result = await self.elastic.get(index="genres", id=str(genre))
                return genre_result["_source"]["name"]
            except NotFoundError as e:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail=f"Переданный жанр не найден: {e}",
                )
        return None

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get/
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
