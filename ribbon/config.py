from pathlib import Path
import os

# Path to the directory where the ribbon containers are stored
DOWNLOAD_DIR = Path('~/ribbon_containers').expanduser()

# Path to the directory where the ribbon module is stored
MODULE_DIR = Path(__file__).resolve().parent
os.environ['RIBBON_MODULE_DIR'] = str(MODULE_DIR) # Set the environment variable, so the apptainer can access it.
