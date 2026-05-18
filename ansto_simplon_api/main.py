import importlib
import importlib.util

from fastapi import FastAPI
from fastapi.exception_handlers import http_exception_handler
from fastapi.logger import logger
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import __version__
from .config import get_settings
from .routes.ansto_endpoints.ansto_endpoints import router as ansto_endpoints
from .routes.detector.command import router as command
from .routes.detector.config import router as detector_config
from .routes.status.status import router as status
from .routes.stream.config import router as stream_config

config = get_settings()


def _should_enable_dynamic_frame_routes() -> bool:
    if not config.DYNAMIC_FRAME_ENABLED:
        return False

    has_pyfai = importlib.util.find_spec("pyFAI") is not None
    if not has_pyfai:
        raise RuntimeError(
            "AS_DYNAMIC_FRAME_ENABLED is true but pyFAI is not installed"
        )

    return True


_description: str
with open(config.README, "r") as _file:
    _description = _file.read()


app = FastAPI(
    title=config.API_APP_NAME,
    description=_description,
    version=__version__,
    docs_url=config.API_DOCS_URL,
    redoc_url=config.API_REDOC_URL,
    openapi_url=config.API_OPENAPI_URL,
)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    """Catch any HTTPException and log the error"""
    logger.error(f"{str(exc)}\n{exc.detail}", exc_info=exc)
    return await http_exception_handler(request, exc)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(config.API_FAVICON)


app.include_router(command)
app.include_router(stream_config)
app.include_router(detector_config)
app.include_router(status)
app.include_router(ansto_endpoints)

if _should_enable_dynamic_frame_routes():
    dynamic_module = importlib.import_module(
        "ansto_simplon_api.routes.ansto_endpoints.dynamic_frame"
    )
    app.include_router(dynamic_module.router)


@app.get("/")
def home():
    return {"ANSTO SIMPLON API": "Home"}
