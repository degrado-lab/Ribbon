#!/bin/bash
## Run from the root of the project
echo "Building Ribbon container"

# Build the docker image
docker build -f container/Dockerfile -t nicholasfreitas/ribbon:docker .

# Push the docker image
docker push nicholasfreitas/ribbon:docker

# Build the apptainer:
apptainer build ribbon.sif container/ribbon.def

# Push the apptainer
apptainer push ribbon.sif oras://docker.io/nicholasfreitas/ribbon:latest