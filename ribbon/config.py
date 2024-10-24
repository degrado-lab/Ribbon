from pathlib import Path

# Path to the directory where the ribbon containers are stored
DOWNLOAD_DIR = Path('~/ribbon_containers').expanduser()

# Path to the directory where the ribbon module is stored
MODULE_DIR = Path(__file__).resolve().parent