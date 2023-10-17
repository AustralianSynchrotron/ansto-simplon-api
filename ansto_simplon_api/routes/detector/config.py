from fastapi import APIRouter

from ...schemas.configuration import (
    DetectorConfiguration,
    SimplonRequestAny,
    SimplonRequestBool,
    SimplonRequestDict,
    SimplonRequestFloat,
    SimplonRequestInt,
    SimplonRequestStr,
)
from ...simulate_zmq_stream import zmq_start_message, zmq_stream

router = APIRouter(prefix="/detector/api/1.8.0/config", tags=["Detector Configuration"])

detector_configuration = DetectorConfiguration()

### Detector subsystem config
# @router.put("/auto_summation")


@router.get("/auto_summation")
async def get_auto_summation():
    return {"value": True}


@router.get("/beam_center_x")
async def get_beam_center_x():
    return {"value": zmq_start_message.beam_center_x}


@router.put("/beam_center_x")
async def put_beam_center_x(input: SimplonRequestFloat):
    zmq_start_message.beam_center_x = input.value
    return {"value": zmq_start_message.beam_center_x}


@router.get("/beam_center_y")
async def get_beam_center_y():
    return {"value": zmq_start_message.beam_center_y}


@router.put("/beam_center_y")
async def put_beam_center_y(input: SimplonRequestFloat):
    zmq_start_message.beam_center_y = input.value
    return {"value": zmq_start_message.beam_center_y}


@router.put("/bit_depth_image")
async def put_bit_depth_image(input: SimplonRequestInt):
    detector_configuration.detector_bit_depth_image = input.value
    # the bit depth image is not the dtype
    return {"value": detector_configuration.detector_bit_depth_image}


@router.get("/bit_depth_image")
async def get_bit_depth_image():
    return {"value": detector_configuration.detector_bit_depth_image}


# @router.put("/bit_depth_readout")
@router.get("/bit_depth_readout")
async def get_bit_depth_readout():
    return {"value": 16}


# chi_increment
# chi_start


@router.put("/compression")
async def set_compression(compression: SimplonRequestStr):
    zmq_stream.compression = compression.value
    return {"value": zmq_stream.compression}


@router.get("/compression")
async def get_compression():
    return {"value": zmq_stream.compression}


@router.get("/count_time")
async def get_count_time():
    return {"value": zmq_start_message.count_time}


@router.put("/count_time")
async def put_count_time(input: SimplonRequestFloat):
    zmq_start_message.count_time = input.value
    return {"value": zmq_start_message.count_time}


# counting_mode
# countrate_correction_applied
@router.get("/countrate_correction_applied")
async def get_countrate_correction_applied():
    return {"value": zmq_start_message.countrate_correction_enabled}


@router.put("/countrate_correction_applied")
async def put_countrate_correction_applied(input: SimplonRequestBool):
    zmq_start_message.countrate_correction_enabled = input.value
    return {"value": zmq_start_message.countrate_correction_enabled}


# @router.put("/countrate_correction_count_cutoff")
@router.get("/countrate_correction_count_cutoff")
async def get_countrate_correction_count_cutoff():
    return {"value": 133343}


# data_collection_date


@router.put("/description")
async def put_description(input: SimplonRequestStr):
    zmq_start_message.detector_description = input.value
    return {"value": zmq_start_message.detector_description}


@router.get("/description")
async def get_description():
    return {"value": zmq_start_message.detector_description}


@router.get("/detector_distance")
async def get_detector_distance():
    return {"value": zmq_start_message.detector_translation}


@router.put("/detector_distance")
async def put_detector_distance(
    input: SimplonRequestFloat,
):
    detector_translation = (0, 0, input.value)
    zmq_start_message.detector_translation = detector_translation
    return {"value": zmq_start_message.detector_translation}


@router.put("/detector_number")
async def put_detector_number(input: SimplonRequestStr):
    zmq_start_message.detector_serial_number = input.value
    return {"value": zmq_start_message.detector_serial_number}


@router.get("/detector_number")
async def get_detector_number():
    return {"value": zmq_start_message.detector_serial_number}


@router.get("/detector_readout_time")
async def get_detector_readout_time():
    return {"value": detector_configuration.detector_readout_time}


@router.put("/detector_readout_time")
async def put_detector_readout_time(input: SimplonRequestFloat):
    detector_configuration.detector_readout_time = input.value
    return {"value": detector_configuration.detector_readout_time}


# @router.put("/eiger_fw_version")
@router.get("/eiger_fw_version")
async def get_eiger_fw_version():
    return {"value": "release-2020.2.5"}


# element
# flatfield
# flatfield_correction_applied


# @router.put("/frame_count_time")
@router.get("/frame_count_time")
async def get_frame_count_time():
    return {"value": 0.004170816650000}


@router.get("/frame_time")
async def get_frame_time():
    return {"value": zmq_start_message.frame_time}


@router.put("/frame_time")
async def put_frame_time(input: SimplonRequestFloat):
    zmq_start_message.frame_time = input.value
    return {"value": zmq_start_message.frame_time}


