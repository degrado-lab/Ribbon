import runners
from pathlib import Path

# Input directory
input_dir = Path('./examples/input_dir')

# Run directory:
run_dir = Path('./examples/example_run')

# Number of cycles
num_cycles = 3

for i in range(num_cycles):
	# Set up directories
	current_dir = run_dir / f'cycle_{i}'
	LMPNN_dir = current_dir / 'LMPNN'
	FR_dir = current_dir / 'FR'
	if i == 0: previous_dir = input_dir # First cycle

	# Create directories
	LMPNN_dir.mkdir(parents=True, exist_ok=True)
	FR_dir.mkdir(parents=True, exist_ok=True)

	# Run ligandmpnn
	runners.ligandmpnn(
		pdb_input_dir=previous_dir / 'FR',
		output_dir=LMPNN_dir,
		num_designs=2						# Generate 10 sequences per previous structure
	)

	# Run fastrelax on generated backbones
	runners.fastrelax(
		pdb_input_dir = LMPNN_dir / 'backbones',
		output_dir=FR_dir
	)

	# Update previous directory for next cycle
	previous_dir = current_dir
