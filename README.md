# MX Sim-Plon API
A simulated Dectris Simplon API. Aims to have the same RESTlike interface and produce a ZMQ stream of data from an input Hdf5 file.
The input HDF5 file is defined by the environment variable `HDF5_MASTER_FILE`, e.g. `HDF5_MASTER_FILE=/path/to/HDF5_masterfile.h5`

Currently generates a [Stream2 alpha] release compatible ZMQ stream.

## Setup

1. **Simulated Simplon API Configuration**

   To run the simulated Simplon API, you need to specify the path of an HDF5 master file using the `HDF5_MASTER_FILE` environment variable. You can also configure other parameters using the following environment variables:

   - `DELAY_BETWEEN_FRAMES`: Specifies the delay between frames in seconds (default: 0.1 s).
   - `NUMBER_OF_DATA_FILES`: Sets the number of data files from the master file loaded into memory (default: 1). Note that the datafiles are stored in memory, so they should not be too large.
   - `NUMBER_OF_FRAMES_PER_TRIGGER`: Controls the number of frames per trigger. By default, it's set to 30, but you can modify it using the `/detector/api/1.8.0/config/nimages` endpoint.

2. **Running the simulated SIMPLON API**
    * Install the library via 1) `poetry install` or 2) `pip install .`
    * Set the HDF5 file path: ```export  HDF5_MASTER_FILE=/path/to/HDF5_master_file```
    * Run the FAST-API application:
    ```uvicorn ansto_simplon_api.main:app```



3. **(Optional) Running the simplon API with Docker Compose**

   To build the image and start the service, modify the docker compose file with the corresponding environment variables and the run:

   ```bash
   docker compose up --detach
   ```

## Example Usage

1) Start the consumer: `python examples/receiver.py`

2) Trigger the detector using our sim_plon_api: `python examples/trigger_detector.py`

<!-- NOTE: If you need to use a different HDF5 file, copy the master hdf5 file and the data file to
the `hdf5_data` folder to run this example, e.g. `testcrystal_0009_master.h5` and `testcrystal_0009_data_000001.h5`.
At the moment only one master file can be in the `hdf5_data` folder -->

[Stream2 alpha]: https://github.com/dectris/documentation/tree/473d768c3eddc1989da00c941081847955c94e96/stream_v2
