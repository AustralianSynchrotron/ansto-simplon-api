# ANSTO Sim-Plon API
A simulated Dectris Simplon API. Aims to have the same RESTlike interface and produce a ZMQ stream of data from an input Hdf5 file.

Supports both [Stream V2] and `Legacy` ZMQ stream formats.

## Running the simulated SIMPLON API

### Running the app using docker (Recommended)
You can build and run the app by simply running:
```bash
docker compose up --detach
```
The app's behavior can be optionally modified by setting environment variables in the `docker-compose.yml` file

The following environment variables can be configured:

- `AS_DELAY_BETWEEN_FRAMES`: Specifies the delay between frames in seconds (default: 0.01 s). This number can be modified during runtime via the `/ansto_endpoints/delay_between_frames` endpoint.

- `AS_NUMBER_OF_DATA_FILES`: Sets the number of data files from the master file loaded into memory (default: 1). This can be updated when loading a new master file via the `/ansto_endpoints/hdf5_master_file endpoint`.

- `AS_HDF5_MASTER_FILE`: The absolute path to an HDF5 master file. If unset, the project's default master file is used. You can switch master files at runtime via the `/ansto_endpoints/hdf5_master_file` endpoint.

### Running the app locally

Follow these steps to run the app locally:

1. **Install the Library**

   This repository uses [UV].

   To install the dependencies run `uv sync`
     **Note**: For Ubuntu users, additionally install the following packages
     ```bash
      apt update
      apt-get install -y gcc libhdf5-serial-dev
     ```
     For other operating systems, Install the equivalent libraries for `gcc` and `libhdf5-serial-dev`.

   The same environment variables described in the `docker` section can be updated if necessary.

3. **Run the FAST-API application**
   ```bash
   uvicorn ansto_simplon_api.main:app
   ```

## Example usage
Once the simulated SIMPLON API is up and running, you can verify its functionality by:

1. **Starting the ZMQ Consumer**

```bash
python examples/cbor_stream/receiver.py
```

2. **Triggering the detector**

You can arm, trigger, and disarm the detector using the following script:
```bash
python examples/cbor_stream/trigger_detector.py
```
After running this script, you should see messages being received by the `receiver.py` script.

`Legacy` ZMQ stream examples can be found in the `examples/legacy_stream/` folder.


## Documentation
You can see the endpoints currently implemented by accessing the interactive API documentation at [http://localhost:8000/swagger](http://localhost:8000/swagger). Ensure that the simulated SIMPLON API is up and running to access the documentation.

[Stream V2]: https://github.com/dectris/documentation/tree/main/stream_v2
[UV]: https://docs.astral.sh/uv/
