from typing import List
import orjson

from pydantic import BaseModel, Field

from src.models.genre import Genre
from src.models.person import Person
from src.utils.orjson_dumps import orjson_dumps


class FilmBase(BaseModel):
    uuid: str = Field(..., alias="id")
    title: str | None
    description: str | None
    imdb_rating: float | None

    class Config:
        populate_by_name = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class FullFilm(BaseModel):
    uuid: str = Field(..., alias="id")
    title: str | None
    description: str | None
    imdb_rating: float | None
    genres: List[Genre]
    actors: List[Person]
    writers: List[Person]
    directors: List[Person]

    class Config:
        populate_by_name = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps
