# syntax=docker/dockerfile:1.9

# Global build arguments
ARG PYTHON_VERSION=3.12


FROM python:${PYTHON_VERSION}-slim-bookworm AS base_runtime

ARG DEBIAN_FRONTEND=noninteractive
ARG PYTHONUNBUFFERED=1
ARG PIP_DISABLE_PIP_VERSION_CHECK=1
ARG PIP_ROOT_USER_ACTION=ignore
ARG AS_PIP_INDEX_URL="https://pypi.asci.synchrotron.org.au/root/pypi/+simple"
ARG POETRY_VIRTUALENVS_IN_PROJECT=true
ARG POETRY_VIRTUALENVS_CREATE=false
ARG POETRY_NO_INTERACTION=1
ARG POETRY_VERSION=1.8.3
ARG POETRY_DEPENDENCY_GROUPS=main
ARG PIPX_BIN_DIR="/usr/local/bin/"
ARG USE_EMOJI="false"
ENV HDF5_MASTER_FILE=/mnt/disk/dev_share/datasets_full/minimalInsulinMX1/030/testcrystal_0014_master.h5

# Install system packages
RUN <<EOT bash
set -eux
apt-get update
apt-get install -y libhdf5-serial-dev gcc ca-certificates curl wget
rm -rf /var/lib/apt/lists/*
EOT

# Install `pipx` package manager
COPY --link <<EOF requirements.txt
argcomplete  == 3.3.0 --hash=sha256:c168c3723482c031df3c207d4ba8fa702717ccb9fc0bfe4117166c1f537b4a54
packaging    == 24.0  --hash=sha256:2ddfb553fdf02fb784c234c7ba6ccc288296ceabec964ad2eae3777778130bc5
platformdirs == 4.2.2 --hash=sha256:2d7a1657e36a80ea911db832a8a6ece5ee53d8de21edd5cc5879af6530b1bfee
userpath     == 1.9.2 --hash=sha256:2cbf01a23d655a1ff8fc166dfb78da1b641d1ceabf0fe5f970767d380b14e89d
pipx         == 1.5.0 --hash=sha256:801a55a9d58004bb18a464f668508e79fbffc22deb6f07982832d3ce3ff3756d
EOF
RUN <<EOT /bin/sh
_pip_index_url="https://pypi.org/simple"
_pip_user_agent=python - <<-\GET_PIP_USER_AGENT
from sys import stdout
from pip._internal.network.session import user_agent
stdout.write(user_agent())
GET_PIP_USER_AGENT

# Check if configured index is actually network accessible
if wget --spider -T 10 -U "${_pip_user_agent}" -q "${AS_PIP_INDEX_URL}"; then
    # Index is network accessible
    _pip_index_url="${AS_PIP_INDEX_URL}"
fi

# Install Python dependencies
pip install \
    --no-deps \
    --ignore-installed \
    --compile \
    --require-hashes \
    --progress-bar off \
    --no-clean \
    --extra-index-url "${_pip_index_url}" \
    --no-input \
    --no-cache-dir \
    --no-color \
    -r requirements.txt
rm ./requirements.txt
EOT

# Add entrypoint script
WORKDIR /opt/mx_sim_plon_api
COPY --chmod=744 <<'EOF' entrypoint.sh
#!/usr/bin/env bash
set -e;
exec "$@"
EOF

# Install Poetry package manager
RUN pipx install "poetry==${POETRY_VERSION}"

# Install Python dependencies
COPY --link ./pyproject.toml ./poetry.lock ./
RUN poetry install --compile --only "${POETRY_DEPENDENCY_GROUPS}"

# Copy across source code
COPY --link ./ansto_simplon_api ./ansto_simplon_api
COPY --link ./README.md ./

EXPOSE 8000
ENTRYPOINT [ "/opt/mx_sim_plon_api/entrypoint.sh" ]
CMD [ "fastapi", "run", "./ansto_simplon_api/main.py", "--port=8000" ]


FROM base_runtime AS runtime

ARG BUILD_GIT_AUTHOR
ARG BUILD_GIT_AUTHOR_NAME
ARG BUILD_GIT_BRANCH
ARG BUILD_GIT_COMMIT
ARG BUILD_CREATED
ARG BUILD_NUMBER
ARG BUILD_GIT_REPO_LINK

WORKDIR /opt/mx_sim_plon_api
COPY <<EOF .build_info.json
{
    "build_author": "${BUILD_GIT_AUTHOR}",
    "build_author_name": "${BUILD_GIT_AUTHOR_NAME}",
    "build_branch": "${BUILD_GIT_BRANCH}",
    "build_commit": "${BUILD_GIT_COMMIT}",
    "build_date": ${BUILD_CREATED:-null},
    "build_number": ${BUILD_NUMBER:-null},
    "build_repository": "${BUILD_GIT_REPO_LINK}"
}
EOF


FROM base_runtime AS debug_runtime

COPY --link ./.git ./.git
