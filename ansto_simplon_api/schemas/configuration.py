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


class ZMQStartMessage(BaseModel):
    type: str = "start"
    series_id: int = 0
    number_of_images: int = 1
    user_data: dict | None = {}
    series_unique_id: str = ""

    image_size_x: int = 3108


class DetectorConfiguration(BaseModel):
    """Any entry that is not sent via ZMQ goes here"""

    detector_readout_time: float = 0.0000001
