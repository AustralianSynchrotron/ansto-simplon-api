from fastapi import APIRouter

from ...schemas.configuration import (
    SimplonRequestFloat,
    SimplonRequestInt,
    SimplonRequestStr,
)
from ...simulate_zmq_stream import zmq_stream

router = APIRouter(prefix="/detector/api/1.8.0/config", tags=["Detector Configuration"])


@router.put("/frame_time")
async def set_frame_time(frame_time: SimplonRequestFloat):
    return {"value": frame_time.value}


@router.put("/nimages")
async def set_nimages(number_of_images: SimplonRequestInt):
    zmq_stream.number_of_frames_per_trigger = number_of_images.value
    return {"value": zmq_stream.number_of_frames_per_trigger}


@router.get("/nimages")
async def get_nimages():
    return {"value": zmq_stream.number_of_frames_per_trigger}


@router.put("/compression")
async def set_compression(compression: SimplonRequestStr):
    zmq_stream.compression = compression.value
    return {"value": zmq_stream.compression}


@router.get("/compression")
async def get_compression():
    return {"value": zmq_stream.compression}


@router.get("/sensor_thickness")
async def get_sensor_thickness():
    return {"value": 0.000450}


@router.get("/sensor_material")
async def get_sensor_material():
    return {"value": "Si"}


@router.get("/x_pixel_size")
async def get_x_pixel_size():
    return {"value": 0.000075000000000}


@router.get("/y_pixel_size")
async def get_y_pixel_size():
    return {"value": 0.000075000000000}


@router.get("/auto_summation")
async def get_auto_summation():
    return {"value": True}


@router.get("/eiger_fw_version")
async def get_eiger_fw_version():
    return {"value": "release-2020.2.5"}


@router.get("/software_version")
async def get_software_version():
    return {"value": "1.8.0"}


@router.get("/description")
async def get_description():
    return {"value": "Dectris EIGER2 Si 9M"}


@router.get("/detector_number")
async def get_detector_number():
    return {"value": "E-18-0108"}


@router.get("/detector_type")
async def get_detector_type():
    return {"value": "HPC"}


@router.get("/detector_readout_time")
async def get_detector_readout_time():
    return {"value": 0.0000001}


@router.get("/bit_depth_image")
async def get_bit_depth_image():
    return {"value": 32}


@router.get("/bit_depth_readout")
async def get_bit_depth_readout():
    return {"value": 16}


@router.get("/countrate_correction_count_cutoff")
async def get_countrate_correction_count_cutoff():
    return {"value": 133343}


@router.get("/frame_count_time")
async def get_frame_count_time():
    return {"value": 0.004170816650000}


@router.get("/number_of_excluded_pixels")
async def get_number_of_excluded_pixels():
    return {"value": 664708}


@router.get("/trigger_mode")
async def get_trigger_mode():
    return {"value": "exts"}


@router.get("/x_pixels_in_detector")
async def get_x_pixels_in_detector():
    return {"value": 3108}


@router.get("/y_pixels_in_detector")
async def get_y_pixels_in_detector():
    return {"value": 3262}


@router.get("/ntrigger")
async def get_ntrigger():
    return {"value": 1}
