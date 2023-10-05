from fastapi import FastAPI

from .routes.ansto_endpoints.load_hdf5_files import router as ansto_endpoints
from .routes.detector.command import router as command
from .routes.detector.config import router as detector_config
from .routes.stream.config import router as stream_config

app = FastAPI()
app.include_router(command)
app.include_router(stream_config)
app.include_router(detector_config)
app.include_router(ansto_endpoints)


@app.get("/")
def home():
    return {"ANSTO SIMPLON API": "Home"}
