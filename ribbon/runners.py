#ribbon?
from utils import ribbon_decorator
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
        # Create a temporary directory to store the input files
        temp_dir = tempfile.mkdtemp()
        # Copy the input file to the temp_dir
        shutil.copy(pdb_input_file, temp_dir)
        # Set the pdb_input_dir to the temp_dir
        pdb_input_dir = temp_dir

    # Make directories:
    output_dir, pdb_input_dir = Path(output_dir), Path(pdb_input_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pdb_input_dir.mkdir(parents=True, exist_ok=True)

    # Then, write out the files within pdb_input_dir to a json file:
    pdb_input_json = output_dir / 'pdb_input.json'
    pdb_files = [os.path.join(pdb_input_dir, f) for f in os.listdir(pdb_input_dir) if f.endswith('.pdb')]
    with open(pdb_input_json, 'w') as f:
        json.dump(pdb_files, f)

    print(f'pdb_input_json: {pdb_input_json}')
	
	# Specify the command to run
    command = f'apptainer run --nv {container_path} LigandMPNN/run.py --pdb_path_multi {pdb_input_json} --out_folder {output_dir} --batch_size {num_designs}'

    utils.run_command(command) # What do we do with errors? Raise error codes, display, ignore?
	
    # Clean up the temporary directory. Eventually fix this using TempFile
    if pdb_input_file is not None:
        shutil.rmtree(temp_dir)

    return #what? True if it worked? Error/completion code?


@ribbon_decorator('FastRelax')
def fastrelax(output_dir, pdb_input_file=None, pdb_input_dir=None, container_path=None):
	# Must specify either pdb_input_file OR pdb_input_dir
    if pdb_input_file is None and pdb_input_dir is None:
        raise ValueError('Must specify either pdb_input_file or pdb_input_dir')

	# If pdb_input_file is not None, copy the file to a temporary directory
    if pdb_input_file is not None:
        # Create a temporary directory to store the input files
        temp_dir = tempfile.mkdtemp()
        # Copy the input file to the temp_dir
        shutil.copy(pdb_input_file, temp_dir)
        # Set the pdb_input_dir to the temp_dir
        pdb_input_dir = temp_dir

    # Make directories:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Join many PDBs into a string to pass to the command
    pdb_list = pdb_input_dir.glob('*.pdb')
    pdb_string = " ".join(map(str, pdb_list)) + " "
	
	# Specify the command to run
    command = f'apptainer run --nv {container_path} relax -in:file:s {pdb_string} -out:path:pdb {output_dir} -out:path:score {output_dir}'

    utils.run_command(command) # What do we do with errors? Raise error codes, display, ignore?

    return #what? True if it worked? Error/completion code?

# Types of inputs:
# FASTA_FILE
# FASTA_DIR
# PDB_FILE
# PDB_DIR