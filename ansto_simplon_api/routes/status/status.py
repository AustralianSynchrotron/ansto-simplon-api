from fastapi import APIRouter

router = APIRouter(prefix="/detector/api/1.8.0/status", tags=["Detector Status"])


@router.get("/state")
def get_detector_state():
    return {"value": "idle"}
