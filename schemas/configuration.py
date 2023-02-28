from typing import Any

from pydantic import BaseModel


class SimplonRequestInt(BaseModel):
    value: int


class SimplonRequestFloat(BaseModel):
    value: float


class SimplonRequestAny(BaseModel):
    value: Any
