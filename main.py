# import glob
import os
from distutils.util import strtobool

from fastapi import FastAPI

from schemas.configuration import FrameTime, NumberOfImages
from simulate_zmq_stream import ZmqStream

app = FastAPI()

ZMQ_ADDRESS = os.environ.get("ZMQ_ADDRESS", "tcp://*:5555")
HDF5_MASTER_FILE = os.environ["HDF5_MASTER_FILE"]
DELAY_BETWEEN_FRAMES = float(os.environ.get("DELAY_BETWEEN_FRAMES", "0.1"))
COMPRESSION_TYPE = os.environ.get("COMPRESSION_TYPE", "lz4")
RASTER_FRAMES = bool(strtobool(os.environ.get("RASTER_FRAMES", "False")))
NUMBER_OF_DATA_FILES = int(os.environ.get("NUMBER_OF_DATA_FILES", "2"))
NUMBER_OF_FRAMES_PER_TRIGGER = int(
    os.environ.get("NUMBER_OF_FRAMES_PER_TRIGGER", "400")
)

stream = ZmqStream(
    address=ZMQ_ADDRESS,
    hdf5_file_path=HDF5_MASTER_FILE,
    compression=COMPRESSION_TYPE,
    delay_between_frames=DELAY_BETWEEN_FRAMES,
    raster_frames=RASTER_FRAMES,
    number_of_data_files=NUMBER_OF_DATA_FILES,
    number_of_frames_per_trigger=NUMBER_OF_FRAMES_PER_TRIGGER,
)


@app.get("/")
def home():
    return {"SIMplonAPI": "Test"}


@app.put("/detector/api/1.8.0/command/trigger")
def trigger():
    stream.stream_frames(stream.frames, stream.raster_frames)


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
async def set_frame_time(frame_time: FrameTime):
    return {"value": frame_time.value}


@app.put("/detector/api/1.8.0/config/nimages")
async def set_nimages(number_of_images: NumberOfImages):
    stream.number_of_frames_per_trigger = number_of_images.value
    return {"value": stream.number_of_frames_per_trigger}
