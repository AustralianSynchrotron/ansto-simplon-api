# MX Sim-Plon API
A simulated Dectris Simplon API. Aims to have the same RESTlike interface and produce a ZMQ stream of data from an input Hdf5 file.
The input HDF5 file is defined by the environment variable `HDF5_MASTER_FILE`, e.g. `HDF5_MASTER_FILE=/path/to/HDF5_masterfile.h5`

Currently generates a [Stream2 alpha] release compatible ZMQ stream.

## Setup

**Simulated Simplon API Configuration**

   To run the simulated Simplon API, you need to specify the path of an HDF5 master file using the `HDF5_MASTER_FILE` environment variable. You can also configure other parameters using the following environment variables:

   - `DELAY_BETWEEN_FRAMES`: Specifies the delay between frames in seconds (default: 0.1 s).
   - `NUMBER_OF_DATA_FILES`: Sets the number of data files from the master file loaded into memory (default: 1). Note that the datafiles are stored in memory, so they should not be too large.
   - `NUMBER_OF_FRAMES_PER_TRIGGER`: Controls the number of frames per trigger. By default, it's set to 30, but you can modify it using the `/detector/api/1.8.0/config/nimages` endpoint.

## Running the simulated SIMPLON API

Follow these steps to run the simulated SIMPLON API and ensure its proper functionality:

1. **Install the Library**
   You have two options to install the library:
   - Using Poetry: Run `poetry install`.
   - Using pip: Run `pip install .`.

2. **Set the HDF5 File Path**
   Before running the API, set the `HDF5_MASTER_FILE` environment variable using the following command:
   ```bash
   export HDF5_MASTER_FILE=/path/to/HDF5_master_file
   ```

3. **Run the FAST-API application**
   Launch the FAST-API application
   ```bash
   uvicorn ansto_simplon_api.main:app
   ```

4. **Start the ZMQ Consumer**
Once the simulated SIMPLON API is up and running, you can verify its functionality by running the ZMQ receiver and triggering the detector:
```bash
python examples/receiver.py
```
5. **Arm, trigger and disarm the detector**
Finally run the arm, trigger, and disarm script as follows:
```bash
python examples/trigger_detector.py
```
After running this script, you should see messages being received by the `receiver.py` script.

[Stream2 alpha]: https://github.com/dectris/documentation/tree/473d768c3eddc1989da00c941081847955c94e96/stream_v2

## Documentation
You can see the endpoints currently implemented by accessing the interactive API documentation at [http://localhost:8000/docs](http://localhost:8000/docs). Ensure that the simulated SIMPLON API is up and running to access the documentation.
