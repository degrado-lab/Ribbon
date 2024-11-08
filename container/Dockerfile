# docker build -f container/Dockerfile -t nicholasfreitas/ribbon:docker .

# Use Ubuntu as the base image
FROM ubuntu:22.04

# Set environment variables to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Miniconda dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        bzip2 \
        ca-certificates \
        software-properties-common \
        gnupg \
        sudo && \
    rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    /bin/bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

# Update PATH environment variable
ENV PATH="/opt/conda/bin:${PATH}"

# Add the Apptainer PPA
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:apptainer/ppa

# Install Apptainer
RUN apt-get update && \
    apt-get install -y apptainer

# Copy the current directory contents into /app inside the container
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Install your package using pip
RUN pip install .

