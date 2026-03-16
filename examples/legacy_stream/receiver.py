import json
import logging
import re

import numpy as np
import numpy.typing as npt
import zmq
from dectris.compression import decompress

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)


def decompress_legacy_frame(
    encoding: str,
    frame_bytes: bytes,
    shape_xy: list[int] | tuple[int, int],
    dtype_str: str,
) -> npt.NDArray:
    """
    Decompresses a frame from the legacy stream

    Parameters
    ----------
    encoding : str
        The encoding of the frame, e.g. "<"
    frame_bytes : bytes
        The compressed frame bytes
    shape_xy : list[int] | tuple[int, int]
        The (x,y) shape of the image
    dtype_str : str
        The data type of the image, e.g. "<u4"

    Returns
    -------
    npt.NDArray
        A decompressed frame
    """
    dtype = np.dtype(dtype_str)

    x, y = int(shape_xy[0]), int(shape_xy[1])
    shape_yx = (y, x)

    if encoding in ("<", ">"):
        # uncompressed frame
        return np.frombuffer(frame_bytes, dtype=dtype.newbyteorder(encoding)).reshape(
            shape_yx
        )

    # detector encoding is in a format e.g. `bs32-lz4<` for
    # bslz4 with 32-bit and little-endian order
    match = re.fullmatch(r"bs(\d+)-lz4([<>])", encoding)
    if match is not None:
        element_size = int(match.group(1)) // 8
        endian = "<" if match.group(2) == "<" else ">"
        decompressed_bytes = decompress(
            frame_bytes,
            "bslz4",
            elem_size=element_size,
        )
        dtype = dtype.newbyteorder(endian)
        return np.frombuffer(decompressed_bytes, dtype=dtype).reshape(shape_yx)

    raise NotImplementedError(f"Unsupported encoding: {encoding}")


ctx = zmq.Context()
socket = ctx.socket(zmq.PULL)
endpoint = "tcp://127.0.0.1:5555"
socket.connect(endpoint)
logging.info(f"PULL {endpoint}")

count = 0

while True:
    parts = socket.recv_multipart()
    header = json.loads(parts[0].decode())
    htype = header["htype"]

    if htype == "dheader-1.0":
        logging.info("-" * 80)
        logging.info("LEGACY start (dheader)")
        logging.info(header)
        if len(parts) >= 2:
            detector_config = json.loads(parts[1].decode())
            logging.info(f"Detector configuration: {detector_config}")
        count = 0

    elif htype == "dseries_end-1.0":
        logging.info("-" * 80)
        logging.info("LEGACY end (dseries_end)")
        logging.info(header)
        count = 0

    elif htype == "dimage-1.0" and len(parts) == 4:
        part_1 = header  # frame header with series/frame numbers
        part_2 = json.loads(parts[1].decode())  # frame metadata
        part_3 = parts[2]  # raw frame bytes
        part_4 = json.loads(parts[3].decode())  # frame timing info

        logging.info("-" * 80)
        logging.info(f"series: {part_1['series']} frame: {part_1['frame']}")

        image = decompress_legacy_frame(
            encoding=str(part_2["encoding"]),
            frame_bytes=part_3,
            shape_xy=part_2["shape"],
            dtype_str=str(part_2["type"]),
        )
        count += 1
        logging.info(
            f"Processed {count} frames, image shape={image.shape}, "
            f"dtype={image.dtype}, real_time={part_4['real_time']}"
        )
    else:
        logging.info(
            f"Received unknown message with htype: {htype} and {len(parts)} parts"
        )
