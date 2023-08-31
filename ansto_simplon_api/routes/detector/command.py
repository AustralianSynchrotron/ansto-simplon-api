from fastapi import APIRouter

from ...simulate_zmq_stream import zmq_stream

router = APIRouter(prefix="/detector/api/1.8.0/command", tags=["Detector Command"])


@router.put("/trigger")
def trigger():
    zmq_stream.stream_frames(zmq_stream.frames)


@router.put("/arm")
def arm():
    zmq_stream.sequence_id += 1
    # Reset the image number every time we arm the detector
    zmq_stream.image_number = 0
    zmq_stream.stream_start_message()
    return {"sequence id": zmq_stream.sequence_id}


@router.put("/disarm")
def disarm():
    zmq_stream.stream_end_message()
    print("Disarm detector")
