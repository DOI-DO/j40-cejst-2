FROM ubuntu:24.04

# Install packages
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y \
    software-properties-common \
    tippecanoe \
    libgdal-dev
    
# Install python3.10 and dependencies
RUN add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update -y && \
    apt remove python3-cryptography -y && \
    apt install -y python3.10-dev && \
    apt install -y python3-pip && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 && \
    update-alternatives --config python3 && \
    pip install cryptography && \
    pip install cffi && \
    pip install openpyxl

# Set the working directory
WORKDIR /data-pipeline

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 \
    PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.4 

# Install poetry
RUN apt-get update -y && \
    pip install "poetry==$POETRY_VERSION" 

# Copy configs and install packages
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry config virtualenvs.in-project false && \
    poetry install --only main --no-interaction --no-ansi

# Copy all project files into the container
COPY . .

# Default behavior is to output the options for the base application. This prevents the entire pipeline from running unintentionally.
ENV PIPELINE_CMD="data_pipeline.application --help"
CMD ["sh", "-c", "poetry run python3 -m $PIPELINE_CMD"]