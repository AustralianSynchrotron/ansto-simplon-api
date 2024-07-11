# ANSTO Sim-Plon API
A simulated Dectris Simplon API. Aims to have the same RESTlike interface and produce a ZMQ stream of data from an input Hdf5 file.
The input HDF5 file is defined by the environment variable `HDF5_MASTER_FILE`, e.g. `HDF5_MASTER_FILE=/path/to/HDF5_masterfile.h5`

Currently generates a [Stream V2] release compatible ZMQ stream.

## Setup

**Simulated Simplon API Configuration**

   To run the simulated Simplon API, you need to specify the path of an HDF5 master file using the `HDF5_MASTER_FILE` environment variable. You can also configure other parameters using the following environment variables:

   - `DELAY_BETWEEN_FRAMES`: Specifies the delay between frames in seconds (default: 0.1 s). This number can be modified via the `/ansto_endpoints/delay_between_frames` endpoint.
   - `NUMBER_OF_DATA_FILES`: Sets the number of data files from the master file loaded into memory (default: 1). The number of datafiles can be additionally modified when loading a new master file using the
   `/ansto_endpoints/hdf5_master_file` endpoint.
   - The number of frames per trigger is set automatically to the number of frames in the master file. This can be modified by using the `/detector/api/1.8.0/config/nimages` endpoint.

## Running the simulated SIMPLON API

Follow these steps to run the simulated SIMPLON API and ensure its proper functionality:

1. **Install the Library**

   You have two options to install the library:
   - Using Poetry (Recommended): Run `poetry install`.
   - Using pip: Run `pip install .`.

     **Note**: For Ubuntu users, additionally install the following packages
     ```bash
      apt update
      apt-get install -y gcc libhdf5-serial-dev
     ```
     For other operating systems, Install the equivalent libraries for `gcc` and `libhdf5-serial-dev`.

2. **Set the HDF5 File Path**

   Before running the API, set the `HDF5_MASTER_FILE` environment variable using the following command:
   ```bash
   export HDF5_MASTER_FILE=/path/to/HDF5_master_file
   ```

3. **Run the FAST-API application**
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

[Stream V2]: https://github.com/dectris/documentation/tree/main/stream_v2

## Documentation
You can see the endpoints currently implemented by accessing the interactive API documentation at [http://localhost:8000/docs](http://localhost:8000/docs). Ensure that the simulated SIMPLON API is up and running to access the documentation.
