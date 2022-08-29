FROM python:3.9

ENV HDF5_MASTER_FILE=/share_data/4Mrasterdata/01x10/testraster01_0008_master.h5
ENV POETRY_VERSION=1.1.13

# Install OS packages
USER root
RUN apt update && apt-get install -y gcc libhdf5-serial-dev

# Create app runner user
RUN useradd -ms /bin/bash asuser

# Copy across source code
WORKDIR /home/asuser/
COPY pyproject.toml poetry.lock simulate_zmq_stream.py \
    parse_master_file.py main.py /home/asuser/
COPY schemas/ /home/asuser/schemas

# Setup Poetry environment
RUN pip install "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false
RUN poetry install

USER asuser

EXPOSE 8000 5555
ENTRYPOINT uvicorn main:app --host 0.0.0.0 --port 8000
