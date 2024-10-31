from fastapi import APIRouter

from ...schemas.configuration import (
    SimplonRequestAny,
    SimplonRequestStr,
    StreamConfiguration,
)
from ...simulate_zmq_stream import zmq_stream

router = APIRouter(prefix="/stream/api/1.8.0/config", tags=["Stream Configuration"])

stream_config = StreamConfiguration()


@router.put("/header_appendix")
async def set_user_data(user_data: SimplonRequestAny):
    zmq_stream.user_data = user_data.value
    return {"value": zmq_stream.user_data}


@router.get("/header_appendix")
async def get_user_data():
    return {"value": zmq_stream.user_data}


@router.get("/format")
async def get_format():
    return {"value": stream_config.format}


@router.put("/format")
async def set_format(input: SimplonRequestStr):
    stream_config.format = input.value
    return {"value": stream_config.format}


@router.get("/mode")
async def get_mode():
    return {"value": stream_config.format}


@router.put("/mode")
async def set_mode(input: SimplonRequestStr):
    stream_config.mode = input.value
    return {"value": stream_config.mode}


### Stream subsystem config
# header_detail
# image_appendix
# mode
