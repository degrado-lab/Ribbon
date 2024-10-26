from ribbon.utils import make_directories, make_directory, directory_to_list
from ribbon.runner import run_task
from pathlib import Path
import tempfile
import shutil
import json

def ligandmpnn(output_dir, pdb_input_file=None, pdb_input_dir=None, num_designs=1, extra_args="",):
    ''' Run the LigandMPNN task.
    Args:
        output_dir (str): 
            The directory to save the output files.
            This will have the contents:
                - backbones: The generated backbones
                - packed: The packed structures, including sidechains
                - sequences: The generated sequences as FASTA files. Multiple chains are separated by ':'. Each line is a different design.
        pdb_input_file (str), pdb_input_dir (str): 
            The input PDB file or directory containing PDB files. Must use one or the other.
        num_designs (int): The number of designs to generate per input structure.
    Returns:
        None'''
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

    # Compile all our PDB and/or CIF files into a list:
    pdb_files = directory_to_list(pdb_input_dir, '.pdb') + directory_to_list(pdb_input_dir, '.cif')

    # Then, write out the files within pdb_input_dir to a json file:
    pdb_input_json = output_dir / 'pdb_input.json'
    with open(pdb_input_json, 'w') as f:
        json.dump(pdb_files, f)
    print(f'pdb_input_json: {pdb_input_json}')
	
    # Run the task:
    run_task("LigandMPNN", 
                pdb_input_json = pdb_input_json, 
                output_dir = output_dir, 
                num_designs = num_designs,
                extra_args = extra_args)
	
    # Clean up the temporary directory. Eventually fix this using TempFile
    if pdb_input_file is not None:
        shutil.rmtree(temp_dir)

    return 

def fastrelax(output_dir, pdb_input_file=None, pdb_input_dir=None):
	# Must specify either pdb_input_file OR pdb_input_dir
    if pdb_input_file is None and pdb_input_dir is None:
        raise ValueError('Must specify either pdb_input_file or pdb_input_dir')

	# If pdb_input_file is not None, copy the file to a temporary directory
    if pdb_input_file is not None:
        temp_dir = tempfile.mkdtemp()
        shutil.copy(pdb_input_file, temp_dir)
        pdb_input_dir = temp_dir

    # Make directories:
    output_dir = make_directory(output_dir)

    # Join many PDBs into a string to pass to the command
    pdb_list = directory_to_list(pdb_input_dir, '.pdb')
    pdb_string = " ".join(map(str, pdb_list)) + " "

    # Run the task:
    run_task("FastRelax", 
                pdb_string = pdb_string, 
                output_dir = str(output_dir))

    return

def chai1(fasta_file, smiles_string, output_dir):
    ''' Run the Chai-1 task.
    Args:
        fasta_file (str): 
            The FASTA file containing the protein sequence (no ligand). Only runs 1 system, with multiple chains/ligands optional.
        smiles_string (str): 
            The SMILES string of the ligand.
        output_dir (str):
            The directory to save the output files.
    '''
    # Make directories:
    output_dir = make_directory(output_dir)

    # Run the task:
    run_task("Chai-1", 
                fasta_file = fasta_file,
                smiles_string = smiles_string, 
                output_dir = str(output_dir))

    return

def calculate_distance(pdb_file, chain1_id, res1_id, atom1_name, chain2_id, res2_id, atom2_name, output_file):
    ''' Calculate the distance between two atoms in a PDB file.
    Args:
        pdb_file (str): Path to the PDB file
        chain1_id (str): Chain ID of the first atom
        res1_id (str): Residue ID of the first atom
        atom1_name (str): Name of the first atom
        chain2_id (str): Chain ID of the second atom
        res2_id (str): Residue ID of the second atom
        atom2_name (str): Name of the second atom
        output_file (str): Path to the output file
    Returns:
        distance (float): The distance between the two atoms
    '''
    # Make directories:
    make_directory(Path(output_file).parent)

    # Run the task:
    run_task("Calculate Distance", 
                pdb_file = pdb_file,
                chain1_id = chain1_id,
                res1_id = res1_id,
                atom1_name = atom1_name,
                chain2_id = chain2_id,
                res2_id = res2_id,
                atom2_name = atom2_name,
                output_file = output_file)

    return