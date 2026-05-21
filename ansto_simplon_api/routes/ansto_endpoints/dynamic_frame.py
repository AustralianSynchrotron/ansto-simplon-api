from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from starlette import status

from ...config import FrameSourceEnum
from ...schemas.ansto_endpoints import FrameSource
from ...zmq_stream.simulate_zmq_stream import zmq_stream

router = APIRouter(
    prefix="/ansto_endpoints/dynamic_frame", tags=["ANSTO Dynamic Frame"]
)


@router.get("/source")
async def get_frame_source():
    return {"value": zmq_stream.frame_source}


@router.put("/source")
async def set_frame_source(source: FrameSource):
    if (
        source.value == FrameSourceEnum.DYNAMIC_FRAME
        and zmq_stream.stream_config.format == "legacy"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="dynamic-frame source is supported only when stream format is cbor",
        )

    try:
        zmq_stream.set_frame_source(source.value)
    except RuntimeError as ex:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(ex),
        ) from ex

    return {"value": zmq_stream.frame_source}
