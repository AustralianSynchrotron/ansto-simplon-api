from fastapi import APIRouter

from ...schemas.configuration import SimplonRequestAny
from ...simulate_zmq_stream import zmq_stream

router = APIRouter(prefix="/stream/api/1.8.0/config", tags=["Stream Configuration"])


@router.put("/header_appendix")
async def set_user_data(user_data: SimplonRequestAny):
    zmq_stream.user_data = user_data.value
    return {"value": zmq_stream.user_data}


@router.get("/header_appendix")
async def get_user_data():
    return {"value": zmq_stream.user_data}


### Stream subsystem config
# header_detail
# image_appendix
# mode
