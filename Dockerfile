FROM python:3.9

ARG HDF5_FOLDER_PATH=hdf5_data

EXPOSE 8000 5555

ENV POETRY_VERSION=1.1.13

RUN apt update

RUN apt-get install -y gcc libhdf5-serial-dev

WORKDIR /home/asuser/

COPY pyproject.toml poetry.lock /home/asuser/

COPY $HDF5_FOLDER_PATH /home/asuser/

RUN pip install "poetry==$POETRY_VERSION"

RUN poetry config virtualenvs.create false

RUN poetry install

COPY simulate_zmq_stream.py parse_master_file.py main.py /home/asuser/

ENTRYPOINT uvicorn main:app --host 0.0.0.0 --port 8000
