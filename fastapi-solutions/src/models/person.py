import uuid

from typing import List

from src.models.model_config import BaseOrjsonModel


class Person(BaseOrjsonModel):
    uuid: str
    full_name: str


class PersonFilm(BaseOrjsonModel):
    uuid: uuid.UUID
    roles: List[str]


class PersonWithFilms(Person):
    films: List[PersonFilm]


class PersonFilmWithRating(BaseOrjsonModel):
    uuid: uuid.UUID
    title: str
    imdb_rating: float
