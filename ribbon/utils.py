import os
import subprocess
from pathlib import Path
import json
from ribbon.config import DOWNLOAD_DIR, MODULE_DIR

#def directory_to_list(directory, extension):
#    '''Returns a list of files in a directory with a given extension'''
#    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(extension)]

def list_files(directory, extension):
    '''Returns a list of files in a directory with a given extension'''
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(extension)]

def make_directories(*directories):
    '''Creates directories if they do not exist. 
    Returns a list of Path objects, in case they were strings.'''
    for directory in directories:
        # Check it's a Path object:
        if not isinstance(directory, Path):
            directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
    return directories

def make_directory(directory):
    '''Creates a directory if it does not exist. 
    Returns a Path object, in case it was a string.'''
    if not isinstance(directory, Path):
        directory = make_directories(directory)[0]
    return directory

def verify_container(software_name):
   # Get the container local path and ORAS URL:
    import json
    with open(MODULE_DIR / 'containers.json') as f:
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
    # Make sure downloads directory exists:
    make_directories(DOWNLOAD_DIR)

    # Download the container to the download_dir
    command = f'apptainer pull {container_local_path} {container_ORAS_URL}'
    run_command(command)

    return # Get error codes, etc.

def get_task_dict(task_name):
    '''Returns the dictionary for a given task'''
    # Which inputs does our task require?
    with open(MODULE_DIR / 'tasks.json') as f:
        tasks = json.load(f)

    return tasks[task_name]

def get_task_inputs(task_name):
    '''Returns the inputs required for a given task'''
    #Get the command:
    command = get_task_dict(task_name)['command']

    #Inputs are surrounded by curly braces. Here we extract them.
    inputs = [i[1:-1] for i in command.split() if i.startswith('{') and i.endswith('}')]

    #Remove duplicates:
    inputs = list(set(inputs))
    
    return inputs

def run_command(command):
	# Run the container
    subprocess.run(command, shell=True)
    #print(result.stdout)
    #if result.stderr:
    #    print(result.stderr)
    return # Get error codes, etc.
	
    