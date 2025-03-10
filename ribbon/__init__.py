# Import some utility functions to top level
from .utils import clean_cache, serialize, deserialize, wait_for_jobs
from .config import RIBBON_TASKS_ENV_VAR, GITHUB_ZIP_URL, TASKS_MODULE_DIR
from pathlib import Path
import os
import sys

def data_already_downloaded(data_dir, repo_name):
    """
    Check if data appears to be downloaded.
    For example, by checking for a marker file that should be present.
    """
    marker_file = os.path.join(data_dir, repo_name, "README.md")  # adjust this to a file that should exist
    return os.path.exists(marker_file)

def download_and_extract_data(data_dir, repo_name):
    """Download the repo ZIP from GitHub and extract it into data_dir with a custom name."""
    print(f"Downloading Ribbon Task files from GitHub to {data_dir}...")
    import urllib.request
    import zipfile
    import io
    import shutil
    
    try:
        with urllib.request.urlopen(GITHUB_ZIP_URL) as response:
            zip_data = response.read()
    except Exception as e:
        raise RuntimeError("Failed to download data: " + str(e))
    
    try:
        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            z.extractall(data_dir)
    except Exception as e:
        raise RuntimeError("Failed to extract data: " + str(e))
    
    final_dir = os.path.join(data_dir, repo_name)
    
    print("Ribbon Task files downloaded and extracted to:", final_dir)

### Ensure that the required data files are available.
# The environment variable will be set automatically by config.py if it's not already set by the user.
custom_tasks_path = Path(os.environ.get(RIBBON_TASKS_ENV_VAR))

if not os.path.exists(custom_tasks_path):
    os.makedirs(custom_tasks_path.parent, exist_ok=True)

if not data_already_downloaded(custom_tasks_path.parent, custom_tasks_path.name):
    download_and_extract_data(custom_tasks_path.parent, custom_tasks_path.name)
else:
    print("Data files already present in:", custom_tasks_path)

# Run import
# Add the custom_tasks_path to sys.path temporarily
print(f"Importing custom 'ribbon_tasks' package from '{TASKS_MODULE_DIR}'")
parent_dir = os.path.dirname(TASKS_MODULE_DIR)
sys.path.insert(0, parent_dir)

try:
    # Import the custom ribbon_tasks package
    import ribbon_tasks
    from ribbon_tasks import *
except ImportError as e:
    raise ImportError(f"Failed to import custom 'ribbon_tasks' package: {e}")
finally:
    # Remove the custom_tasks_path from sys.path to avoid side effects
    sys.path.pop(0)
