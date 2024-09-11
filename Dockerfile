FROM python:3.12

ENV POETRY_VERSION=1.8.3

# Install OS packages
USER root
RUN apt update && apt-get install -y gcc libhdf5-serial-dev

# Create app runner user
RUN useradd -ms /bin/bash asuser
WORKDIR /home/asuser/

# Setup Poetry environment
COPY pyproject.toml poetry.lock README.md /home/asuser/
RUN pip install "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false
RUN poetry install

# Copy across source code
COPY ansto_simplon_api /home/asuser/ansto_simplon_api
USER asuser

EXPOSE 8000 5555
ENTRYPOINT uvicorn ansto_simplon_api.main:app --host 0.0.0.0 --port 8000
