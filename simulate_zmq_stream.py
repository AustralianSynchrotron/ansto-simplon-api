import logging
import time

import bitshuffle
import cbor2
import h5py
import hdf5plugin  # noqa
import lz4.frame
import numpy as np
import zmq
from tqdm import tqdm, trange

from parse_master_file import Parse

logging.basicConfig(level=logging.DEBUG)


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
            Time delay between images sent via the ZeroMQ stream


        Returns
        -------
        None
        """

        self.address = address
        self.hdf5_file_path = hdf5_file_path
        self.compression = compression
        self.delay_between_frames = delay_between_frames

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.bind(self.address)

        self._sequence_id = 0

        logging.info("Loading dataset...")
        self.frames = self.create_list_of_compressed_frames(
            self.hdf5_file_path, self.compression
        )
        logging.info("Dataset loaded")

    def create_list_of_compressed_frames(
        self, hdf5_file_path: str, compression: str
    ) -> list[bytes]:
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
        Exception
            If the compression algorithm is not bslz4 or lz4

        Returns
        -------
        frame_list : list[bytes]
            A list containing an encoded dictionary of compressed frames, and
            frame metadata
        """

        hdf5_file = h5py.File(hdf5_file_path)
        key = list(hdf5_file["entry"]["data"].keys())[0]

        frame_array = np.array(hdf5_file["entry"]["data"][key])

        # Would make more sense in the __init__ section
        # but then we'd need to read the file twice
        self.start_message, self.image_message, self.end_message = Parse(
            hdf5_file
        ).header()

        # Delete the hdf5_file, we got what we needed
        del hdf5_file

        # FIXME: We just need one frome for rastering
        # number_of_frames = frame_array.shape[0]
        number_of_frames = 1
        array_shape = frame_array[0].shape
        dtype = frame_array.dtype

        frame_list = []
        if compression == "lz4":
            logging.info("Compression type: {self.compression}. Compressing data...")

            for ii in trange(number_of_frames):
                image = lz4.frame.compress(frame_array[ii])
                # Copy image message template
                image_message = self.image_message
                # Fill in missing bits.
                image_message["channels"][0]["data"] = image
                image_message["channels"][0]["compression"] = "lz4"
                image_message["channels"][0]["data_type"] = str(dtype)
                image_message["channels"][0]["array_shape"] = array_shape

                frame_list.append(image_message)

        elif compression == "bslz4":
            logging.info("Compression type: {self.compression}. Compressing data...")

            for ii in trange(number_of_frames):
                image = bitshuffle.compress_lz4(frame_array[ii]).tobytes()
                image_message = self.image_message
                # Fill in missing bits.
                image_message["channels"][0]["data"] = image
                image_message["channels"][0]["compression"] = "bslz4"
                image_message["channels"][0]["data_type"] = str(dtype)
                image_message["channels"][0]["array_shape"] = array_shape

                frame_list.append(image_message)

        else:
            raise Exception("The allowed compression types are lz4 and bslz4")

        return frame_list

    def stream_frames(self, compressed_image_list: list[bytes]) -> None:
        """Send images through a ZeroMQ stream

        Parameters
        ----------
        compressed_image_list : list[bytes]
            A list of compressed frames

        Returns
        -------
        None
        """

        logging.info("sending frames...")
        t = time.time()
        for image in tqdm(compressed_image_list):
            time.sleep(self.delay_between_frames)

            # Add series number
            image["series_number"] = self.sequence_id
            self.socket.send(cbor2.dumps(image))

        frame_rate = len(compressed_image_list) / (time.time() - t)
        logging.info(f"Frame rate: {frame_rate} frames / s")

    def stream_start_message(self) -> None:
        """
        Send start message through a ZeroMQ Stream

        Returns
        -------
        None
        """

        logging.info("Sending start message")
        logging.debug(self.start_message)
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
        logging.debug(self.end_message)
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
