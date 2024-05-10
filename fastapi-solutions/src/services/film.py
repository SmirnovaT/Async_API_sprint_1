import uuid
from functools import lru_cache
from http import HTTPStatus
from typing import Optional, List
from pydantic import parse_obj_as
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, HTTPException
from redis.asyncio import Redis

from src.core.logger import a_api_logger
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import FullFilm, Genre, FilmBase
from src.models.person import Person
from src.services.genre import GenreService, get_genre_service

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(
        self,
        redis: Redis,
        elastic: AsyncElasticsearch,
        genre_service: GenreService,
    ):
        self.redis = redis
        self.elastic = elastic
        self.genre_service = genre_service

    async def get_film_details(self, film_id: str) -> Optional[FullFilm]:
        """Получение полной информации по фильму"""
        film_data = await self._get_film_from_elastic(film_id)
        if not film_data:
            return None
        film = await self._get_full_info(film_data)
        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[dict]:
        """Получение фильмов по id фильма"""
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
            film_data = doc["_source"]
            return film_data
        except NotFoundError as e:
            a_api_logger.error(f"Фильм не найден: {e}")
            return None

    async def _get_full_info(self, film_data: dict) -> FullFilm:
        """Преобразование исходных данных фильма"""

        genres_list = []
        for genre_name in film_data["genres"]:
            genre_uuid = await self.genre_service.get_uuid_genre(genre_name)
            genre_obj = Genre(id=genre_uuid, name=genre_name)
            genres_list.append(genre_obj)

        film_data.update(
            {
                "genres": genres_list,
                "actors": await self._get_person_list(film_data["actors"]),
                "writers": await self._get_person_list(film_data["writers"]),
                "directors": await self._get_person_list(film_data["directors"]),
            }
        )
        return FullFilm(**film_data)

    @staticmethod
    async def _get_person_list(person_data):
        return [
            Person(uuid=person["id"], full_name=person["name"])
            for person in person_data
        ]

    async def get_similar_films(self, film_id: str) -> List[FilmBase] | None:
        """Получение списка фильмов, у которых есть хотя бы один такой же жанр,
        как у переданного фильма (film_id)"""

        film_data = await self._get_film_from_elastic(film_id)
        if not film_data:
            return None
        genres = film_data["genres"]
        query = {
            "query": {
                "bool": {
                    "should": [{"match": {"genres": genre}} for genre in genres],
                    "minimum_should_match": 1,
                }
            }
        }
        result = await self.elastic.search(index="movies", body=query)
        films = [
            parse_obj_as(FilmBase, hit["_source"]) for hit in result["hits"]["hits"]
        ]
        return films

    async def get_all_films_from_elastic(
        self,
        genre: uuid.UUID = None,
        sort: str = "-imdb_rating",
        page_size: int = 10,
        page_number: int = 1,
    ) -> list[FilmBase]:
        """Получение всех фильмов с возможностью фильтрации по uuid жанра.
        По умолчанию остортированы по убыванию imdb_rating"""

        try:
            query = await self._construct_query(genre, sort, page_size, page_number)
            result = await self.elastic.search(index="movies", body=query)
            films = [FilmBase(**doc["_source"]) for doc in result["hits"]["hits"]]
            return films
        except Exception as e:
            a_api_logger.error(f"Произошла непредвиденная ошибка:{e}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Произошла непредвиденная ошибка {e}",
            )

    async def _construct_query(
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
        genre_name = await self.genre_service.get_genre_name(genre)
        if genre_name:
            query["query"] = {"terms": {"genres": [str(genre_name)]}}
        return query

    async def _film_from_cache(self, film_id: str) -> Optional[FilmBase]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get/
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = FilmBase.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: FilmBase):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
    genre_service: GenreService = Depends(get_genre_service),
) -> FilmService:
    return FilmService(redis, elastic, genre_service)
