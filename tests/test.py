from ribbon.tasks import tasks
from pathlib import Path
import shutil

# Input directory
input_dir = Path('./examples/input_dir')

# Run directory:
run_dir = Path('./examples/example_run')

# Number of cycles
num_cycles = 3

# Set up input directory with initial structure:
cycle_start_dir = run_dir / 'cycle_start'
cycle_start_dir.mkdir(parents=True, exist_ok=True)
(cycle_start_dir / "FR").mkdir(parents=True, exist_ok=True)
for file in input_dir.iterdir():
    shutil.copy(file, cycle_start_dir / 'FR')

for i in range(num_cycles):
	# Set up directories
	current_dir = run_dir / f'cycle_{i}'
	LMPNN_dir = current_dir / 'LMPNN'
	FR_dir = current_dir / 'FR'
	if i == 0: previous_dir = cycle_start_dir # First cycle

	# Create directories
	LMPNN_dir.mkdir(parents=True, exist_ok=True)
	FR_dir.mkdir(parents=True, exist_ok=True)

	# Run ligandmpnn
	tasks.ligandmpnn(
		LMPNN_dir,
		pdb_input_dir=previous_dir / 'FR',
		num_designs=2						# Generate 10 sequences per previous structure
	)

	# Run fastrelax on generated backbones
	tasks.fastrelax(
		FR_dir,
		pdb_input_dir = LMPNN_dir / 'backbones',
	)

	# Update previous directory for next cycle
	previous_dir = current_dir
