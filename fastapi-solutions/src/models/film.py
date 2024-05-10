from typing import Optional, List
import orjson

from pydantic import BaseModel, Field

from src.models.genre import Genre
from src.models.person import Person
from src.shared.orjson_dumps import orjson_dumps


class FilmBase(BaseModel):
    uuid: str = Field(..., alias="id")
    title: Optional[str]
    description: Optional[str]
    imdb_rating: Optional[float]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class FullFilm(BaseModel):
    uuid: str = Field(..., alias="id")
    title: Optional[str]
    description: Optional[str]
    imdb_rating: Optional[float]
    genres: List[Genre]
    actors: List[Person]
    writers: List[Person]
    directors: List[Person]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
