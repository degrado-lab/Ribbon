from ribbon.tasks import tasks
from ribbon.utils import make_directories, list_files
from pathlib import Path
import shutil

####### SET UP INPUTS #######

# Input directory, run directory:
input_dir = Path('./examples/input_dir')
run_dir = Path('./examples/run_TKSI_KEMP1_2')

# Input SMILES string, and residues to keep in the design:
INPUT_SMILES = 'O=C1C=C(C)C(C=CC2=C3C=NO2)=C3O1'
RESIDUES_TO_KEEP = 'A99'

# Number of cycles
NUM_CYCLES = 5

###### CREATE DIRECTORIES ######
cycle_start_dir = run_dir / 'cycle_start'
initial_structures_dir = cycle_start_dir / 'Top_Designs' # This is where we copy our initial structure
make_directories(run_dir, initial_structures_dir)
# And, copy our inputs: 
for file in input_dir.iterdir():
    shutil.copy(file, cycle_start_dir / "Top_Designs" )

###### MAIN LOOP #######

for i in range(NUM_CYCLES):
	
	print('-----------------------------------')
	print('---------- Cycle:', i, '-------------')
	print('-----------------------------------')
	
	###### SET UP DIRECTORIES #######
	current_dir = 		run_dir / f'cycle_{i}'
	LMPNN_dir = 		current_dir / 'LMPNN'
	Chai_dir = 			current_dir / 'Chai'
	distance_dir = 		current_dir / 'Distance'
	top_design_dir = 	current_dir / 'Top_Designs'

	if i == 0: 	
		previous_dir = cycle_start_dir # First cycle
	
	# Create directories
	make_directories(current_dir, LMPNN_dir, Chai_dir, distance_dir, top_design_dir)


	######## RUN LIGANDMPNN #########
	old_structures_list = list_files(previous_dir / 'Top_Designs', '.cif') + list_files(previous_dir / 'Top_Designs', '.pdb')
	print('Number of structures:', len(old_structures_list))

	tasks.ligandmpnn(
		LMPNN_dir,
		structure_list=old_structures_list,
		num_designs=2,										# Generate 5 sequences per previous structure
		extra_args= '--fixed_residues ' + RESIDUES_TO_KEEP	# Make sure to keep my catalytric residue
	)
	
	######## RUN CHAI-1 #########
	sequences_list = list_files(LMPNN_dir / 'seqs_split', '.fasta')

	for file in sequences_list:
		file = Path(file)
		tasks.chai1(
			fasta_file = file,
			smiles_string = INPUT_SMILES,
			output_prefix = file.stem, # Our output will be named this, + '_pred_X.cif'
			output_dir = Chai_dir,
		)


	######## CALCULATE DISTANCE #########
	new_structures = list_files(Chai_dir, '.cif')

	for file in new_structures:
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
			output_file = distance_dir / f'{Path(file).stem}.dist'
		)


	######## GET TOP DESIGNS #########
	distance_files = list_files(distance_dir, '.dist')

	distance_dict = {}
	for file in distance_files:
		file = Path(file)
		# Write out the distance to a dictionary:
		with open(file) as f:
			distance = float(f.read())
			distance_dict[file.stem + '.cif'] = distance

	# Get the top 10, by lowest distance:
	top_designs = dict(sorted(distance_dict.items(), key=lambda item: item[1])[:10]) # Get top 10 designs 
	
	for design in top_designs:
		# Copy the design:
		shutil.copy(Chai_dir / design, top_design_dir / design)

	######## UPDATE DIRECTORIES #########
	previous_dir = current_dir

