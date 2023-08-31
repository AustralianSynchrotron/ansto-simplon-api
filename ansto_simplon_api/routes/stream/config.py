from fastapi import APIRouter
from ...simulate_zmq_stream import zmq_stream
from ...schemas.configuration import SimplonRequestAny

router = APIRouter(prefix="/detector/api/1.8.0/command", tags=["Stream Configuration"])


@router.put("/header_appendix")
async def set_user_data(user_data: SimplonRequestAny):
    zmq_stream.user_data = user_data.value
    return {"value": zmq_stream.user_data}


@router.get("/header_appendix")
async def get_user_data():
    return {"value": zmq_stream.user_data}
