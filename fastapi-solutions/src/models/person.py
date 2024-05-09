from orjson import orjson
from pydantic import BaseModel
from src.shared.orjson_dumps import orjson_dumps


class Person(BaseModel):
    uuid: str
    full_name: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