# kappa_increment
# kappa_start


### NOTE: this endpoint is not used by the zmq_start_message but
### by the zmq_stream elsewhere. Is this correct?
@router.put("/nimages")
async def set_nimages(number_of_images: SimplonRequestInt):
    zmq_stream.number_of_frames_per_trigger = number_of_images.value
    return {"value": zmq_stream.number_of_frames_per_trigger}


### NOTE: Same
@router.get("/nimages")
async def get_nimages():
    return {"value": zmq_stream.number_of_frames_per_trigger}


# @router.put("/ntrigger")
@router.get("/ntrigger")
async def get_ntrigger():
    return {"value": 1}


# @router.put("/number_of_excluded_pixels")
@router.get("/ntrigger")
async def get_number_of_excluded_pixels():
    return {"value": 664708}


# omega_increment
# omega_start
# phi_increment
# phi_start


@router.get("/photon_energy")
async def get_photon_energy():
    return {"value": zmq_start_message.incident_energy}


@router.put("/photon_energy")
async def put_photon_energy(input: SimplonRequestFloat):
    zmq_start_message.incident_energy = input.value
    return {"value": zmq_start_message.incident_energy}


# pixel_mask
# pixel_mask_applied
# roi_mode


@router.put("/sensor_material")
async def put_sensor_material(input: SimplonRequestStr):
    zmq_start_message.sensor_material = input.value
    return {"value": zmq_start_message.sensor_material}


@router.get("/sensor_material")
async def get_sensor_material():
    return {"value": zmq_start_message.sensor_material}


@router.put("/sensor_thickness")
async def put_sensor_thickness(input: SimplonRequestFloat):
    zmq_start_message.sensor_thickness = input.value
    return {"value": zmq_start_message.sensor_thickness}


@router.get("/sensor_thickness")
async def get_sensor_thickness():
    return {"value": zmq_start_message.sensor_thickness}


# @router.put("/software_version")
@router.get("/software_version")
async def get_software_version():
    return {"value": "1.8.0"}


# threshold_energy


@router.get("/threshold_energy")
async def get_threshold_energy():
    return {"value": zmq_start_message.threshold_energy}


@router.put("/threshold_energy")
async def put_threshold_energy(input: SimplonRequestDict):
    zmq_start_message.threshold_energy = input.value
    return {"value": zmq_start_message.threshold_energy}


# threshold / n / energy
# threshold / n / mode
# threshold / difference / upper_threshold


# @router.put("/trigger_mode")
@router.get("/trigger_mode")
async def get_trigger_mode():
    return {"value": "exts"}


# trigger_start_delay
# two_theta_increment
# two_theta_start


@router.get("/virtual_pixel_correction_applied")
async def get_virtual_pixel_correction_applied():
    return {"value": zmq_start_message.virtual_pixel_interpolation_enabled}


@router.put("/virtual_pixel_correction_applied")
async def put_virtual_pixel_correction_applied(input: SimplonRequestBool):
    zmq_start_message.virtual_pixel_interpolation_enabled = input.value
    return {"value": zmq_start_message.virtual_pixel_interpolation_enabled}


# wavelength


@router.put("/x_pixel_size")
async def put_x_pixel_size(input: SimplonRequestFloat):
    zmq_start_message.pixel_size_x = input.value
    return zmq_start_message.pixel_size_x


@router.get("/x_pixel_size")
async def get_x_pixel_size():
    return {"value": zmq_start_message.pixel_size_x}


@router.get("/x_pixels_in_detector")
async def get_x_pixels_in_detector():
    return {"value": zmq_start_message.image_size_x}


@router.put("/x_pixels_in_detector")
async def put_x_pixels_in_detector(input: SimplonRequestFloat):
    zmq_start_message.image_size_x = input.value
    return {"value": zmq_start_message.image_size_x}


@router.put("/y_pixel_size")
async def put_y_pixel_size(input: SimplonRequestFloat):
    zmq_start_message.pixel_size_y = input.value
    return zmq_start_message.pixel_size_y


@router.get("/y_pixel_size")
async def get_y_pixel_size():
    return {"value": zmq_start_message.pixel_size_y}


@router.get("/y_pixels_in_detector")
async def get_y_pixels_in_detector():
    return {"value": zmq_start_message.image_size_y}


@router.put("/y_pixels_in_detector")
async def put_y_pixels_in_detector(input: SimplonRequestFloat):
    zmq_start_message.image_size_y = input.value
    return {"value": zmq_start_message.image_size_y}


### Monitor subsystem config
# buffer_size
# discard_new
# mode

### Filewriter subsystem config
# compression_enabled
# image_nr_start
# nimages_per_file


### Other
# @router.put("/detector_type")
@router.get("/detector_type")
async def get_detector_type():
    return {"value": "HPC"}


@router.get("/goniometer")
async def get_goniometer():
    return {"value": zmq_start_message.goniometer}


@router.put("/goniometer")
async def put_goniometer(input: SimplonRequestAny):
    zmq_start_message.goniometer = input.value
    return {"value": zmq_start_message.goniometer}


# user_data(dict)
