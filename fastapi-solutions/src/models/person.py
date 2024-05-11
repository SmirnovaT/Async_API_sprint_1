import uuid

from pydantic import BaseModel

from src.models.model_config import BaseOrjsonModel


class Person(BaseOrjsonModel):
    uuid: str
    full_name: str


class PersonFilm(BaseOrjsonModel):
    uuid: uuid.UUID
    roles: list[str]


class PersonWithFilms(Person):
    films: list[PersonFilm]

class PersonWithFilms(BaseModel):
    uuid: str
    full_name: str
    films: list[PersonFilm]


class PersonFilmWithRating(BaseOrjsonModel):
    uuid: uuid.UUID
    title: str
    imdb_rating: float
