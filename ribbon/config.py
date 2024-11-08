from pathlib import Path
import os

# Path to the directory where the ribbon containers are stored
DOWNLOAD_DIR = Path('~/ribbon_containers').expanduser()

# Path to the directory where the ribbon module is stored
MODULE_DIR = Path(__file__).resolve().parent
os.environ['RIBBON_MODULE_DIR'] = str(MODULE_DIR) # Set the environment variable, so the apptainer can access it.

# Path to the directory where the ribbon tasks are stored
TASKS_DIR = MODULE_DIR / 'ribbon_tasks'
# if not already set:
if 'RIBBON_TASKS_DIR' not in os.environ or not os.environ['RIBBON_TASKS_DIR']:
    os.environ['RIBBON_TASKS_DIR'] = str(TASKS_DIR) # Set the environment variable, so the apptainer can access it.
TASKS_DIR = Path(os.environ['RIBBON_TASKS_DIR']) / 'ribbon_tasks'

# Here's where we store serialized tasks, to be queued on a cluster
TASK_CACHE_DIR = Path('~/.ribbon_cache').expanduser()
