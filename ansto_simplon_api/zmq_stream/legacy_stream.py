import json
import logging
import sys
import time
import uuid
from typing import Literal

import numpy as np
import zmq
from tqdm import trange

from ..config import get_settings
from ..schemas.configuration import DetectorConfiguration
from ..schemas.stream import (
    LegacyConfigHeader,
    LegacyFrame,
    StreamConfiguration,
    ZMQStartMessage,
)

config = get_settings()

zmq_start_message = ZMQStartMessage()


class LegacyStream:
    """
    A class to handle the Dectris legacy stream format for the ZMQ stream
    """

    def __init__(
        self,
        compression: Literal["bslz4", "none"],
        sequence_id: int,
        number_of_frames_per_trigger: int,
        delay_between_frames: float,
        address: str,
        user_data: str | dict,
    ):
        """
        Parameters
        ----------
        compression : Literal["bslz4", "none"]
            The compression type. Allowed values are "bslz4" and "none".
        sequence_id : int
            The sequence id
        number_of_frames_per_trigger : int
            The number of frames to be sent per trigger
        delay_between_frames : float
            The delay between frames in seconds
        address : str
            The ZMQ address
        user_data : str | dict
            The user data to be sent in the start message
        """
        self.compression: Literal["bslz4", "none"] = compression
        self.sequence_id = sequence_id
        self.number_of_frames_per_trigger = number_of_frames_per_trigger
        self.delay_between_frames = delay_between_frames
        self.address = address
        self.detector_config = DetectorConfiguration()
        self.user_data = user_data

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.bind(self.address)
        self.stream_config = StreamConfiguration()

    def _legacy_stream_start_message(self) -> None:
        """
        Sends a start message through a ZMQ stream using the legacy stream format.

        Returns
        -------
        None
        """
        self.series_unique_id = str(uuid.uuid4())

        header = {
            "htype": "dheader-1.0",
            "series": self.sequence_id,
            "header_detail": "basic",
            "header_appendix": self.user_data,
        }

        config_header = LegacyConfigHeader(
            beam_center_x=zmq_start_message.beam_center_x,
            beam_center_y=zmq_start_message.beam_center_y,
            count_time=zmq_start_message.count_time,
            frame_time=zmq_start_message.frame_time,
            nimages=int(self.number_of_frames_per_trigger),
            ntrigger=1,
            compression=self.compression,
            bit_depth_image=self.detector_config.detector_bit_depth_image,
            bit_depth_readout=self.detector_config.detector_bit_depth_readout,
            pixel_mask_applied=self.detector_config.pixel_mask_applied,
            roi_mode=self.detector_config.roi_mode,
            software_version=self.detector_config.software_version,
            detector_readout_time=self.detector_config.detector_readout_time,
            x_pixels_in_detector=zmq_start_message.image_size_x,
            y_pixels_in_detector=zmq_start_message.image_size_y,
        )

        self.socket.send_multipart(
            [
                self._json_dumps_bytes(header),
                self._json_dumps_bytes(config_header.model_dump()),
            ]
        )

    def _legacy_stream_frames(self, legacy_frames: list[LegacyFrame]) -> None:
        """
        Sends frames through a ZMQ stream using the legacy stream format.

        Returns
        -------
        None
        """
        logging.info(f"Sending LEGACY frames to {self.address}")
        start_time = time.time()
        count_time = zmq_start_message.count_time

        for _ in trange(self.number_of_frames_per_trigger):
            time.sleep(self.delay_between_frames)
            try:
                frame = legacy_frames[self.frame_id]
            except IndexError:
                self.frame_id = 0
                frame = legacy_frames[self.frame_id]

            part_1 = {
                "htype": "dimage-1.0",
                "series": self.sequence_id,
                "frame": int(self.image_number),
                "hash": "",
            }
            part_2 = {
                "htype": "dimage_d-1.0",
                "shape": [
                    int(zmq_start_message.image_size_x),
                    int(zmq_start_message.image_size_y),
                ],
                "encoding": frame.encoding,
                "type": frame.dtype,
                "size": int(frame.size),
            }

            start_nano = int((start_time + self.image_number * count_time) * 1e9)
            stop_nano = int((start_time + (self.image_number + 1) * count_time) * 1e9)
            part_4 = {
                "htype": "dconfig-1.0",
                "start_time": start_nano,
                "stop_time": stop_nano,
                "real_time": int(stop_nano - start_nano),
            }

            self.socket.send_multipart(
                [
                    self._json_dumps_bytes(part_1),
                    self._json_dumps_bytes(part_2),
                    frame.data,
                    self._json_dumps_bytes(part_4),
                ]
            )
            self.frame_id += 1
            self.image_number += 1

        frame_rate = self.number_of_frames_per_trigger / (time.time() - start_time)
        logging.info(f"Frame rate: {frame_rate} frames / s")

    def _legacy_stream_end_message(self) -> None:
        """
        Sends an end message through a ZMQ stream using the legacy stream format.

        Returns
        -------
        None
        """
        header = {"htype": "dseries_end-1.0", "series": self.sequence_id}
        self.socket.send(self._json_dumps_bytes(header))

    def _stream_enabled(self) -> bool:
        """Checks if the stream is enabled

        Returns
        -------
        bool
            True if the stream is enabled, False otherwise
        """
        return self.stream_config.mode == "enabled"

    def _json_dumps_bytes(self, input: dict) -> bytes:
        """Dumps a dict to json and encodes it to bytes.
        Used only for the legacy stream format.

        Parameters
        ----------
        input : dict
            The dictionary to be dumped and encoded

        Returns
        -------
        bytes
            The encoded object
        """
        return json.dumps(input).encode()

    def _endian_marker(self, dtype: np.dtype) -> Literal["<", ">"]:
        """
        Determines the endian marker for a given numpy dtype.
        Used only for the legacy stream format

        Parameters
        ----------
        dtype : np.dtype
            A numpy dtype

        Returns
        -------
        Literal["<", ">"]
            The endian marker
        """
        if dtype.byteorder in ("<", ">"):
            return dtype.byteorder

        if sys.byteorder == "little":
            return "<"
        else:
            return ">"

    def _legacy_encoding(self, dtype: np.dtype) -> str:
        """From the simplon api docs, the legacy encoding follows the format:

        "[bs<BIT>][[-]lz4][<|>]".

        e.g. "bs16-lz4<", "lz4<", "<".
        """

        bits = int(dtype.itemsize) * 8
        endian = self._endian_marker(dtype)

        if self.compression == "bslz4":
            return f"bs{bits}-lz4{endian}"
        elif self.compression == "none":
            return endian
        else:
            raise NotImplementedError(
                f"The allowed compression types are bslz4 and none, not {self.compression}"
            )
