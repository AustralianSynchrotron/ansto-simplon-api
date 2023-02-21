from pydantic import BaseModel
from typing import Any


class SimplonRequestInt(BaseModel):
    value: int


class SimplonRequestFloat(BaseModel):
    value: float


class SimplonRequestAny(BaseModel):
    value: Any
