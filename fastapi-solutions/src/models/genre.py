from pydantic import Field

import orjson
from pydantic import BaseModel

from src.shared.orjson_dumps import orjson_dumps


class Genre(BaseModel):
    uuid: str = Field(alias="id")
    name: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps