from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel


class TriggerMode(BaseModel):
    value: Literal["ints", "inte", "exts", "exte", "eies", "extg"]


class ROIMode(BaseModel):
    value: Literal["disabled", "4M"]


class Compression(BaseModel):
    value: Literal["bslz4", "none"]


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


class ZMQStartMessage(BaseModel):
    """
    Default values matches pre-operations
    test dataset. To be updated when we collect
    new datasets to be used as standards.

    TODO: Map from channel name to energy, flatfield, mask, etc
    """

    type: str = "start"
    arm_date: datetime = datetime.now(tz=timezone.utc)
    beam_center_x: float = 1056
    beam_center_y: float = 1134
    channels: list[str] = ["0"]
    count_time: float = 0.0109
    countrate_correction_enabled: bool = True
    countrate_correction_lookup_table: list | None = [0]
    detector_description: str = "Dectris EIGER2 Si 16M"
    detector_serial_number: str = "E-32-0130"
    detector_translation: tuple[float, float, float] | list = [0, 0, -0.298]
    flatfield: list | None = []
    flatfield_enabled: bool = True
    frame_time: float = 0.0110
    goniometer: dict = {"omega": {"increment": 0.1, "start": 360}}
    image_dtype: str = "uint32"
    image_size_x: int = 2070
    image_size_y: int = 2167
    incident_energy: float = 12700
    incident_wavelength: float = 0.9763
    number_of_images: int = 1
    pixel_mask: list | None = []
    pixel_mask_enabled: bool = True
    pixel_size_x: float = 7.5e-05
    pixel_size_y: float = 7.5e-05
    saturation_value: int | None = 33000  # TODO: check where this value comes from
    sensor_material: str = "Si"
    sensor_thickness: float = 4.5e-04
    series_id: int = 0
    series_unique_id: str = "0"
    threshold_energy: dict = {"threshold_1": 6350}
    user_data: dict | str | None = ""
    virtual_pixel_interpolation_enabled: bool = True


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


class StreamConfiguration(BaseModel):
    format: Literal["cbor", "legacy"] = "cbor"
    mode: Literal["enabled", "disabled"] = "enabled"
