import logging
import time
from copy import deepcopy

import bitshuffle
import cbor2
import h5py
import hdf5plugin  # noqa
import lz4.frame
import numpy as np
import zmq
from tqdm import trange

from parse_master_file import Parse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)


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
        compression: str = "bslz4",
        delay_between_frames: float = 0.1,
        raster_frames: bool = True,
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
        compression : str, optional
            Compression type. Accepted compression types are lz4 and bslz4.
            Default value is bslz4
        delay_between_frames : float, optional
            Time delay between images sent via the ZeroMQ stream [seconds]
        raster_frames : bool, optional
            If true, the sim-plon-api only sends one frame per trigger
        number_of_data_files : int, optional
            Number of data files loaded in memory
        number_of_frames_per_trigger : int, optional
            Number of frames per trigger

        Returns
        -------
        None
        """

        self.address = address
        self.hdf5_file_path = hdf5_file_path
        self.compression = compression
        self.delay_between_frames = delay_between_frames
        self.raster_frames = raster_frames
        self.number_of_data_files = number_of_data_files
        self.number_of_frames_per_trigger = number_of_frames_per_trigger

        logging.info(f"ZMQ Address: {self.address}")
        logging.info(f"Hdf5 file path: {self.hdf5_file_path}")
        logging.info(f"Compression type: {self.compression}")
        logging.info(f"Delay between frames (s): {self.delay_between_frames}")
        logging.info(f"Raster frames: {self.raster_frames}")
        logging.info(f"Number of data files: {self.number_of_data_files}")
        logging.info(
            f"Number of frames per trigger: {self.number_of_frames_per_trigger}"
        )

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.bind(self.address)

        self._sequence_id = 0

        self.frame_id = 0

        logging.info("Loading dataset...")
        self.frames = self.create_list_of_compressed_frames(
            self.hdf5_file_path, self.compression
        )
        logging.info("Dataset loaded")

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

        frame_list = []
        for i in range(self.number_of_data_files):
            frame_list.append(np.array(hdf5_file["entry"]["data"][keys[i]]))

        frame_array = np.array(frame_list)
        del frame_list

        # Would make more sense in the __init__ section
        # but then we'd need to read the file twice
        self.start_message, self.image_message, self.end_message = Parse(
            hdf5_file
        ).header()

        # Delete the hdf5_file, we got what we needed
        hdf5_file.close()
        del hdf5_file

        number_of_frames_per_data_file = frame_array.shape[1]
        array_shape = frame_array[0][0].shape
        dtype = frame_array.dtype

        frame_list = []

        for jj in range(self.number_of_data_files):
            logging.info(f"Loading data file {jj}:")
            logging.info(f"Compression type: {self.compression}. Compressing data...")
            for ii in trange(number_of_frames_per_data_file):
                image_message = deepcopy(self.image_message)
                if compression == "lz4":
                    image = lz4.frame.compress(frame_array[jj][ii])
                    image_message["channels"][0]["compression"] = "lz4"
                elif compression == "bslz4":
                    image = bitshuffle.compress_lz4(frame_array[jj][ii]).tobytes()
                    image_message["channels"][0]["compression"] = "bslz4"
                elif compression == "no_compression":
                    image = frame_array[jj][ii].tobytes()
                    image_message["channels"][0]["compression"] = "no_compression"
                else:
                    raise NotImplementedError(
                        "The allowed compression types are lz4, bslz4 and "
                        "no_compression"
                    )

                # Fill in missing bits.
                image_message["channels"][0]["data"] = image
                image_message["channels"][0]["data_type"] = str(dtype)
                image_message["channels"][0]["array_shape"] = array_shape

                frame_list.append(image_message)

        return frame_list

    def stream_frames(
        self, compressed_image_list: list[dict], raster_frames=True
    ) -> None:
        """Send images through a ZeroMQ stream

        Parameters
        ----------
        compressed_image_list : list[dict]
            A list of dictionaries containing compressed frames and metadata

        raster_frames : bool
            If true, the sim-plon-api only sends one frame per trigger

        Returns
        -------
        None
        """
        logging.info("Sending frames")
        if raster_frames:
            try:
                image = compressed_image_list[self.frame_id]
                logging.info(f"frame_id: {self.frame_id}")
                image["series_number"] = self.sequence_id
                self.socket.send(cbor2.dumps(image))

                self.frame_id += 1

            except IndexError:
                self.frame_id = 0
                image = compressed_image_list[self.frame_id]
                logging.info(f"frame_id: {self.frame_id}")
                image["series_number"] = self.sequence_id
                self.socket.send(cbor2.dumps(image))

                self.frame_id += 1

        else:
            t = time.time()
            for _ in trange(self.number_of_frames_per_trigger):
                time.sleep(self.delay_between_frames)
                try:
                    # Add series number
                    compressed_image_list[self.frame_id][
                        "series_number"
                    ] = self.sequence_id
                    self.socket.send(cbor2.dumps(compressed_image_list[self.frame_id]))
                    self.frame_id += 1

                except IndexError:
                    self.frame_id = 0
                    compressed_image_list[self.frame_id][
                        "series_number"
                    ] = self.sequence_id
                    self.socket.send(cbor2.dumps(compressed_image_list[self.frame_id]))

                    self.frame_id += 1

            frame_rate = self.number_of_frames_per_trigger / (time.time() - t)
            logging.info(f"Frame rate: {frame_rate} frames / s")

    def stream_start_message(self) -> None:
        """
        Send start message through a ZeroMQ Stream

        Returns
        -------
        None
        """

        logging.info("Sending start message")
        self.start_message["series_number"] = self.sequence_id
        message = cbor2.dumps(self.start_message)
        self.socket.send(message)

    def stream_end_message(self) -> None:
        """
        Send end message through a ZeroMQ Stream

        Returns
        -------
        None
        """

        logging.info("Sending end message")
        self.end_message["series_number"] = self.sequence_id
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
        self.stream_frames(self.frames, self.raster_frames)
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
