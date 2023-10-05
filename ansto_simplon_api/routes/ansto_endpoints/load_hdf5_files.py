from fastapi import APIRouter

from ...schemas.configuration import SimplonRequestStr
from ...simulate_zmq_stream import zmq_stream

router = APIRouter(prefix="/ansto_endpoints", tags=["ANSTO Endpoints"])


@router.put("/load_hdf5_master_file")
async def set_user_data(hdf5_file_path: SimplonRequestStr):
    zmq_stream.hdf5_file_path = hdf5_file_path.value
    return {"value": zmq_stream.hdf5_file_path}
