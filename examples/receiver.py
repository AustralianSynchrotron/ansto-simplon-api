import logging
from typing import Any

import bitshuffle
import cbor2
import lz4.frame
import numpy as np
import zmq

logging.basicConfig(level=logging.INFO)


def decompress_lz4_image(
    image: bytes, shape: tuple[int, int], dtype: np.dtype[Any]
) -> np.ndarray:
    """Decompress lz4 byte images

    Parameters
    ----------
    image : bytes
        Image in bytes format
    shape : tuple[int,int]
        Shape of the original image
    dtype : np.dtype[Any]
        Data type of the original image

    Returns
    -------
    reshaped_data : np.ndarray
        Decompressed image
    """

    decompressed_image = lz4.frame.decompress(image)
    deserialized_bytes = np.frombuffer(decompressed_image, dtype=dtype)
    reshaped_data = np.reshape(deserialized_bytes, newshape=shape)

    return reshaped_data


def decompress_bslz4_image(
    image: bytes, shape: tuple[int, int], dtype: np.dtype[Any]
) -> np.ndarray:
    """Decompress bslz4 byte images

    Parameters
    ----------
    image : bytes
        Image in bytes format
    shape : tuple[int,int]
        Shape of the original image
    dtype : np.dtype[Any]
        Data type of the original image

    Returns
    -------
    decompressed_image : np.ndarray
        Decompressed image
    """
    numpy_array = np.frombuffer(image, dtype="uint8")
    decompressed_image = bitshuffle.decompress_lz4(numpy_array, shape, dtype, 0)

    return decompressed_image


context = zmq.Context()

#  Socket to talk to server
socket = context.socket(zmq.PULL)
endpoint = "tcp://0.0.0.0:5555"

count = 0

data_type = {
    "uint8": np.dtype(np.uint8),
    "uint16": np.dtype(np.uint16),
    "uint32": np.dtype(np.uint32),
}

with socket.connect(endpoint):
    logging.info(f"PULL {endpoint}")
    while True:
        message = socket.recv()
        loaded_message = cbor2.loads(message)

        if loaded_message["type"] == "image":
            if loaded_message["channels"][0]["compression"] == "lz4":
                loaded_message["channels"][0]["data"] = decompress_lz4_image(
                    loaded_message["channels"][0]["data"],
                    loaded_message["channels"][0]["array_shape"],
                    data_type[loaded_message["channels"][0]["data_type"]],
                )
                count += 1

            elif loaded_message["channels"][0]["compression"] == "bslz4":
                loaded_message["channels"][0]["data"] = decompress_bslz4_image(
                    loaded_message["channels"][0]["data"],
                    loaded_message["channels"][0]["array_shape"],
                    data_type[loaded_message["channels"][0]["data_type"]],
                )
                count += 1

            # Print only multiples of 10
            if not count % 10:
                logging.info(f"Successfully processed {count} frames")

        elif loaded_message["type"] == "start" or "end":
            logging.info(loaded_message)
