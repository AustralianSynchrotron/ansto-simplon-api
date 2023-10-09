import logging
import struct
import time
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from os import environ
from typing import Any

import bitshuffle
import cbor2
import h5py
import hdf5plugin  # noqa
import numpy as np
import numpy.typing as npt
import zmq
from tqdm import trange

from .parse_master_file import Parse
from .schemas.configuration import ZMQStartMessage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)

zmq_start_message = ZMQStartMessage()


class ZmqStream:
    """
    Class used to stream data through a ZeroMQ stream by reading a HDF5 file.
    Frames are compressed using the lz4 or bslz4 compression algorithms before they
    are sent through the ZeroMQ stream
    """

    def __init__(
        self,
        address: str,
        hdf5_file_path: str,
        delay_between_frames: float = 0.1,
        number_of_data_files: int = 1,
        number_of_frames_per_trigger: int = 200,
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
        number_of_frames_per_trigger : int, optional
            Number of frames per trigger

        Returns
        -------
        None
        """

        self.address = address
        self.compression = "bslz4"
        self.delay_between_frames = delay_between_frames
        self.number_of_data_files = number_of_data_files
        self.number_of_frames_per_trigger = number_of_frames_per_trigger

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.bind(self.address)

        self._sequence_id = 0

        self.frame_id = 0

        self.image_number = 0  # used to mimic the dectris image number

        self.user_data = ""  # an empty string is the real default value
        self.series_unique_id = None
        self.frames = None
        self.hdf5_file_path = hdf5_file_path

        logging.info(f"ZMQ Address: {self.address}")
        logging.info(f"Hdf5 file path: {self.hdf5_file_path}")
        logging.info(f"Compression type: {self.compression}")
        logging.info(f"Delay between frames (s): {self.delay_between_frames}")
        logging.info(f"Number of data files: {self.number_of_data_files}")

    def create_list_of_compressed_frames(
        self, hdf5_file_path: str, compression: str
    ) -> list[dict]:
        """
        Creates a list of compressed frames from a hdf5 file

        Parameters
        ----------
        hdf5_file_path : str
            Path of the hdf5 file
        compression : str
            Compression type. Accepted compression types are lz4 and bslz4.
            Default value is bslz4

        Raises
        ------
        NotImplementedError
            If the compression algorithm is not bslz4, lz4, or no_compression

        Returns
        -------
        frame_list : list[dict]
            A list containing a dictionary of compressed frames, and
            frame metadata
        """

        hdf5_file = h5py.File(hdf5_file_path)
        keys = list(hdf5_file["entry"]["data"].keys())

        datafile_list: list[npt.NDArray] = [
            np.array(hdf5_file["entry"]["data"][keys[i]])
            for i in range(self.number_of_data_files)
        ]

        # Would make more sense in the __init__ section
        # but then we'd need to read the file twice
        self.start_message, self.image_message, self.end_message = Parse(
            hdf5_file
        ).header()

        # Delete the hdf5_file, we got what we needed
        hdf5_file.close()
        del hdf5_file

        number_of_frames_per_data_file = [
            datafile.shape[0] for datafile in datafile_list
        ]
        array_shape = datafile_list[0].shape[1:]
        dtype = datafile_list[0].dtype

        frame_list = []

        for jj in range(self.number_of_data_files):
            logging.info(f"Loading data file {jj}:")
            logging.info(f"Compression type: {self.compression}. Compressing data...")
            for ii in trange(number_of_frames_per_data_file[jj]):
                image_message = deepcopy(self.image_message)
                # if compression == "lz4":
                #    image = lz4.frame.compress(datafile_list[jj][ii])
                #    # image_message["data"]["threshold_1"]["compression"] = "lz4"
                if compression.lower() == "bslz4":
                    image = bitshuffle.compress_lz4(datafile_list[jj][ii]).tobytes()
                    image_contents = self.create_image_cbor_object(
                        image, str(dtype), array_shape
                    )

                elif compression.lower() == "none":
                    image = datafile_list[jj][ii].tobytes()
                    image_contents = self.create_image_cbor_object(
                        image, str(dtype), array_shape, compressed_image=False
                    )
                else:
                    raise NotImplementedError(
                        "The allowed compression types are lz4, bslz4 and "
                        f"no_compression, not {compression}"
                    )

                data = cbor2.CBORTag(40, [array_shape, image_contents])
                image_message["data"]["threshold_1"] = data

                frame_list.append(image_message)

                del image_message

        logging.info(f"Number of unique frames: {len(frame_list)}")
        del datafile_list
        return frame_list

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

        bytes_number_of_elements = struct.pack(
            ">q", (shape[0] * shape[1] * element_size)
        )
        # TODO: There's probably a way to write the bytes_block_size with
        # the struct library
        bytes_block_size = b"\x00\x00 \x00"

        byte_array = bytes_number_of_elements + bytes_block_size + image

        image_obj = cbor2.CBORTag(56500, [self.compression, element_size, byte_array])

        image_contents = cbor2.CBORTag(tag, image_obj)

        return image_contents

    def stream_frames(self, compressed_image_list: list[dict]) -> None:
        """Send images through a ZeroMQ stream

        Parameters
        ----------
        compressed_image_list : list[dict]
            A list of dictionaries containing compressed frames and metadata

        Returns
        -------
        None
        """
        logging.info("Sending frames")
        t = time.time()
        for _ in trange(self.number_of_frames_per_trigger):
            time.sleep(self.delay_between_frames)
            try:
                # Add series number
                compressed_image_list[self.frame_id]["series_id"] = self.sequence_id
                compressed_image_list[self.frame_id]["image_id"] = self.image_number
                compressed_image_list[self.frame_id]["series_date"] = datetime.now(
                    tz=timezone.utc
                )
                compressed_image_list[self.frame_id]["stop_time"] = [50000000, 50000000]
                compressed_image_list[self.frame_id][
                    "series_unique_id"
                ] = self.series_unique_id

                self.socket.send(cbor2.dumps(compressed_image_list[self.frame_id]))
                self.frame_id += 1
                self.image_number += 1
            except IndexError:
                self.frame_id = 0
                compressed_image_list[self.frame_id]["series_id"] = self.sequence_id
                compressed_image_list[self.frame_id]["image_id"] = self.image_number
                compressed_image_list[self.frame_id]["series_date"] = datetime.now(
                    tz=timezone.utc
                )
                compressed_image_list[self.frame_id]["stop_time"] = [50000000, 50000000]
                compressed_image_list[self.frame_id][
                    "series_unique_id"
                ] = self.series_unique_id

                self.socket.send(cbor2.dumps(compressed_image_list[self.frame_id]))

                self.frame_id += 1
                self.image_number += 1

        frame_rate = self.number_of_frames_per_trigger / (time.time() - t)
        logging.info(f"Frame rate: {frame_rate} frames / s")

    def stream_start_message(self) -> None:
        """
        Send start message through a ZeroMQ Stream

        Returns
        -------
        None
        """
        self.series_unique_id = str(uuid.uuid4())

        logging.info("Sending start message")
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

        logging.info("Sending end message")
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
        self.stream_frames(self.frames)
        self.stream_end_message()

    @property
    def sequence_id(self) -> int:
        """
        Gets the sequence_id

        Returns
        -------
        self._sequence_id: int
            The sequence_id
        """
        return self._sequence_id

    @sequence_id.setter
    def sequence_id(self, value: int) -> None:
        """
        Sets the sequence_id

        Returns
        -------
        None
        """
        self._sequence_id = value

    @property
    def image_number(self) -> int:
        """
        Gets the image_number

        Returns
        -------
        self._image_number: int
            The image_number
        """
        return self._image_number

    @image_number.setter
    def image_number(self, value: int) -> None:
        """
        Sets the image_number

        Returns
        -------
        None
        """
        self._image_number = value

    @property
    def number_of_frames_per_trigger(self) -> None:
        """
        Sets the number of frames per trigger

        Returns
        -------
        None
        """
        return self._number_of_frames_per_trigger

    @number_of_frames_per_trigger.setter
    def number_of_frames_per_trigger(self, value: int) -> None:
        """
        Sets the image_number

        Parameters
        ----------
        value : int
            The number of frames per trigger

        Returns
        -------
        None
        """
        self._number_of_frames_per_trigger = value
        logging.info(f"nimages set to: {value}")

    @property
    def user_data(self) -> Any:
        """
        Gets the user data

        Returns
        -------
        self._user_data : Any
            The user data
        """
        return self._user_data

    @user_data.setter
    def user_data(self, value: Any) -> None:
        """
        Sets the user data

        Parameters
        ----------
        value : Any
            New value

        Returns
        -------
        None
        """
        self._user_data = value

    @property
    def compression(self) -> str:
        """
        Gets the compression type

        Returns
        -------
        self._user_data : Any
            The user data
        """
        return self._compression

    @compression.setter
    def compression(self, value: str) -> None:
        """
        Sets the compression type

        Parameters
        ----------
        value : str
            New value

        Returns
        -------
        None
        """
        allowed_compressions = ["bslz4", "none"]
        if value.lower() in allowed_compressions:
            self._compression = value
            try:
                self.frames = self.create_list_of_compressed_frames(
                    self.hdf5_file_path, self.compression
                )
            except AttributeError:
                pass
        else:
            raise ValueError(
                "Allowed compressions are bslz4 and none only" f"not {value}"
            )

    @property
    def hdf5_file_path(self) -> str:
        """
        Gets the hdf5_file_path

        Returns
        -------
        self._hdf5_file_path : str
            The hdf5 file name
        """
        return self._hdf5_file_path

    @hdf5_file_path.setter
    def hdf5_file_path(self, value: str) -> None:
        """
        Sets the hdf5 file name and loads frames from the HDF5 file into memory

        Parameters
        ----------
        value : str
            The hdf5 filename
        """
        logging.info("Loading dataset...")
        self._hdf5_file_path = value
        self.frames = self.create_list_of_compressed_frames(
            self._hdf5_file_path, self.compression
        )
        logging.info("Dataset loaded")


ZMQ_ADDRESS = environ.get("ZMQ_ADDRESS", "tcp://*:5555")
try:
    HDF5_MASTER_FILE = environ["HDF5_MASTER_FILE"]
except KeyError:
    raise KeyError(
        "No HDF5 master file found. Set the absolute path of the HDF5 master file via the "
        "HDF5_MASTER_FILE environment variable"
    )

DELAY_BETWEEN_FRAMES = float(environ.get("DELAY_BETWEEN_FRAMES", "0.1"))
NUMBER_OF_DATA_FILES = int(environ.get("NUMBER_OF_DATA_FILES", "1"))
NUMBER_OF_FRAMES_PER_TRIGGER = int(environ.get("NUMBER_OF_FRAMES_PER_TRIGGER", "1"))

zmq_stream = ZmqStream(
    address=ZMQ_ADDRESS,
    hdf5_file_path=HDF5_MASTER_FILE,
    delay_between_frames=DELAY_BETWEEN_FRAMES,
    number_of_data_files=NUMBER_OF_DATA_FILES,
    number_of_frames_per_trigger=NUMBER_OF_FRAMES_PER_TRIGGER,
)
