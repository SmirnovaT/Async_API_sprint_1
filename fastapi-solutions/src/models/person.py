import uuid

from orjson import orjson
from pydantic import BaseModel

from src.utils.orjson_dumps import orjson_dumps


class Person(BaseModel):
    uuid: str
    full_name: str

    class Config:
        populate_by_name = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class PersonFilm(BaseModel):
    uuid: uuid.UUID
    roles: list[str]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class PersonWithFilms(BaseModel):
    uuid: str
    full_name: str
    films: list[PersonFilm]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class PersonFilmWithRating(BaseModel):
    uuid: uuid.UUID
    title: str
    imdb_rating: float

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
