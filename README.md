# MX Sim-Plon API

## Setup

### Docker Compose

1) If required, edit the "docker-compose.yml" file and modify the "HDF5_MASTER_FILE" environment variable to point to another HDF5 file hosted on the MX SMB share.

2) Run docker compose to build the image and start the service.

```text
docker-compose up
```

### Manual Setup

1) Build the container image `docker build -t sim_plon_api .`

2) Create a volume using the cifs driver to give the container access to the SMB share.

```text
docker volume create --driver local --opt type=cifs \
    --opt device=//10.244.101.66/smd-share \
    --opt o=username=guest,password=guest,vers=2.0,uid=1000,gid=1000 \
    --name simplon_share_data
```

3) Start the container attaching the new SMB volume.

> Note: If required, modify the "HDF5_MASTER_FILE" environment variable to point to another HDF5 file hosted on the MX SMB share.

```text
docker run --rm -dt --name sim_plon_api \
    -p 8000:8000 -p 5555:5555 \
    -e HDF5_MASTER_FILE='/share_data/4Mrasterdata/01x10/testraster01_0008_master.h5' \
    -v simplon_share_data:/share_data sim_plon_api
```

## Example Usage

1) Start the consumer: `python examples/receiver.py`

2) Trigger the detector using our sim_plon_api: `python examples/trigger_detector.py`

<!-- NOTE: If you need to use a different HDF5 file, copy the master hdf5 file and the data file to
the `hdf5_data` folder to run this example, e.g. `testcrystal_0009_master.h5` and `testcrystal_0009_data_000001.h5`.
At the moment only one master file can be in the `hdf5_data` folder -->
