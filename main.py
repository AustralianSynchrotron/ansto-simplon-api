# import glob
import os
from distutils.util import strtobool

from fastapi import FastAPI

from simulate_zmq_stream import ZmqStream

app = FastAPI()

ZMQ_ADDRESS = os.environ.get("ZMQ_ADDRESS", "tcp://*:5555")
HDF5_MASTER_FILE = os.environ["HDF5_MASTER_FILE"]
DELAY_BETWEEN_FRAMES = float(os.environ.get("DELAY_BETWEEN_FRAMES", "0.1"))
COMPRESSION_TYPE = os.environ.get("COMPRESSION_TYPE", "lz4")
RASTER_FRAMES = bool(strtobool(os.environ.get("RASTER_FRAMES", "True")))

stream = ZmqStream(
    address=ZMQ_ADDRESS,
    hdf5_file_path=HDF5_MASTER_FILE,
    compression=COMPRESSION_TYPE,
    delay_between_frames=DELAY_BETWEEN_FRAMES,
    raster_frames=RASTER_FRAMES,
)


@app.get("/")
def home():
    return {"SIMplonAPI": "Test"}


@app.put("/detector/api/1.8.0/command/trigger")
def trigger():
    stream.start_stream()


@app.put("/detector/api/1.8.0/command/arm")
def arm():
    stream.sequence_id += 1
    return {"sequence id": stream.sequence_id}


@app.put("/detector/api/1.8.0/command/disarm")
def disarm():
    print("Disarm detector")


@app.put("/detector/api/1.8.0/config/{frame_time}")
def set_frame_time(frame_time):
    return {"value": frame_time}


@app.put("/detector/api/1.8.0/config/{nimages}")
def set_nimages(nimages):
    return {"value": nimages}
