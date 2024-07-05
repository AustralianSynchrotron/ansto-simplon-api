from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from starlette import status

from ...schemas.ansto_endpoints import LoadHDF5File
from ...simulate_zmq_stream import zmq_stream

router = APIRouter(prefix="/ansto_endpoints", tags=["ANSTO Endpoints"])


@router.put("/hdf5_master_file")
async def set_master_file(hdf5_model: LoadHDF5File):
    try:
        zmq_stream.create_list_of_compressed_frames(
            hdf5_file_path=hdf5_model.hdf5_file_path,
            compression=hdf5_model.compression,
            number_of_datafiles=hdf5_model.number_of_datafiles,
        )
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The number of datafiles specified exceed the number of datafiles available "
            "in the master file. Reduce number_of_datafiles",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    zmq_stream.frame_id = 0
    zmq_stream.image_number = 0
    return {"value": zmq_stream.hdf5_file_path}


@router.get("/hdf5_master_file")
async def get_master_file() -> LoadHDF5File:
    return LoadHDF5File(
        hdf5_file_path=zmq_stream.hdf5_file_path,
        number_of_datafiles=zmq_stream.number_of_data_files,
        compression=zmq_stream.compression,
    )
