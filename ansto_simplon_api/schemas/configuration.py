from typing import Any

from pydantic import BaseModel

from datetime import datetime


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


class ZMQStartMessage(BaseModel):
    """
    Default values matches pre-operations
    test dataset. To be updated when we collect
    new datasets to be used as standards.
    """

    type: str = "start"
    arm_date: datetime = datetime.now()
    beam_center_x: float = 2099.46240234375
    beam_center_y: float = 2119.423828125
    channels: list[str] = ["1"]
    count_time: float = 0.010999999940395355
    countrate_correction_enabled: bool = True
    countrate_correction_lookup_table: list | None
    detector_description: str = "Dectris EIGER2 Si 16M"
    detector_serial_number: str = "E-32-0130"
    detector_translation: list[float, float, float]
    flatfield: list | None
    flatfield_enabled: bool = True
    frame_time: float = 0.011003094725310802
    goniometer: dict = {"omega": {"increment": float, "start": float}}
    image_dtype: str
    image_size_x: int = 4150
    image_size_y: int = 4371
    incident_energy: float = 0.9762535309700807
    number_of_images: int = 1
    pixel_mask: list | None
    pixel_mask_enabled: bool
    pixel_size_x: float = 7.5e-05
    pixel_size_y: float = 7.5e-05
    saturation_value: int | None
    sensor_material: str = "Si"
    sensor_thickness: float = 4.5e-04
    series_id: int = 0
    series_unique_id: str
    threshold_energy: float
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
    detector_number_of_excluded_pixels: int
    detector_trigger_mode: str = "exts"
