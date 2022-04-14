import glob

from fastapi import FastAPI

from simulate_zmq_stream import ZmqStream

app = FastAPI()

HDF5_MASTER_FILE = glob.glob("*_master.h5")[0]
stream = ZmqStream("tcp://*:5555", HDF5_MASTER_FILE, compression="lz4")


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
