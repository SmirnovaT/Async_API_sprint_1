from typing import List

from pydantic import Field

from src.models.model_config import BaseOrjsonModel
from src.models.genre import Genre
from src.models.person import Person


class FilmBase(BaseOrjsonModel):
    uuid: str = Field(..., alias="id")
    title: str | None
    description: str | None
    imdb_rating: float | None


class FullFilm(BaseOrjsonModel):
    uuid: str = Field(..., alias="id")
    title: str | None
    description: str | None
    imdb_rating: float | None
    genres: List[Genre]
    actors: List[Person]
    writers: List[Person]
    directors: List[Person]

