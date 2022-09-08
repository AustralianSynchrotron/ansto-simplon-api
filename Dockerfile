FROM python:3.10

ENV HDF5_MASTER_FILE=/share_data/datasets_full/minimalInsulinMX1/030/testcrystal_0014_master.h5
ENV POETRY_VERSION=1.1.12

# Install OS packages
USER root
RUN apt update && apt-get install -y gcc libhdf5-serial-dev

# Create app runner user
RUN useradd -ms /bin/bash asuser
WORKDIR /home/asuser/

# Setup Poetry environment
COPY pyproject.toml poetry.lock /home/asuser/
RUN pip install "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false
RUN poetry install

# Copy across source code
COPY schemas/ /home/asuser/schemas
COPY simulate_zmq_stream.py parse_master_file.py main.py /home/asuser/
USER asuser

EXPOSE 8000 5555
ENTRYPOINT uvicorn main:app --host 0.0.0.0 --port 8000
