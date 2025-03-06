import ribbon
from ribbon.utils import list_files
from pathlib import Path

starting_structure = 'my_happy_protein.pdb'
output_directory = Path('./out')

# We start with just our initial structure:
structures_to_resequence = [starting_structure]

import time
start_time = time.time()

def rename_files(directory, extension):
    '''Remove the ".RaptorX-Single-ESM1b" from the end of the file names'''
    for file in list_files(directory, extension):
        new_name = file.replace('.RaptorX-Single-ESM1b', '')
        Path(file).rename(new_name)

for i in range(3):

    # Make the output directory:
    current_output_dir = output_directory / f'iter_{i}'
    current_output_dir.mkdir(exist_ok=True, parents=True)

    # First, we create 5 new sequences for this structure:
    ribbon.LigandMPNN(
        structure_list = structures_to_resequence,
        output_dir = current_output_dir / 'lmpnn',
        num_designs = 5
    ).run()
    # These sequences are split into individual files, and are stored in 'out/iter_[X]/lmpnn/seqs_split'

    # Then, we fold using RaptorX:
    ribbon.RaptorXSingle(
            fasta_file_or_dir = current_output_dir / 'lmpnn' / 'seqs_split',
            output_dir = current_output_dir / 'raptorx'
    ).run()
    # The PDB structures are stored in 'out/iter_[X]/raptorx/'

    # The names get messy, so we'll clean them up:
    rename_files(current_output_dir / 'raptorx', '.pdb')

    # We'll make a list of these files, to pass back in to the next iteration:
    structures_to_resequence = list_files(current_output_dir / 'raptorx', '.pdb')

print('Done!')
print('Total time elapsed:', time.time() - start_time)