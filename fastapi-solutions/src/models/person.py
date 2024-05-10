import uuid
from orjson import orjson
from pydantic import BaseModel
from typing import List

from src.utils.orjson_dumps import orjson_dumps


class Person(BaseModel):
    uuid: str
    full_name: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class PersonFilm(BaseModel):
    uuid: uuid.UUID
    roles: List[str]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class PersonWithFilms(BaseModel):
    uuid: str
    full_name: str
    films: List[PersonFilm]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
