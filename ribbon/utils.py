import os
import subprocess
from pathlib import Path
from config import DOWNLOAD_DIR



def ribbon_decorator(software_name):
    def ribbon_decorator_internal(func):
        def wrapper(*args, **kwargs):

                # Verify we have the container associated with the software we want to run. 
                # If not, attempt to download it to the download_dir
                container_path = verify_container(software_name)

                return func(*args, **kwargs, container_path=container_path)
        
        return wrapper
    
    return ribbon_decorator_internal

def verify_container(software_name):
   # Get the container local path and ORAS URL:
    import json
    with open('containers.json') as f:
        containers = json.load(f)

    # Our database maps software names to container names and ORAS URLs
    # Example:  {"LigandMPNN": ["ligandMPNN.sif", "oras://docker.io/nicholasfreitas/ligandmpnn:latest"]}
    container_local_name, container_ORAS_URL = containers[software_name]
    container_local_path = DOWNLOAD_DIR / container_local_name

    # Is the container already downloaded?
    if not os.path.exists(container_local_path):
        # If not, download the container
        download_container(container_local_path, container_ORAS_URL)
    
    return container_local_path

def download_container(container_local_path, container_ORAS_URL):
    # Download the container to the download_dir
    command = f'apptainer pull {container_local_path} {container_ORAS_URL}'
    run_command(command)

    return # Get error codes, etc.

def run_command(command):
	# Run the container
    subprocess.run(command, shell=True) #command.split() ?

    return # Get error codes, etc.
	
    