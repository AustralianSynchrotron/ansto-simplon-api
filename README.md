# Example

1) `docker build -t sim_plon_api .`

2) `docker run --rm -dt --name sim_plon_api -p 8000:8000 -p 5555:5555 sim_plon_api`

2) Start the consumer: `python examples/receiver.py`

3) Trigger the detector using our sim_plon_api: `python examples/trigger_detector.py`

NOTE: If you need to use a different HDF5 file, copy the master hdf5 file and the data file to
the `hdf5_data` folder to run this example, e.g. `testcrystal_0009_master.h5` and `testcrystal_0009_data_000001.h5`.
At the moment only one master file can be in the `hdf5_data` folder
