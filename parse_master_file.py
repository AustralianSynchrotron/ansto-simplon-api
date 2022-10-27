import h5py
import numpy as np


class Parse:
    """
    Class for reading in a HDF5 Master file and generating a
    Dectris Stream2 set of messages (start, image, end).
    """

    def __init__(self, hdf5_file: h5py.File) -> None:
        """
        Parameters
        ----------
        hdf5-file : h5py.File object
            A hdf5 Master file read in via h5py.File()

        Returns
        -------
        None
        """
        self.hf = hdf5_file
        self.entries = self.list_entries(self.hf)

    @staticmethod
    def list_entries(hdf5_file: h5py.File) -> list[str]:
        """
        Generates a list of all entries in the hdf5 Master file.

        Parameters
        ----------
        hdf5-file : h5py.File object
            A hdf5 Master file read in via h5py.File()

        Returns
        -------
        entries : list[str]
        """
        entries = []
        hdf5_file.visit(entries.append)
        return entries

    def parse(self, look_for: str) -> str | int | float:
        """
        Looks up and returns entry from Master file. Treats the
        Master file like a key:value store with unique keys.

        TODO:
        This method assumes that each key is unique which might
        not hold true. Seems to work for the input Master files
        used so far. If this becomes a problem, the whole thing
        should be redone with direct reference to the hdf5
        fields and data.

        Parameters
        ----------
        look_for : str
            The key to look up in the Master file.

        Returns
        -------
        item : str or int or float
            The value stored under the key.
        """
        for entry in self.entries:
            sublist = entry.split("/")
            # Find exact entry
            if look_for in sublist:
                item = np.array(self.hf.get(entry)).item()
                try:
                    # Decode if string
                    return item.decode()
                except AttributeError:
                    # Leave as is if float or int
                    return item

    def header(self) -> dict:
        """
        Generate the Dectris stream2 message structure,
        and look up the corresponding values in the input
        Master file.

        Parameters
        ----------
        None

        Returns
        -------
        start_message, image_message, end_message : dict
            Three dictionaries corresponding to the stream2
            message structure.

        """
        start_message = {
            "type": "start",
            "arm_date": self.parse("data_collection_date"),
            "beam_center_x": self.parse("beam_center_x"),
            "beam_center_y": self.parse("beam_center_y"),
            "channels": ["1"],
            "count_time": self.parse("count_time"),
            "countrate_correction_enabled": bool(
                self.parse("countrate_correction_applied")
            ),
            "countrate_correction_lookup_table": None,
            "detector_description": self.parse("description"),
            "detector_serial_number": self.parse("detector_number"),
            "detector_translation": [
                0.0,
                0.0,
                self.parse("detector_distance"),
            ],
            "flatfield": None,
            "flatfield_enabled": bool(self.parse("flatfield_correction_applied")),
            "frame_time": self.parse("frame_time"),
            "goniometer": {
                "omega": {
                    "increment": self.parse("omega_range_average"),
                    # Needs to get the first item of a list, so can't use parse
                    "start": float(self.hf.get("/entry/sample/goniometer/omega")[0]),
                },
                "otherAxis": {
                    "increment": 1.0,
                    "start": 0.0,
                },
            },
            "image_size_x": self.parse("x_pixels_in_detector"),
            "image_size_y": self.parse("y_pixels_in_detector"),
            "incident_energy": self.parse("photon_energy"),
            "incident_wavelength": self.parse("incident_wavelength"),
            "number_of_images": None,  # self.parse("nimages"),
            "pixel_mask": None,
            "pixel_mask_enabled": bool(self.parse("pixel_mask_applied")),
            "pixel_size_x": self.parse("x_pixel_size"),
            "pixel_size_y": self.parse("y_pixel_size"),
            "saturation_value": self.parse("saturation_value"),
            "sensor_material": self.parse("sensor_material"),
            "sensor_thickness": self.parse("sensor_thickness"),
            "series_id": None,  # int
            "series_unique_id": None,  # str
            "threshold_energy": {
                "1": self.parse("threshold_energy"),
                "2": self.parse("threshold_energy") * 3,
            },
            "user_data": {"pi": float(np.pi)},
            "virtual_pixel_correction_applied": bool(
                self.parse("virtual_pixel_correction_applied")
            ),
        }

        image_message = {
            "type": "image",
            "series_id": "FIX",
            "series_unique_id": "FIX",
            "image_id": "FIX",
            "hardware_start_time": "FIX",
            "hardware_stop_time": "FIX",
            "hardware_exposure_time": "FIX",
            # One list per threshold; so normally 1 but up to N.
            "channels": [
                {
                    "compression": "-add in simulate_zmq_stream.py-",
                    "data_type": "FIX",
                    "lost_pixel_count": "FIX",
                    "thresholds": "FIX",
                    "data": "-add in simulate_zmq_stream.py-",
                }
            ],
        }

        end_message = {
            "type": "end",
            "series_id": "FIX",
            "series_unique_id": "FIX",
        }
        return start_message, image_message, end_message
