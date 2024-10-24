from ribbon import tasks
from pathlib import Path
import shutil

# Input directory
input_dir = Path('./examples/input_dir')

# Input SMILES string
INPUT_SMILES = 'C[C@]12CC[C@H]3[C@H]([C@@H]1CCC2=O)CC[C@@H]4[C@@H]3CCC(=O)C4'
RESIDUES_TO_KEEP = 'A99'

# Run directory:
run_dir = Path('./examples/example_run_chai')

# Number of cycles
num_cycles = 3

# Set up input directory with initial structure:
cycle_start_dir = run_dir / 'cycle_start'
cycle_start_dir.mkdir(parents=True, exist_ok=True)
(cycle_start_dir / "Chai").mkdir(parents=True, exist_ok=True)
for file in input_dir.iterdir():
    shutil.copy(file, cycle_start_dir / 'Chai')


### Helper to split FASTA files:
def split_fasta(fasta_file, output_dir):
    # Each LigandMPNN input produces a FASTA with multiple outputs as > lines. Each line has 1 or more chains separated by ':'
	# Here, we separate each output into it's own FASTA file, with chains as separate > lines:
	output_dir.mkdir(parents=True, exist_ok=True)
	with open(fasta_file) as f:
		for i, line in enumerate(f):
			# Discard the first two lines, since these are the original input:
			if i < 2: continue
			# Get each line starting with >, and the following line:
			if line.startswith('>'):
				# Write out the previous sequence to a new file:
				index = 0
				# Make sure we don't overwrite existing files:
				while (output_dir / f'{fasta_file.stem}_{line[1]}_{index}.fasta').exists():
					index += 1
				with open(output_dir / f'{fasta_file.stem}_{line[1]}_{index}.fasta', 'w') as g:
					# Get name by getting first word:
					name = line.split(',')[0]
					# Get the second line, and split by ':'
					next_line = next(f).strip().split(':')
					for chain_index, chain in enumerate(next_line):
						g.write(f'{name}_{chain_index}\n')
						g.write(chain + '\n')

for i in range(num_cycles):
	# Set up directories
	current_dir = run_dir / f'cycle_{i}'
	LMPNN_dir = current_dir / 'LMPNN'
	Chai_dir = current_dir / 'Chai'
	distance_dir = current_dir / 'Distance'
	if i == 0: previous_dir = cycle_start_dir # First cycle

	# Create directories
	LMPNN_dir.mkdir(parents=True, exist_ok=True)
	Chai_dir.mkdir(parents=True, exist_ok=True)
	distance_dir.mkdir(parents=True, exist_ok=True)

	# Run ligandmpnn
	tasks.ligandmpnn(
		LMPNN_dir,
		pdb_input_dir=previous_dir / 'Chai',
		num_designs=2,										# Generate 10 sequences per previous structure
		extra_args= '--fixed_residues '+RESIDUES_TO_KEEP	# Make sure to keep my catalytric residue
	)

	# Split FASTA files
	for file in (LMPNN_dir/'seqs').iterdir():
		split_fasta(file, LMPNN_dir/'split_FASTA')

	# Run Chai-1
	for file in (LMPNN_dir/'split_FASTA').iterdir():
		tasks.chai1(
			fasta_file = file,
			smiles_string = INPUT_SMILES,
			output_dir = Chai_dir / file.stem # Each design gets it's own subdir
		)

	# Calculate Distance between D99 CG and LIG C2:
	for subdir in Chai_dir.iterdir():
		for file in subdir.iterdir():
			# Skip if not CIF:
			if file.suffix != '.cif': continue
			
			tasks.calculate_distance(
				pdb_file = file,
				chain1_id = 'D',
				res1_id = '99',
				atom1_name = 'CG',
				chain2_id = 'L',
				res2_id = '1',
				atom2_name = 'C_2',
				output_file = distance_dir / f'{file.stem}.dist'
			)

	# Update previous directory for next cycle
	previous_dir = current_dir

