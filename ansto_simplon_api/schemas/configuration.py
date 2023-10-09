from typing import Any

from pydantic import BaseModel


class SimplonRequestInt(BaseModel):
    value: int


class SimplonRequestFloat(BaseModel):
    value: float


class SimplonRequestAny(BaseModel):
    value: Any


class SimplonRequestStr(BaseModel):
    value: str


class DetectorConfiguration(BaseModel):
    x_pixels_in_detector: int = 3108
