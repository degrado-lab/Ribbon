#ribbon?
from utils import ribbon_decorator, make_directories, directory_to_list
import os
import tempfile
import shutil
import json
import utils
from pathlib import Path

@ribbon_decorator('LigandMPNN')
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


@ribbon_decorator('FastRelax')
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

# Types of inputs:
# FASTA_FILE
# FASTA_DIR
# PDB_FILE
# PDB_DIR