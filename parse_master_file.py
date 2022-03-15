import h5py
import numpy as np


class Parse:
    def __init__(self, hdf5_file) -> None:
        self.hdf5_file = hdf5_file
        self.entries = self.list_entries(self.hdf5_file)

    @staticmethod
    def list_entries(hdf5_file) -> list:
        entries = []
        hdf5_file.visit(entries.append)
        return entries

    def parse(self, look_for: str):  # -> str OR int OR float
        for entry in self.entries:
            sublist = entry.split('/')
            # Find exact entry
            if look_for in sublist:
                item = np.array(self.hdf5_file.get(entry)).item()
                try:
                    # Decode if string
                    return item.decode()
                except AttributeError:
                    # Leave as is if float or int
                    return item

    def header(self) -> dict:
        start_message = {
            'type': 'start',
            'beam_center_x': self.parse('beam_center_x'),
            'beam_center_y': self.parse('beam_center_y'),
            'channels': [{
                'data_type': 'FIX',
                'thresholds': ['FIX']
            }],
            'count_time': self.parse('count_time'),
            'countrate_correction_applied': bool(
                self.parse('countrate_correction_applied')),
            'detector_description': self.parse('description'),
            'detector_distance': self.parse('detector_distance'),
            'detector_serial_number': self.parse('detector_number'),
            'flatfield_applied': bool(self.parse('flatfield_correction_applied')),
            'frame_time': 'FIX',
            'goniometer': 'FIX',
            'image_size': [
                self.parse('y_pixels_in_detector'),
                self.parse('x_pixels_in_detector')
            ],
            'images_per_trigger': 'FIX',
            'incident_energy': self.parse('photon_energy'),
            'incident_wavelength': self.parse('incident_wavelength'),
            'number_of_images': self.parse('nimages'),
            'number_of_triggers': self.parse('ntrigger'),
            'pixel_mask_applied': bool(self.parse('pixel_mask_applied')),
            'pixel_size_x': self.parse('x_pixel_size'),
            'pixel_size_y': self.parse('y_pixel_size'),
            'roi_mode': self.parse('roi_mode'),
            'saturation_value': self.parse('saturation_value'),
            'sensor_material': self.parse('sensor_material'),
            'sensor_thickness': self.parse('sensor_thickness'),
            'series_date': self.parse('data_collection_date'),
            'threshold_energy': {
                '1': self.parse('threshold_energy'),
                '2': 'FIX',
            },
            'virtual_pixel_correction_applied': bool(
                self.parse('virtual_pixel_correction_applied')),
        }

        image_message = {
            'type': 'image',
            'series_number': 'FIX',
            'series_unique_id': 'FIX',
            'image_number': 'FIX',
            'hardware_start_time': 'FIX',
            'hardware_stop_time': 'FIX',
            'hardware_exposure_time': 'FIX',
            # One list per threshold; so normally 1 but up to 2.
            'channels': [{
                'compression': '-add in simulate_zmq_stream.py-',
                'data_type': 'FIX',
                'lost_pixel_count': 'FIX',
                'thresholds': 'FIX',
                'data': '-add in simulate_zmq_stream.py-',
            }],
        }

        end_message = {
            'type': 'end',
            'series_number': 'FIX',
            'series_unique_id': 'FIX',
        }
        return start_message, image_message, end_message
