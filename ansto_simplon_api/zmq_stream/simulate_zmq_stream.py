# mypy: disable-error-code="import-untyped"

import logging
import struct
import time
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Literal

import bitshuffle
import cbor2
import h5py
import hdf5plugin  # noqa
import numpy as np
import numpy.typing as npt
from tqdm import trange

from ..config import FrameSourceEnum, get_settings
from ..schemas.stream import LegacyFrame
from .dynamic_frame import build_dynamic_frame_cache_key, generate_dynamic_image
from .legacy_stream import LegacyStream, zmq_start_message
from .parse_master_file import Parse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)

config = get_settings()


class ZmqStream(LegacyStream):
    """
    Class used to stream data through a ZeroMQ stream by reading a HDF5 file or
    generating frames dynamically, based on detector geometry and wavelength.
    Frames are compressed using the bslz4 compression algorithms before they
    are sent through the ZeroMQ stream.
    For the HDF5 source, both legacy and CBOR stream formats are supported.
    """

    def __init__(
        self,
        address: str,
        hdf5_file_path: str,
        delay_between_frames: float = 0.1,
        number_of_data_files: int = 1,
        frame_source: FrameSourceEnum = FrameSourceEnum.HDF5,
    ) -> None:
        """
        Parameters
        ----------
        address : str
            ZMQ stream address, e.g. tcp://*:5555
        hdf5_file_path : str
            Path of the hdf5 file
        delay_between_frames : float, optional
            Time delay between images sent via the ZeroMQ stream [seconds]
        number_of_data_files : int, optional
            Number of data files loaded in memory
        frame_source : FrameSourceEnum, optional
            The source of frames for the ZMQ stream. Allowed values are
            FrameSourceEnum.HDF5 and FrameSourceEnum.DYNAMIC_FRAME.
            Defaults to FrameSourceEnum.HDF5

        Returns
        -------
        None
        """

        super().__init__(
            compression="bslz4",
            sequence_id=0,
            number_of_frames_per_trigger=1,
            delay_between_frames=delay_between_frames,
            address=address,
            user_data="",
        )

        self.number_of_data_files = number_of_data_files

        self.frame_id = 0

        self.image_number = 0  # used to mimic the dectris image number

        self.series_unique_id = "0"
        self.hdf5_file_path = hdf5_file_path
        self.frame_source = frame_source
        self._dynamic_frame_cache_key: tuple | None = None
        self._dynamic_frame_cache_frame: dict | None = None

        if self.frame_source == FrameSourceEnum.HDF5:
            self.create_list_of_compressed_frames(
                self.hdf5_file_path, self.compression, self.number_of_data_files
            )
        else:
            if not self._dynamic_frame_available():
                raise RuntimeError(
                    "dynamic-frame startup requires pyFAI, which is not available."
                )
            self._load_master_stream_messages(self.hdf5_file_path)

        logging.info(f"ZMQ Address: {self.address}")
        logging.info(f"Hdf5 file path: {self.hdf5_file_path}")
        logging.info(f"Compression type: {self.compression}")
        logging.info(f"Delay between frames (s): {self.delay_between_frames}")
        logging.info(f"Number of data files: {self.number_of_data_files}")

    def _load_master_stream_messages(self, hdf5_file_path: str | Path) -> None:
        """Load stream2 message templates from the master file metadata."""
        with h5py.File(hdf5_file_path, mode="r") as hdf5_file:
            self.start_message, self.image_message, self.end_message = Parse(
                hdf5_file
            ).header()
            self._update_zmq_start_message()
            self._update_detector_configuration(hdf5_file)

    def _update_zmq_start_message(self) -> None:
        """
        Updates the ZMQ start message with values derived from the master file
        loaded into the Simplon API.

        Returns
        -------
        None
        """
        for key, val in self.start_message.items():
            setattr(zmq_start_message, key, val)

    def _get_hdf5_value(self, hf: h5py.File, path: str) -> npt.NDArray | bytes:
        """
        Gets a value from a hdf5 file

        Parameters
        ----------
        hf : h5py.File
            A hdf5 file
        path : str
            Path to the dataset within the hdf5 file

        Returns
        -------
        npt.NDArray | bytes
            The value of the dataset

        Raises
        ------
        KeyError
            If the path does not exist or is not a dataset
        """
        obj = hf.get(path)
        if obj is None:
            raise KeyError(path)
        if isinstance(obj, h5py.Dataset):
            return obj[()]
        raise KeyError(f"Path is not a dataset: {path}")

    def _get_hdf5_group(self, hf: h5py.File, path: str) -> h5py.Group:
        """
        Gets a group from a hdf5 file

        Parameters
        ----------
        hf : h5py.File
            A hdf5 file
        path : str
            Path to the group within the hdf5 file

        Returns
        -------
        h5py.Group
            The group at the specified path

        Raises
        ------
        KeyError
            If the path does not exist or is not a group
        """
        obj = hf.get(path)
        if obj is None:
            raise KeyError(path)
        elif isinstance(obj, h5py.Group):
            return obj
        raise KeyError(f"Path is not a group: {path}")

    def _update_detector_configuration(self, hf: h5py.File) -> None:
        """
        Updates the detector configuration by reading the detector
        config from a hdf5 file

        Parameters
        ----------
        hf : h5py.File
            A hdf5 file

        Returns
        -------
        None
        """
        try:
            readout_time = self._get_hdf5_value(
                hf, "/entry/instrument/detector/detector_readout_time"
            )
            self.detector_config.detector_readout_time = float(readout_time)

            bit_depth_image = self._get_hdf5_value(
                hf, "/entry/instrument/detector/bit_depth_image"
            )
            self.detector_config.detector_bit_depth_image = int(bit_depth_image)

            bit_depth_readout = self._get_hdf5_value(
                hf, "/entry/instrument/detector/bit_depth_readout"
            )
            self.detector_config.detector_bit_depth_readout = int(bit_depth_readout)

            compression = self._get_hdf5_value(
                hf, "/entry/instrument/detector/detectorSpecific/compression"
            )
            if isinstance(compression, bytes):
                compression_str = compression.decode()
                if compression_str == "bslz4":
                    self.detector_config.detector_compression = "bslz4"
                elif compression_str == "none":
                    self.detector_config.detector_compression = "none"

            cutoff = self._get_hdf5_value(
                hf,
                "/entry/instrument/detector/detectorSpecific/countrate_correction_count_cutoff",
            )
            self.detector_config.detector_countrate_correction_cutoff = int(cutoff)

            software_version = self._get_hdf5_value(
                hf, "/entry/instrument/detector/detectorSpecific/software_version"
            )
            if isinstance(software_version, bytes):
                self.detector_config.software_version = str(software_version.decode())

            eiger_fw_version = self._get_hdf5_value(
                hf, "/entry/instrument/detector/detectorSpecific/eiger_fw_version"
            )
            if isinstance(eiger_fw_version, bytes):
                self.detector_config.eiger_fw_version = str(eiger_fw_version.decode())

        except KeyError:
            logging.warning(
                "Detector configuration could not be loaded. Using detector "
                "configuration defaults"
            )

    def create_list_of_compressed_frames(
        self,
        hdf5_file_path: str | Path,
        compression: Literal["bslz4", "none"],
        number_of_datafiles: int,
    ) -> None:
        """
        Creates a list of compressed frames from a hdf5 file

        Parameters
        ----------
        hdf5_file_path : str
            Path of the hdf5 file
        compression : str
            Compression type. Accepted compression types are lz4 and bslz4.
            Default value is bslz4
        number_of_datafiles: int | None = None
            The number of datafiles loaded in memory. If number_of_datafiles=None,
            we load all datafiles specified in the master file

        Raises
        ------
        NotImplementedError
            If the compression algorithm is not bslz4, lz4, or no_compression

        Returns
        -------
        None
        """
        self.hdf5_file_path = str(hdf5_file_path)
        self.compression = compression
        self.number_of_data_files = number_of_datafiles
        self.frame_source = FrameSourceEnum.HDF5

        with h5py.File(hdf5_file_path, mode="r") as hdf5_file:
            raw_data_group = self._get_hdf5_group(hdf5_file, "/entry/data")
            keys = list(raw_data_group.keys())

            datafile_list: list[npt.NDArray] = [
                np.array(raw_data_group[keys[i]])
                for i in range(self.number_of_data_files)
            ]

            self.start_message, self.image_message, self.end_message = Parse(
                hdf5_file
            ).header()
            self._update_zmq_start_message()
            self._update_detector_configuration(hdf5_file)

        self.number_of_frames_per_trigger = zmq_start_message.number_of_images

        number_of_frames_per_data_file = [
            datafile.shape[0] for datafile in datafile_list
        ]
        array_shape = datafile_list[0].shape[1:]

        zmq_start_message.image_size_x = array_shape[1]
        zmq_start_message.image_size_y = array_shape[0]

        dtype = datafile_list[0].dtype
        zmq_start_message.image_dtype = str(dtype)

        frame_list = []
        legacy_frame_list: list[LegacyFrame] = []
        legacy_encoding = self._legacy_encoding(np.dtype(dtype))

        for jj in range(self.number_of_data_files):
            logging.info(f"Loading data file {jj}:")
            logging.info(f"Compression type: {self.compression}. Compressing data...")
            for ii in trange(number_of_frames_per_data_file[jj]):
                image_message: dict[str, Any] = deepcopy(self.image_message)
                # if compression == "lz4":
                #    image = lz4.frame.compress(datafile_list[jj][ii])
                #    # image_message["data"]["threshold_1"]["compression"] = "lz4"
                if compression.lower() == "bslz4":
                    image = bitshuffle.compress_lz4(datafile_list[jj][ii]).tobytes()
                    image_contents = self.create_image_cbor_object(
                        image, str(dtype), array_shape
                    )
                    legacy_image = self.create_dectris_compression_payload(
                        image,
                        element_size=int(dtype.itemsize),
                        shape=array_shape,
                    )

                elif compression.lower() == "none":
                    image = datafile_list[jj][ii].tobytes()
                    image_contents = self.create_image_cbor_object(
                        image, str(dtype), array_shape, compressed_image=False
                    )
                    legacy_image = image
                else:
                    raise NotImplementedError(
                        "The allowed compression types are lz4, bslz4 and "
                        f"no_compression, not {compression}"
                    )

                legacy_frame_list.append(
                    LegacyFrame(
                        data=legacy_image,
                        dtype=str(dtype),
                        encoding=legacy_encoding,
                        size=len(legacy_image),
                    )
                )

                data = cbor2.CBORTag(40, [array_shape, image_contents])
                image_message["data"]["threshold_1"] = data

                frame_list.append(image_message)

                del image_message

        logging.info(f"Number of unique frames: {len(frame_list)}")
        del datafile_list
        self.frames = frame_list
        self.legacy_frames = legacy_frame_list

    def set_frame_source(self, frame_source: FrameSourceEnum) -> None:
        """Set the frame source used by stream_frames."""
        # TODO only allow changing frame source if AS_DYNAMIC_FRAME_ENABLED is true
        if (
            frame_source == FrameSourceEnum.DYNAMIC_FRAME
            and not self._dynamic_frame_available()
        ):
            raise RuntimeError(
                "dynamic-frame mode requires pyFAI. Install optional dependency: "
                "pip install 'ansto-simplon-api[dynamic-frame]'"
            )

        self.frame_source = frame_source
        self.frame_id = 0

    def _dynamic_frame_available(self) -> bool:
        return find_spec("pyFAI") is not None

    def _current_dynamic_frame_cache_key(self) -> tuple:
        return build_dynamic_frame_cache_key(
            start_message=zmq_start_message,
            compression=self.compression,
        )

    def _build_dynamic_frame(self) -> dict:
        dtype = np.dtype(zmq_start_message.image_dtype)
        image_array = generate_dynamic_image(zmq_start_message)

        if self.compression.lower() == "bslz4":
            image = bitshuffle.compress_lz4(image_array).tobytes()
            image_contents = self.create_image_cbor_object(
                image,
                str(dtype),
                image_array.shape,
            )
        elif self.compression.lower() == "none":
            image = image_array.tobytes()
            image_contents = self.create_image_cbor_object(
                image,
                str(dtype),
                image_array.shape,
                compressed_image=False,
            )
        else:
            raise NotImplementedError(
                "The allowed compression types are bslz4 and none, "
                f"not {self.compression}"
            )

        image_message: dict[str, Any] = deepcopy(self.image_message)
        image_data = image_message["data"]
        image_data["threshold_1"] = cbor2.CBORTag(
            40, [image_array.shape, image_contents]
        )
        return image_message

    def _get_dynamic_frame(self) -> dict:
        key = self._current_dynamic_frame_cache_key()
        if (
            self._dynamic_frame_cache_key != key
            or self._dynamic_frame_cache_frame is None
        ):
            logging.info("Dynamic frame cache invalidated, regenerating image")
            self._dynamic_frame_cache_frame = self._build_dynamic_frame()
            self._dynamic_frame_cache_key = key

        return dict(self._dynamic_frame_cache_frame)

    def _send_cbor_frame(self, frame: dict) -> None:
        frame["series_id"] = self.sequence_id
        frame["image_id"] = self.image_number
        frame["series_date"] = datetime.now(tz=timezone.utc)
        frame["stop_time"] = [50000000, 50000000]
        frame["series_unique_id"] = self.series_unique_id

        self.socket.send(cbor2.dumps(frame))
        self.frame_id += 1
        self.image_number += 1

    def _stream_dynamic_frames(self) -> None:
        logging.info(f"Sending dynamic frames to {self.address}")
        t = time.time()

        for _ in trange(self.number_of_frames_per_trigger):
            frame = self._get_dynamic_frame()
            self._send_cbor_frame(frame)
            time.sleep(self.delay_between_frames)

        frame_rate = self.number_of_frames_per_trigger / (time.time() - t)
        logging.info(f"Frame rate: {frame_rate} frames / s")

    def create_dectris_compression_payload(
        self,
        image: bytes,
        element_size: int,
        shape: tuple[int, int],
    ) -> bytes:
        """
        Adds the Dectris compression header to a compressed payload.
        This is used for both cbor and legacy stream formats.

        Parameters
        ----------
        image : bytes
            The compressed image in bytes format
        element_size : int
            The element size, e.g. 4 for uint32
        shape : tuple[int, int]
            The (x,y) shape of the image

        Returns
        -------
        bytes
            The compressed image with the Dectris compression header
        """
        bytes_number_of_elements = struct.pack(
            ">q", (shape[0] * shape[1] * element_size)
        )
        bytes_block_size = b"\x00\x00 \x00"
        return bytes_number_of_elements + bytes_block_size + image

    def create_image_cbor_object(
        self,
        image: bytes,
        dtype: str,
        shape: tuple[int, int],
        compressed_image: bool = True,
    ) -> cbor2.CBORTag | bytes:
        """
        Creates a cbor object containing a compressed frame and frame metadata.
        Here we additionally add the bytes-header necessary to
        1) use the dectris decompression library, and 2) write datafiles directly to
        disk without having to decompress frames.

        Parameters
        ----------
        image : bytes
            A compressed or uncompressed image in bytes format
        dtype : str
            Data type, e.g. 'uint32'
        shape : tuple[int, int]
            Shape of the array

        Returns
        -------
        cbor2.CBORTag
            A cbor2.CBORTag object containing the compressed or uncompressed image.
            If the image is compressed, we add metadata which includes the compression
            type and element size.

        Raises
        ------
        NotImplementedError
            An error if the data type is not uint32 or uint16
        """
        if dtype == "uint32":
            element_size = 4
            tag = 70
        elif dtype == "uint16":
            element_size = 2
            tag = 69
        else:
            raise NotImplementedError(
                f"Supported types are uint32 and uint16, not {dtype}"
            )

        if not compressed_image:
            return cbor2.CBORTag(tag, image)

        byte_array = self.create_dectris_compression_payload(
            image,
            element_size=element_size,
            shape=shape,
        )

        image_obj = cbor2.CBORTag(56500, [self.compression, element_size, byte_array])

        image_contents = cbor2.CBORTag(tag, image_obj)

        return image_contents

    def stream_frames(self, compressed_image_list: list[dict] | None = None) -> None:
        """Send images through a ZeroMQ stream

        Parameters
        ----------
        compressed_image_list : list[dict] | None
            A list of dictionaries containing CBOR stream2 image messages.
            Ignored when `stream_config.format == "legacy"`.

        Returns
        -------
        None
        """
        if not self._stream_enabled():
            return

        if self.stream_config.format == "legacy":
            if self.frame_source == FrameSourceEnum.DYNAMIC_FRAME:
                raise RuntimeError(
                    "dynamic-frame source is supported only when stream format is cbor"
                )
            self._legacy_stream_frames(self.legacy_frames)
            return

        if self.frame_source == FrameSourceEnum.DYNAMIC_FRAME:
            self._stream_dynamic_frames()
            return

        if compressed_image_list is None:
            compressed_image_list = self.frames

        logging.info(f"Sending frames to {self.address}")
        t = time.time()
        for _ in trange(self.number_of_frames_per_trigger):
            time.sleep(self.delay_between_frames)
            try:
                self._send_cbor_frame(compressed_image_list[self.frame_id])
            except IndexError:
                self.frame_id = 0
                self._send_cbor_frame(compressed_image_list[self.frame_id])

        frame_rate = self.number_of_frames_per_trigger / (time.time() - t)
        logging.info(f"Frame rate: {frame_rate} frames / s")

    def stream_start_message(self) -> None:
        """
        Send start message through a ZeroMQ Stream

        Returns
        -------
        None
        """
        if not self._stream_enabled():
            return

        if self.stream_config.format == "legacy":
            if self.frame_source == FrameSourceEnum.DYNAMIC_FRAME:
                raise RuntimeError(
                    "dynamic-frame source is supported only when stream format is cbor"
                )
            self._legacy_stream_start_message()
            return

        self.series_unique_id = str(uuid.uuid4())

        logging.info(f"Sending start message to {self.address}")
        zmq_start_message.series_id = self.sequence_id
        zmq_start_message.number_of_images = self.number_of_frames_per_trigger
        zmq_start_message.user_data = self.user_data
        zmq_start_message.series_unique_id = self.series_unique_id

        message = cbor2.dumps(zmq_start_message.model_dump())
        self.socket.send(message)

    def stream_end_message(self) -> None:
        """
        Send end message through a ZeroMQ Stream

        Returns
        -------
        None
        """

        if not self._stream_enabled():
            return

        if self.stream_config.format == "legacy":
            if self.frame_source == FrameSourceEnum.DYNAMIC_FRAME:
                raise RuntimeError(
                    "dynamic-frame source is supported only when stream format is cbor"
                )
            self._legacy_stream_end_message()
            return

        logging.info(f"Sending end message to {self.address}")
        self.end_message["series_id"] = self.sequence_id
        self.end_message["series_unique_id"] = self.series_unique_id
        message = cbor2.dumps(self.end_message)
        self.socket.send(message)

    def start_stream(self) -> None:
        """
        Send frames, start and end messages through a ZeroMQ stream

        Returns
        -------
        None
        """

        self.stream_start_message()
        self.stream_frames()
        self.stream_end_message()


zmq_stream = ZmqStream(
    address=config.ZMQ_ADDRESS,
    hdf5_file_path=config.HDF5_MASTER_FILE,
    delay_between_frames=config.DELAY_BETWEEN_FRAMES,
    number_of_data_files=config.NUMBER_OF_DATA_FILES,
    frame_source=config.FRAME_SOURCE,
)
