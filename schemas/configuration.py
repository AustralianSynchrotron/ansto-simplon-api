from pydantic import BaseModel


class NumberOfImages(BaseModel):
    value: int


class FrameTime(BaseModel):
    value: int
