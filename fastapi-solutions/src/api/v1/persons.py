from typing import List
import logging
import uuid as uuid
from http import HTTPStatus
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException

from src.services.person import PersonService, get_person_service

router = APIRouter()

class PersonFilm(BaseModel):
    uuid: uuid.UUID
    roles: List[str]


class Person(BaseModel):
    id: uuid.UUID
    full_name: str
    #films: List[PersonFilm]

@router.get("/search", response_model=List[Person])
async def person_search(
    query: str, page_number: int, page_size: int, person_service: PersonService = Depends(get_person_service)
) -> List[Person]:
    persons_list = await person_service.search_for_a_person(query, page_number, page_size)
    logging.error(persons_list)
    return [Person(id = person["id"], full_name = person["full_name"]) for person in persons_list]

@router.get(
    "/{person_id}",
    response_model=Person,
    summary="Получение персоны по ее uuid",
    description="Возвращает персону по id",
)
async def person(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Персона не найдена")

    return person