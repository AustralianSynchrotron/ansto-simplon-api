from typing import Any, Literal

from pydantic import BaseModel


class TriggerMode(BaseModel):
    value: Literal["ints", "inte", "exts", "exte", "eies", "extg"]


class ROIMode(BaseModel):
    value: Literal["disabled", "4M"]


class Compression(BaseModel):
    value: Literal["bslz4", "none"]


class StreamFormat(BaseModel):
    value: Literal["cbor", "legacy"]


class StreamMode(BaseModel):
    value: Literal["enabled", "disabled"]


class SimplonRequestInt(BaseModel):
    value: int


class SimplonRequestFloat(BaseModel):
    value: float


class SimplonRequestAny(BaseModel):
    value: Any


class SimplonRequestStr(BaseModel):
    value: str


class SimplonRequestBool(BaseModel):
    value: bool


class SimplonRequestDict(BaseModel):
    value: dict


class DetectorConfiguration(BaseModel):
    """Any entry that is not sent via ZMQ goes here"""

    detector_readout_time: float = 0.0000001
    detector_bit_depth_image: int = 32
    detector_bit_depth_readout: int = 16
    detector_compression: Literal["bslz4", "none"] = "bslz4"
    detector_countrate_correction_cutoff: int = 126634
    detector_ntrigger: int = 1
    detector_number_of_excluded_pixels: int = 1251206
    detector_trigger_mode: str = "exts"
    software_version: str = "E-32-0130"
    eiger_fw_version: str = "release-2022.1.2rc2"
    roi_mode: Literal["disabled", "4M"] = "disabled"
    pixel_mask_applied: bool = True
