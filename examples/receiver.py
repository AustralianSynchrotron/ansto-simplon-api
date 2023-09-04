import logging

import cbor2
import numpy as np
import numpy.typing as npt
import zmq
from dectris.compression import decompress

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)

tag_decoders = {
    69: "<u2",
    70: "<u4",
}


def decompress_image(zmq_image_message: dict) -> npt.NDArray:
    """Decompresses an image from the zmq image message

    Parameters
    ----------
    zmq_image_message : dict
        ZMQ image message

    Returns
    -------
    npt.NDArray
        A decompressed numpy array
    """

    data: cbor2.CBORTag = zmq_image_message["data"]["threshold_1"]
    contents: cbor2.CBORTag
    shape, contents = data.value
    dtype = tag_decoders[contents.tag]
    if type(contents.value) is bytes:
        # This means the image has not been compressed,
        # e.g. compression=none
        compression_type = None
        return np.frombuffer(contents.value, dtype=dtype).reshape(shape)
    else:
        compression_type, elem_size, image = contents.value.value
        decompressed_bytes = decompress(image, compression_type, elem_size=elem_size)
        return np.frombuffer(decompressed_bytes, dtype=dtype).reshape(shape)


context = zmq.Context()

#  Socket to talk to server
socket = context.socket(zmq.PULL)
endpoint = "tcp://0.0.0.0:5555"

count = 0

with socket.connect(endpoint):
    logging.info(f"PULL {endpoint}")
    while True:
        message = socket.recv()
        loaded_message = cbor2.loads(message)

        if loaded_message["type"] == "image":
            logging.info("-" * 80)
            logging.info(f"series_id: {loaded_message['series_id']}")
            logging.info(f"image_id: {loaded_message['image_id']}")
            image = decompress_image(loaded_message)
            count += 1
            logging.info(f"Successfully processed {count} frames")

        elif loaded_message["type"] == "start" or loaded_message["type"] == "end":
            logging.info(loaded_message)
            count = 0
