from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel


class CborStartMessage(BaseModel):
    """Cbor start message schema"""

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


class StreamConfiguration(BaseModel):
    format: Literal["cbor", "legacy"] = "cbor"
    mode: Literal["enabled", "disabled"] = "enabled"


class LegacyFrame(BaseModel):
    data: bytes
    dtype: str
    encoding: str
    size: int


class LegacyConfigHeader(BaseModel):
    beam_center_x: float
    beam_center_y: float
    count_time: float
    frame_time: float
    nimages: int
    ntrigger: int
    compression: Literal["bslz4", "none"]
    bit_depth_image: int
    bit_depth_readout: int
    pixel_mask_applied: bool
    roi_mode: Literal["disabled", "4M"]
    software_version: str
    detector_readout_time: float
    x_pixels_in_detector: int
    y_pixels_in_detector: int
