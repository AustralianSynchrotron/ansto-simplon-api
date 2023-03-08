# import glob
import os

from fastapi import FastAPI

from schemas.configuration import (
    SimplonRequestAny,
    SimplonRequestFloat,
    SimplonRequestInt,
    SimplonRequestStr,
)
from simulate_zmq_stream import ZmqStream

app = FastAPI()

ZMQ_ADDRESS = os.environ.get("ZMQ_ADDRESS", "tcp://*:5555")
HDF5_MASTER_FILE = os.environ["HDF5_MASTER_FILE"]
DELAY_BETWEEN_FRAMES = float(os.environ.get("DELAY_BETWEEN_FRAMES", "0.1"))
NUMBER_OF_DATA_FILES = int(os.environ.get("NUMBER_OF_DATA_FILES", "2"))
NUMBER_OF_FRAMES_PER_TRIGGER = int(os.environ.get("NUMBER_OF_FRAMES_PER_TRIGGER", "1"))

stream = ZmqStream(
    address=ZMQ_ADDRESS,
    hdf5_file_path=HDF5_MASTER_FILE,
    delay_between_frames=DELAY_BETWEEN_FRAMES,
    number_of_data_files=NUMBER_OF_DATA_FILES,
    number_of_frames_per_trigger=NUMBER_OF_FRAMES_PER_TRIGGER,
)


@app.get("/")
def home():
    return {"SIMplonAPI": "Test"}


@app.put("/detector/api/1.8.0/command/trigger")
def trigger():
    stream.stream_frames(stream.frames)


@app.put("/detector/api/1.8.0/command/arm")
def arm():
    stream.sequence_id += 1
    # Reset the image number every time we arm the detector
    stream.image_number = 0
    stream.stream_start_message()
    return {"sequence id": stream.sequence_id}


@app.put("/detector/api/1.8.0/command/disarm")
def disarm():
    stream.stream_end_message()
    print("Disarm detector")


@app.put("/detector/api/1.8.0/config/frame_time")
async def set_frame_time(frame_time: SimplonRequestFloat):
    return {"value": frame_time.value}


@app.put("/detector/api/1.8.0/config/nimages")
async def set_nimages(number_of_images: SimplonRequestInt):
    stream.number_of_frames_per_trigger = number_of_images.value
    return {"value": stream.number_of_frames_per_trigger}


@app.get("/detector/api/1.8.0/config/nimages")
async def get_nimages():
    return {"value": stream.number_of_frames_per_trigger}


@app.put("/detector/api/1.8.0/config/compression")
async def set_compression(compression: SimplonRequestStr):
    stream.compression = compression.value
    return {"value": stream.compression}


@app.get("/detector/api/1.8.0/config/compression")
async def get_compression():
    return {"value": stream.compression}


@app.put("/stream/api/1.8.0/config/header_appendix")
async def set_user_data(user_data: SimplonRequestAny):
    stream.user_data = user_data.value
    return {"value": stream.user_data}


@app.get("/stream/api/1.8.0/config/header_appendix")
async def get_user_data():
    return {"value": stream.user_data}


@app.get("/detector/api/1.8.0/config/sensor_thickness")
async def get_sensor_thickness():
    return {"value": 0.000450}


@app.get("/detector/api/1.8.0/config/sensor_material")
async def get_sensor_material():
    return {"value": "Si"}


@app.get("/detector/api/1.8.0/config/x_pixel_size")
async def get_x_pixel_size():
    return {"value": 0.000075000000000}


@app.get("/detector/api/1.8.0/config/y_pixel_size")
async def get_y_pixel_size():
    return {"value": 0.000075000000000}


@app.get("/detector/api/1.8.0/config/auto_summation")
async def get_auto_summation():
    return {"value": True}


@app.get("/detector/api/1.8.0/config/eiger_fw_version")
async def get_eiger_fw_version():
    return {"value": "release-2020.2.5"}


@app.get("/detector/api/1.8.0/config/software_version")
async def get_software_version():
    return {"value": "1.8.0"}


@app.get("/detector/api/1.8.0/config/description")
async def get_description():
    return {"value": "Dectris EIGER2 Si 9M"}


@app.get("/detector/api/1.8.0/config/detector_number")
async def get_detector_number():
    return {"value": "E-18-0108"}


@app.get("/detector/api/1.8.0/config/detector_type")
async def get_detector_type():
    return {"value": "HPC"}


@app.get("/detector/api/1.8.0/config/detector_readout_time")
async def get_detector_readout_time():
    return {"value": 0.0000001}


@app.get("/detector/api/1.8.0/config/bit_depth_image")
async def get_bit_depth_image():
    return {"value": 32}


@app.get("/detector/api/1.8.0/config/bit_depth_readout")
async def get_bit_depth_readout():
    return {"value": 16}


@app.get("/detector/api/1.8.0/config/countrate_correction_count_cutoff")
async def get_countrate_correction_count_cutoff():
    return {"value": 133343}


@app.get("/detector/api/1.8.0/config/frame_count_time")
async def get_frame_count_time():
    return {"value": 0.004170816650000}


@app.get("/detector/api/1.8.0/config/number_of_excluded_pixels")
async def get_number_of_excluded_pixels():
    return {"value": 664708}


@app.get("/detector/api/1.8.0/config/trigger_mode")
async def get_trigger_mode():
    return {"value": "exts"}


@app.get("/detector/api/1.8.0/config/x_pixels_in_detector")
async def get_x_pixels_in_detector():
    return {"value": 3108}


@app.get("/detector/api/1.8.0/config/y_pixels_in_detector")
async def get_y_pixels_in_detector():
    return {"value": 3262}
