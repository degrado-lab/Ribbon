import os
import subprocess
from pathlib import Path
import pickle
from ribbon.config import DOWNLOAD_DIR, MODULE_DIR, TASK_CACHE_DIR
import uuid
import datetime

#def directory_to_list(directory, extension):
#    '''Returns a list of files in a directory with a given extension'''
#    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(extension)]

def list_files(directory, extension):
    '''Returns a list of files in a directory with a given extension'''
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(extension)]

def make_directories(*directories):
    '''Creates directories if they do not exist. 
    Returns a list of Path objects, in case they were strings.'''
    new_directories = []
    for directory in directories:
        # Check it's a Path object:
        if not isinstance(directory, Path):
            directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        new_directories.append(directory)
    return new_directories

def make_directory(directory):
    '''Creates a directory if it does not exist. 
    Returns a Path object, in case it was a string.'''
    directory = make_directories(directory)[0]
    return directory

def verify_container(software_name):
   # Get the container local path and ORAS URL:
    import json
    with open(MODULE_DIR / 'tasks' / 'containers.json') as f:
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

def run_command(command):
	# Run the container
    subprocess.run(command, shell=True)
    #print(result.stdout)
    #if result.stderr:
    #    print(result.stderr)
    return # Get error codes, etc.
	
def serialize(obj, save_dir=None):
    '''Saves a Python object to a file. A random filename is generated, and it is saved to the save_dir.
    Returns: the filename of the saved object.'''
    if save_dir is None:
        save_dir = TASK_CACHE_DIR
    # Make sure the directory exists:
    print(save_dir)
    save_dir = make_directory(save_dir)

    print('Saving object to:', save_dir)

    # Generate a random filename:
    filename = save_dir / f'{uuid.uuid4()}.pkl'

    # Save the object:
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)

    return filename

def deserialize(filename, cache_dir=None):
    '''Loads a Python object from a file'''

    # Make sure we have the full path:
    if cache_dir is None:
        cache_dir = TASK_CACHE_DIR
    cache_dir = make_directory(cache_dir)

    filename = Path(filename)
    if not filename.is_absolute():
        filename = cache_dir / filename
    
    with open(filename, 'rb') as f:
        return pickle.load(f)
    
def clean(all=False):
    ''' Cleans the cache directory. If all=True, deletes all files. Otherwise, deletes only files that are older than 1 day.'''
    for file in os.listdir(TASK_CACHE_DIR):
        file = Path(file)
        if all or (datetime.datetime.now() - datetime.datetime.fromtimestamp(file.stat().st_mtime)).days > 1:
            os.remove(file)