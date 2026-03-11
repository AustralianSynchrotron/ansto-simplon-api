import json
import logging

import bitshuffle
import numpy as np
import numpy.typing as npt
import zmq

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
    dtype = np.dtype(dtype_str)

    x, y = int(shape_xy[0]), int(shape_xy[1])
    shape_yx = (y, x)

    if encoding in ("<", ">"):
        # uncompressed frame
        return np.frombuffer(frame_bytes, dtype=dtype).reshape(shape_yx)

    if encoding.startswith("bs") and "lz4" in encoding:
        # bslz4 compressed frame
        comp = np.frombuffer(frame_bytes, dtype=np.uint8)
        return bitshuffle.decompress_lz4(comp, shape_yx, dtype)

    raise NotImplementedError(f"Unsupported encoding: {encoding}")


ctx = zmq.Context()
socket = ctx.socket(zmq.PULL)
endpoint = "tcp://127.0.0.1:5555"
socket.connect(endpoint)
logging.info(f"PULL {endpoint}")

count = 0

while True:
    parts = socket.recv_multipart()
    if not parts:
        continue

    try:
        hdr = json.loads(parts[0].decode())
    except Exception:
        logging.warning("Received non-JSON first part")
        continue

    htype = hdr.get("htype")

    if htype == "dheader-1.0":
        logging.info("-" * 80)
        logging.info("LEGACY start (dheader)")
        logging.info(hdr)
        if len(parts) >= 2:
            try:
                cfg = json.loads(parts[1].decode())
                logging.info(cfg)
            except Exception:
                logging.info("<config header not JSON>")
        count = 0
        continue

    if htype == "dseries_end-1.0":
        logging.info("-" * 80)
        logging.info("LEGACY end (dseries_end)")
        logging.info(hdr)
        count = 0
        continue

    if htype == "dimage-1.0" and len(parts) == 4:
        p1 = hdr
        p2 = json.loads(parts[1].decode())
        frame_blob = parts[2]
        p4 = json.loads(parts[3].decode())

        logging.info("-" * 80)
        logging.info(f"series: {p1.get('series')} frame: {p1.get('frame')}")

        image = decompress_legacy_frame(
            encoding=str(p2.get("encoding")),
            frame_bytes=frame_blob,
            shape_xy=p2.get("shape", [0, 0]),
            dtype_str=str(p2.get("type", "uint16")),
        )
        count += 1
        logging.info(
            "Processed %d frames; image shape=%s dtype=%s real_time=%s",
            count,
            tuple(image.shape),
            str(image.dtype),
            p4.get("real_time"),
        )
        continue

    logging.info(f"{htype} parts={len(parts)}")
