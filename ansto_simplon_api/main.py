# import glob

from fastapi import FastAPI

from .routes.detector.command import router as command
from .routes.stream.config import router as stream_config
from .routes.detector.config import router as detector_config
from .simulate_zmq_stream import zmq_stream

app = FastAPI()
app.include_router(command)
app.include_router(stream_config)
app.include_router(detector_config)


@app.get("/")
def home():
    return {"ANSTO SIMPLON API": "Home"}


