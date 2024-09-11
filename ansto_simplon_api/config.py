from functools import lru_cache
from os.path import dirname as os_dirname, join as os_joinpath, realpath as os_realpath
from pathlib import Path
from typing import Annotated, Self

from pydantic import Field, FilePath, GetPydanticSchema, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

__all__ = ("Settings", "get_settings")

CUR_DIR = os_dirname(os_realpath(__file__))


class APISettings(BaseSettings):
    """API Settings"""

    API_APP_NAME: str = Field(
        title="App Name",
        default="Simulated Simplon API",
    )
    API_DOCS_URL: str | None = Field(
        title="OpenAPI Docs Path",
        default=None,
    )
    API_REDOC_URL: str | None = Field(
        title="ReDocs Path",
        default=None,
    )
    API_OPENAPI_URL: str | None = Field(
        title="OpenAPI Path",
        default=None,
    )
    API_FAVICON: FilePath = Field(
        title="Favicon Image",
        default=os_realpath(os_joinpath(CUR_DIR, "./favicon.ico")),
    )
    API_KEY: SecretStr | None = Field(
        title="Service API-Key",
        default=None,
    )


class ZMQStreamSettings(BaseSettings):
    """ZMQ Stream Settings"""

    ZMQ_ADDRESS: str = Field(
        title="ZMQ Address",
        default="tcp://*:5555",
    )
    HDF5_MASTER_FILE: Annotated[
        str,
        GetPydanticSchema(lambda _, _h: _h.generate_schema(FilePath)),
    ] = Field(
        title="HDF5 Master File",
        default=os_realpath(
            os_joinpath(CUR_DIR, "master_file_examples", "example_1_master.h5")
        ),
    )
    DELAY_BETWEEN_FRAMES: float = Field(
        title="Delay Between Frames",
        default=0.01,
    )
    NUMBER_OF_DATA_FILES: int = Field(
        title="Number of Data Files",
        default=1,
    )


class Settings(APISettings, ZMQStreamSettings):
    README: FilePath = Field(
        title="ReadMe",
        default=os_realpath(os_joinpath(CUR_DIR, "../README.md")),
        validate_default=True,
    )
    PYPROJECT: FilePath = Field(
        title="PyProject",
        default=os_realpath(os_joinpath(CUR_DIR, "../pyproject.toml")),
        validate_default=True,
    )
    BUILD_INFO: Path = Field(
        title="Build Info",
        default=os_realpath(os_joinpath(CUR_DIR, "../.build_info.json")),
        validate_default=True,
    )

    model_config = SettingsConfigDict(
        str_strip_whitespace=True,
        env_prefix="AS_",
        env_file=".env",
        validate_assignment=True,
    )

    @classmethod
    def settings_customise_sources(
        cls: type[Self],
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Restrict settings sources to environment variables only
        return (env_settings, dotenv_settings)


@lru_cache()
def get_settings() -> Settings:
    """Cache the settings, this allows the settings to be used in dependencies and
    for overwriting in tests
    """
    return Settings()  # pyright: ignore[reportCallIssue]
