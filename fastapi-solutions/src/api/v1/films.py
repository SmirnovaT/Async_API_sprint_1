from http import HTTPStatus
from typing import Optional, List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.core.logger import a_api_logger
from src.models.film import FilmBase
from src.models.person import Person
from src.services.film import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    uuid: uuid.UUID
    title: str
    imdb_rating: Optional[float]
    description: str
    actors: List[Person]
    writers: List[Person]
    directors: List[Person]


@router.get("/{film_id}", response_model=Film, summary="Полная информация по фильму")
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_film_details(film_id)
    if not film:
        a_api_logger.error("Фильм не найден")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Фильм не найден")

    return Film(
        uuid=film.uuid,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=film.genres,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors,
    )


class Films(BaseModel):
    uuid: uuid.UUID
    title: str
    imdb_rating: Optional[float]


@router.get("/", response_model=List[Films], summary="Получение всех фильмов")
async def films(
    genre: uuid.UUID = None,
    sort: str = "-imdb_rating",
    page_size: int = 10,
    page_number: int = 1,
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmBase]:
    return await film_service.get_all_films_from_elastic(
        genre=genre, sort=sort, page_size=page_size, page_number=page_number
    )


@router.get(
    "/{film_id}/similar",
    response_model=List[FilmBase],
    summary="Похожие фильмы (с такими же жанрами)",
)
async def similar_films(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> List[FilmBase]:
    films = await film_service.get_similar_films(film_id)
    if not films:
        a_api_logger.error("Фильм не найден")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Фильм не найден")
    return films
