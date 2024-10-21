from utils import make_directories, directory_to_list
import os
import tempfile
import shutil
import json
import utils
from pathlib import Path

#@ribbon_decorator('LigandMPNN')
def ligandmpnn(output_dir, pdb_input_file=None, pdb_input_dir=None, num_designs=1, container_path=None):
	# Must specify either pdb_input_file OR pdb_input_dir
    if pdb_input_file is None and pdb_input_dir is None:
        raise ValueError('Must specify either pdb_input_file or pdb_input_dir')

	# If pdb_input_file is not None, copy the file to a temporary directory
    if pdb_input_file is not None:
        temp_dir = tempfile.mkdtemp()
        shutil.copy(pdb_input_file, temp_dir)
        pdb_input_dir = temp_dir

    # Make directories:
    output_dir, pdb_input_dir = make_directories(output_dir, pdb_input_dir)

    # Compile all our PDB files into a list:
    pdb_files = directory_to_list(pdb_input_dir, '.pdb')

    # Then, write out the files within pdb_input_dir to a json file:
    pdb_input_json = output_dir / 'pdb_input.json'
    with open(pdb_input_json, 'w') as f:
        json.dump(pdb_files, f)
    print(f'pdb_input_json: {pdb_input_json}')
	
    # Example implementation of running task defined in JSON:
    utils.run_task("LigandMPNN", pdb_input_dir, output_dir, num_designs)
	
    # Clean up the temporary directory. Eventually fix this using TempFile
    if pdb_input_file is not None:
        shutil.rmtree(temp_dir)

    return 


#@ribbon_decorator('FastRelax')
def fastrelax(output_dir, pdb_input_file=None, pdb_input_dir=None, container_path=None):
	# Must specify either pdb_input_file OR pdb_input_dir
    if pdb_input_file is None and pdb_input_dir is None:
        raise ValueError('Must specify either pdb_input_file or pdb_input_dir')

	# If pdb_input_file is not None, copy the file to a temporary directory
    if pdb_input_file is not None:
        temp_dir = tempfile.mkdtemp()
        shutil.copy(pdb_input_file, temp_dir)
        pdb_input_dir = temp_dir

    # Make directories:
    output_dir = make_directories(output_dir)

    # Join many PDBs into a string to pass to the command
    pdb_list = directory_to_list(pdb_input_dir, '.pdb')
    pdb_string = " ".join(map(str, pdb_list)) + " "
	
	# Specify the command to run
    #example:
    #ribbon.run_task("FastRelax", pdb_input_dir, output_dir)
    command = f'apptainer run --nv {container_path} relax -in:file:s {pdb_string} -out:path:pdb {output_dir} -out:path:score {output_dir}'

    utils.run_command(command) # What do we do with errors? Raise error codes, display, ignore?

    return


def run_task(task_name, extra_args="", **kwargs ):
    ''' Run a task with the given name and arguments.
    Inputs:
        task_name: str - the name of the task to run
        extra_args: str - additional arguments to pass to the task, which is optional. E.g. '--save_frequency 10 --num_steps 1000'
        kwargs: dict - the arguments to pass to the task. These are task-specific.
    Outputs:
        None
    '''
    # Add extra_args to kwargs:
    kwargs['extra_args'] = extra_args

    # Which inputs does our task require?
    required_inputs = utils.get_task_inputs(task_name)
    print(required_inputs)

    # Check that we have all the required inputs
    for input in required_inputs:
        if input not in kwargs:
            raise ValueError(f'Input {input} is required for task {task_name}')
        print(f'{input}: {kwargs[input]}')

    # Get Information about the task:
    task_dict = utils.get_task_dict(task_name)
    task_name = task_dict['name']
    container_name = task_dict['container']
    print('Task name:', task_name)
    print('Task description:', task_dict['description'])

    # Verify we have the container associated with the software we want to run. 
    # If not, attempt to download it to the download_dir
    container_path = utils.verify_container(container_name)

    # Add inputs to the command, by replacing the placeholders in the command string:
    command = task_dict['command']
    for input in required_inputs:
        command = command.replace(f'{{{input}}}', str(kwargs[input]))
    
    print('Command:', command)

    # Run the task
    apptainer_command = f'apptainer run --nv {container_path} {command}'
    utils.run_command(apptainer_command)


run_task("LigandMPNN", pdb_input_json='test', output_dir='test', num_designs=1, extra_args='--butt face')