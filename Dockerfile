FROM  python:3.11
ENV UV_VERSION=0.8.15
# Install OS packages
USER root
RUN apt update && apt-get install -y gcc libhdf5-serial-dev

# Create app runner user
RUN useradd -ms /bin/bash asuser
WORKDIR /home/asuser/

# Setup Poetry environment
COPY pyproject.toml uv.lock README.md /home/asuser/
COPY ansto_simplon_api /home/asuser/ansto_simplon_api

RUN pip install uv==${UV_VERSION}
RUN uv sync


# Copy across source code
USER asuser

EXPOSE 8000 5555
ENTRYPOINT uv run uvicorn ansto_simplon_api.main:app --host 0.0.0.0 --port 8000
