from fastapi import APIRouter

from ...schemas.ansto_endpoints import LoadHDF5File
from ...simulate_zmq_stream import zmq_stream

router = APIRouter(prefix="/ansto_endpoints", tags=["ANSTO Endpoints"])


@router.put("/hdf5_master_file")
async def set_user_data(hdf5_model: LoadHDF5File):
    zmq_stream.create_list_of_compressed_frames(
        hdf5_file_path=hdf5_model.hdf5_file_path,
        compression=hdf5_model.compression,
        number_of_datafiles=hdf5_model.number_of_datafiles,
    )
    zmq_stream.frame_id = 0
    zmq_stream.image_number = 0
    return {"value": zmq_stream.hdf5_file_path}


@router.get("/hdf5_master_file")
async def get_user_data():
    return {"value": zmq_stream.hdf5_file_path}
