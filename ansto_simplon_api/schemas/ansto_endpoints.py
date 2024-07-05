from typing import Literal

from pydantic import BaseModel, Field


class LoadHDF5File(BaseModel):
    hdf5_file_path: str = Field(examples=["/path/to/master_file"])
    number_of_datafiles: int | None = Field(default=None, examples=[1])
    compression: Literal["bslz4", "none"] = Field(default="bslz4", examples=["bslz4"])
