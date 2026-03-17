from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel


class StreamBase(BaseModel):
    """Legacy and cbor stream base schema"""

    beam_center_x: float = 1056
    beam_center_y: float = 1134
    count_time: float = 0.0109
    detector_translation: tuple[float, float, float] | list = [0, 0, -0.298]
    frame_time: float = 0.0110
    pixel_size_x: float = 7.5e-05
    pixel_size_y: float = 7.5e-05
    sensor_material: str = "Si"
    sensor_thickness: float = 4.5e-04


class ZMQStartMessage(StreamBase):
    """Cbor start message schema"""

    type: str = "start"
    arm_date: datetime = datetime.now(tz=timezone.utc)
    channels: list[str] = ["0"]
    countrate_correction_enabled: bool = True
    countrate_correction_lookup_table: list | None = [0]
    detector_description: str = "Dectris EIGER2 Si 16M"
    detector_serial_number: str = "E-32-0130"
    flatfield: list | None = []
    flatfield_enabled: bool = True
    goniometer: dict = {"omega": {"increment": 0.1, "start": 360}}
    image_dtype: str = "uint32"
    image_size_x: int = 2070
    image_size_y: int = 2167
    incident_energy: float = 12700
    incident_wavelength: float = 0.9763
    number_of_images: int = 1
    pixel_mask: list | None = []
    pixel_mask_enabled: bool = True
    saturation_value: int | None = 33000  # TODO: check where this value comes from
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


class LegacyConfigHeader(StreamBase):
    auto_summation: bool
    bit_depth_image: int
    bit_depth_readout: int
    chi_increment: float
    chi_start: float
    compression: Literal["bslz4", "none"]
    countrate_correction_applied: bool
    countrate_correction_count_cutoff: int
    data_collection_date: str
    description: str
    detector_distance: float
    detector_number: str
    detector_readout_time: float
    eiger_fw_version: str
    element: str
    flatfield_correction_applied: bool
    frame_count_time: float
    frame_period: float
    kappa_increment: float
    kappa_start: float
    nimages: int
    ntrigger: int
    number_of_excluded_pixels: int
    omega_increment: float
    omega_start: float
    phi_increment: float
    phi_start: float
    photon_energy: float
    pixel_mask_applied: bool
    roi_mode: Literal["", "disabled", "4M"]  # TODO: check V1 roi modes, default is ""
    threshold_energy: float
    trigger_mode: str
    two_theta_increment: float
    two_theta_start: float
    virtual_pixel_correction_applied: bool
    wavelength: float
    software_version: str
    x_pixels_in_detector: int
    y_pixels_in_detector: int
