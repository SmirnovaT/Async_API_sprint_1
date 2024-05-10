from typing import List
import uuid as uuid
from http import HTTPStatus
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException

from src.services.person import PersonService, get_person_service

router = APIRouter()


class PersonFilm(BaseModel):
    uuid: uuid.UUID
    roles: List[str]


class PersonFilmWithRating(BaseModel):
    uuid: uuid.UUID
    title: str
    imdb_rating: float


class Person(BaseModel):
    uuid: uuid.UUID
    full_name: str
    films: List[PersonFilm] | None


@router.get("/search", response_model=List[Person])
async def person_search(
    query: str,
    page_number: int,
    page_size: int,
    person_service: PersonService = Depends(get_person_service),
) -> List[Person]:
    persons_list = await person_service.search_for_a_person(
        query, page_number, page_size
    )
    return [
        Person(
            uuid=person["uuid"], full_name=person["full_name"], films=person["films"]
        )
        for person in persons_list
    ]


@router.get(
    "/{person_id}",
    response_model=Person,
    summary="Получение персоны по ее uuid",
    description="Возвращает персону по id",
)
async def person(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Персона не найдена"
        )

    return person


@router.get(
    "/{person_id}/film/",
    response_model=List[PersonFilmWithRating],
    summary="Получение фильмов персоны по ее uuid",
    description="Возвращает фильмы по id персоны",
)
async def person_films(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> List[PersonFilmWithRating]:
    films = await person_service.get_only_person_films(person_id)
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Фильмы персоны не найдены"
        )

    return films
