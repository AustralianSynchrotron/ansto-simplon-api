FROM  python:3.14

ARG UV_SYNC_EXTRA=""

ENV UV_VERSION=0.10.9
ENV PATH="/home/asuser/.venv/bin:${PATH}"
# Install OS packages
USER root
RUN apt update && apt-get install -y gcc libhdf5-serial-dev

# Create app runner user
RUN useradd -ms /bin/bash asuser
WORKDIR /home/asuser/

COPY --chown=asuser:asuser pyproject.toml uv.lock README.md /home/asuser/
COPY --chown=asuser:asuser ansto_simplon_api /home/asuser/ansto_simplon_api

RUN pip install uv==${UV_VERSION}
USER asuser
RUN uv sync --no-dev $UV_SYNC_EXTRA

EXPOSE 8000 5555
ENTRYPOINT ["uvicorn", "ansto_simplon_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
