from ribbon.tasks import tasks
from pathlib import Path
import shutil

### SET UP INPUTS ###

# Input directory
input_dir = Path('./examples/input_dir')

# Input SMILES string
INPUT_SMILES = 'O=C1C=C(C)C(C=CC2=C3C=NO2)=C3O1'
RESIDUES_TO_KEEP = 'A99'

# Run directory:
run_dir = Path('./examples/run_TKSI_KEMP1')

# Number of cycles
num_cycles = 20


### CREATE DIRECTORIES ###
# Set up input directory with initial structure:
cycle_start_dir = run_dir / 'cycle_start'
cycle_start_dir.mkdir(parents=True, exist_ok=True)
(cycle_start_dir / "Top_Designs" / 'initial').mkdir(parents=True, exist_ok=True)
for file in input_dir.iterdir():
    shutil.copy(file, cycle_start_dir / "Top_Designs" / 'initial')


### HELPER FUNCTIONS ###
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


### MAIN LOOP ###

for i in range(num_cycles):
	
	print('-----------------------------------')
	print('---------- Cycle:', i, '-------------')
	print('-----------------------------------')
	### SET UP DIRECTORIES ###
	current_dir = run_dir / f'cycle_{i}'
	LMPNN_dir = current_dir / 'LMPNN'
	Chai_dir = current_dir / 'Chai'
	distance_dir = current_dir / 'Distance'
	top_design_dir = current_dir / 'Top_Designs'
	if i == 0: previous_dir = cycle_start_dir # First cycle

	# Create directories
	LMPNN_dir.mkdir(parents=True, exist_ok=True)
	Chai_dir.mkdir(parents=True, exist_ok=True)
	distance_dir.mkdir(parents=True, exist_ok=True)

	
	### LIGANDMPNN ###
	for subdir in (previous_dir / 'Top_Designs').iterdir():
		tasks.ligandmpnn(
			LMPNN_dir,
			pdb_input_dir= subdir,
			num_designs=5,										# Generate 5 sequences per previous structure
			extra_args= '--fixed_residues ' + RESIDUES_TO_KEEP	# Make sure to keep my catalytric residue
		)

	# Split FASTA files
	for file in (LMPNN_dir/'seqs').iterdir():
		split_fasta(file, LMPNN_dir/'split_FASTA')

	#Run Chai-1
	for file in (LMPNN_dir/'split_FASTA').iterdir():
		tasks.chai1(
			fasta_file = file,
			smiles_string = INPUT_SMILES,
			output_dir = Chai_dir / file.stem # Each design gets it's own subdir
		)

	# Calculate Distance between D99 CG and LIG C2:
	for subdir in Chai_dir.iterdir():
		for file in Path(subdir).iterdir():
			# Skip if not CIF:
			if file.suffix != '.cif': continue
			
			# Get name of subdir:
			subdir = Path(subdir).name

			# Make sure directory exists:
			(distance_dir / subdir).mkdir(parents=True, exist_ok=True)

			# Calculate distance:
			tasks.calculate_distance(
				pdb_file = file,
				#Protein info:
				chain1_id = 'A',
				res1_id = '99',
				atom1_name = 'CG',
				#Ligand info:
				chain2_id = 'B',
				res2_id = '1',
				atom2_name = 'C_10',
				#Output file:
				output_file = distance_dir / subdir / f'{file.stem}.dist'
			)

	distance_dict = {}
	for design in distance_dir.iterdir():
		# Get name of subdir:
		design_name = design.name

		for file in Path(design).iterdir():
			# Skip if not distance file:
			if file.suffix != '.dist': continue

			# Write out the distance to a dictionary:
			with open(file) as f:
				distance = float(f.read())
				distance_dict[design_name+'/'+file.stem + '.cif'] = distance

	total_designs = len(distance_dict)

	# Get the top 10, by lowest distance:
	top_designs = dict(sorted(distance_dict.items(), key=lambda item: item[1])[:10]) # Get top 10 designs 
	
	# Copy top designs to new directory:
	top_design_dir.mkdir(parents=True, exist_ok=True)
	for design in top_designs:
		# Get the subdir:
		subdir = design.split('/')[0]
		# Make sure directory exists:
		(top_design_dir / subdir).mkdir(parents=True, exist_ok=True)
		# Copy the design:
		shutil.copy(Chai_dir / design, top_design_dir / design)

	# Update previous directory for next cycle
	previous_dir = current_dir

