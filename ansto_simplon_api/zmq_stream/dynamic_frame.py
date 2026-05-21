# mypy: disable-error-code="import-untyped"

import logging
from typing import Any

import numpy as np

from ..schemas.stream import ZMQStartMessage


def sanitise_detector_name(detector_name: str) -> str:
    """Sanitise detector labels before passing them to pyFAI's factory.

    pyFAI expects the detector name without the manufacturer, and only accepts sensor
    for CdTe detectors, so we remove "Dectris" and "Si" from the detector description
    to improve the chances of a successful match.

    Parameters
    ----------
    detector_name : str
        The name of the detector to be sanitised.

    Returns
    -------
    str
        The sanitised detector name.
    """
    parts_to_remove = {"dectris", "si"}

    detector_name_parts = detector_name.strip().split()

    sanitised_parts = [
        part for part in detector_name_parts if part.lower() not in parts_to_remove
    ]

    return " ".join(sanitised_parts).lower()


def build_dynamic_frame_cache_key(
    start_message: ZMQStartMessage,
    compression: str,
) -> tuple[float, float, float, float, int, int, str, str, str]:
    """Build the cache key for generated dynamic frames.

    This is used to determine whether a previously generated dynamic frame can be reused
    for a new stream, or if a new one needs to be generated.
    Changing any of these parameters would result in a different dynamic frame.

    Parameters
    ----------
    start_message : ZMQStartMessage
        The ZMQStartMessage containing the metadata for the stream.
    compression : str
        The compression type used for the stream.

    Returns
    -------
    tuple[float, float, float, float, int, int, str, str, str]
        A tuple containing the cache key for the generated dynamic frame.
    """
    detector_distance = float(start_message.detector_translation[2])
    return (
        float(start_message.incident_wavelength),
        float(start_message.beam_center_x),
        float(start_message.beam_center_y),
        detector_distance,
        int(start_message.image_size_x),
        int(start_message.image_size_y),
        str(start_message.image_dtype),
        str(start_message.detector_description),
        str(compression),
    )


def _build_generic_detector_instance(start_message: ZMQStartMessage) -> Any:
    """Build a generic pyFAI Detector instance from stream start metadata.

    Parameters
    ----------
    start_message : ZMQStartMessage
        The ZMQStartMessage containing the metadata for the stream.

    Returns
    -------
    Detector
        A pyFAI Detector instance built from the stream metadata.
    """
    from pyFAI.detectors import Detector

    shape = (
        int(start_message.image_size_y),
        int(start_message.image_size_x),
    )
    dtype = np.dtype(start_message.image_dtype)
    if dtype not in (np.dtype("uint16"), np.dtype("uint32")):
        raise NotImplementedError(
            "dynamic-frame supports uint16 and uint32 image_dtype only"
        ) from None

    pixel_size_y = float(start_message.pixel_size_y)
    pixel_size_x = float(start_message.pixel_size_x)

    return Detector(
        pixel1=pixel_size_y,
        pixel2=pixel_size_x,
        max_shape=shape,
        orientation=3,
    )


def generate_dynamic_image(start_message: ZMQStartMessage) -> np.ndarray:
    """Generate a pyFAI fake rings image from stream start metadata.

    Parameters
    ----------
    start_message : ZMQStartMessage
        The ZMQStartMessage containing the metadata for the stream.

    Returns
    -------
    np.ndarray
        A 2D numpy array containing the generated image.
    """
    from pyFAI import detector_factory
    from pyFAI.calibrant import get_calibrant
    from pyFAI.integrator.azimuthal import AzimuthalIntegrator

    try:
        detector = detector_factory(
            sanitise_detector_name(start_message.detector_description)
        )
    except RuntimeError:
        detector = _build_generic_detector_instance(start_message)

    pixel_size_y = detector.pixel1
    pixel_size_x = detector.pixel2
    detector_distance = abs(float(start_message.detector_translation[2]))

    ai = AzimuthalIntegrator(
        dist=detector_distance,
        poni1=float(start_message.beam_center_y) * pixel_size_y,
        poni2=float(start_message.beam_center_x) * pixel_size_x,
        detector=detector,
        wavelength=float(start_message.incident_wavelength) * 1e-10,
    )

    calibrant = get_calibrant("LaB6")
    try:
        image_array = calibrant.fake_calibration_image(
            ai=ai,
            Imax=1000,
        )
    except ValueError as ex:
        logging.warning(
            "pyFAI could not build rings image (%s); using zero-filled image",
            ex,
        )
        image_array = np.zeros(
            (int(start_message.image_size_y), int(start_message.image_size_x)),
            dtype=np.int32,
        )

    detector_dtype = np.dtype(start_message.image_dtype)
    if detector_dtype not in (np.dtype("uint16"), np.dtype("uint32")):
        raise NotImplementedError(
            "dynamic-frame supports uint16 and uint32 image_dtype only"
        ) from None

    if np.issubdtype(image_array.dtype, np.floating):
        image_array = np.clip(image_array, a_min=0, a_max=np.iinfo(detector_dtype).max)

    return np.ascontiguousarray(image_array, dtype=detector_dtype)
