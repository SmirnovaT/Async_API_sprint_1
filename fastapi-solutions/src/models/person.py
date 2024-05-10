from typing import List
import uuid as uuid
import orjson

from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()

class PersonFilm(BaseModel):
    uuid: uuid.UUID
    roles: List[str]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Person(BaseModel):
    uuid: str = Field(..., alias="id")
    full_name: str
    #films: List[PersonFilm]

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps




