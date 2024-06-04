from datetime import datetime, timezone
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
    detector_translation: tuple[float, float, float] = [0, 0, -0.298]
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
    saturation_value: int | None = 0
    sensor_material: str = "Si"
    sensor_thickness: float = 4.5e-04
    series_id: int = 0
    series_unique_id: str = 0
    threshold_energy: dict = {"threshold_1": 6350}
    user_data: dict | None = {}
    virtual_pixel_interpolation_enabled: bool = True


class DetectorConfiguration(BaseModel):
    """Any entry that is not sent via ZMQ goes here"""

    detector_readout_time: float = 0.0000001
    detector_bit_depth_image: int = 32
    detector_bit_depth_readout: int = 16
    detector_readout_time: float = 1e-07
    detector_compression: str = "bslz4"
    detector_countrate_correction_cutoff: int = 126634
    detector_ntrigger: int = 1
    detector_number_of_excluded_pixels: int = 1251206
    detector_trigger_mode: str = "exts"
