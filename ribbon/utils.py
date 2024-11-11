import os
import subprocess
from pathlib import Path
import pickle
from ribbon.batch.queue_utils import sge_check_job_status
from ribbon.config import DOWNLOAD_DIR, TASKS_DIR, TASK_CACHE_DIR
import uuid
import datetime
import time

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
    print('TASKS_DIR:', TASKS_DIR)
    with open( TASKS_DIR / 'containers.json') as f:
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

def run_command(command, capture_output=False):
    '''
    Runs a command in the shell.
    If capture_output=True, returns the stdout and stderr.
    Otherwise, returns prints the stdout and stderr.
    '''
	# Run the container
    stdout, stderr = None, None
    print('Running command:', command)
    if capture_output:
        process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # return stdout and stderr
        stdout, stderr = process.stdout.decode('utf-8'), process.stderr.decode('utf-8')
    else:
        process = subprocess.run(command, shell=True)
    return stdout, stderr
	
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

def wait_for_jobs(job_ids, max_wait=3600):
    '''Waits for a list of job IDs to complete. Returns when all jobs are completed.
    - job_ids: list of job IDs
    - max_wait: maximum time to wait in seconds. Default is 1 hour.'''
    ### TODO: Add a required parameter for scheduler. For now, we assume SGE.
    ### TODO: Add kill_after parameter to kill jobs if we exceed max_wait. Default false.
    start_time = datetime.datetime.now()

    # Print status:
    waiting_for = len(job_ids)
    print(f'Waiting for {waiting_for} jobs to complete...')

    while True:

        # Check if all jobs are completed:
        all_completed = True
        not_finished_count = 0
        statuses = sge_check_job_status(job_ids)
        for job_id, status in statuses.items():
            if status == 'not completed':
                all_completed = False
                not_finished_count += 1
        if all_completed:
            break # All jobs are completed, we're done!

        # Print status, only when it changes:
        if not_finished_count != waiting_for:
            waiting_for = not_finished_count
            print(f'Waiting for {waiting_for} jobs to complete...')

        # Check if we've waited too long:
        elapsed_time = (datetime.datetime.now() - start_time).seconds
        if elapsed_time > max_wait:
            print('Max wait time exceeded. Exiting.')
            break

        # Wait for a bit before checking again:
        time.sleep(10)

    return