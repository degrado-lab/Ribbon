# Import some utility functions to top level
from .utils import clean_cache, serialize, deserialize, wait_for_jobs
from .config import RIBBON_TASKS_ENV_VAR, RIBBON_TASKS_REPO_NAME, GITHUB_ZIP_URL, TASKS_DIR
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
    
    temp_extract_dir = os.path.join(data_dir, "temp_extract")
    try:
        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            z.extractall(temp_extract_dir)
    except Exception as e:
        raise RuntimeError("Failed to extract data: " + str(e))
    
    # Rename the extracted directory to the desired repo_name
    extracted_dir = os.path.join(temp_extract_dir, "Ribbon-Tasks-main")
    final_dir = os.path.join(data_dir, repo_name)
    if os.path.exists(final_dir):
        shutil.rmtree(final_dir)
    shutil.move(extracted_dir, final_dir)
    shutil.rmtree(temp_extract_dir)
    
    print("Ribbon Task files downloaded and extracted to:", final_dir)

### Ensure that the required data files are available.
# The environment variable will be set automatically by config.py if it's not already set by the user.
custom_tasks_path = os.environ.get(RIBBON_TASKS_ENV_VAR)

if not os.path.exists(custom_tasks_path):
    os.makedirs(custom_tasks_path, exist_ok=True)

if not data_already_downloaded(custom_tasks_path, RIBBON_TASKS_REPO_NAME):
    download_and_extract_data(custom_tasks_path, RIBBON_TASKS_REPO_NAME) #we name it Ribbon-Tasks
else:
    print("Data files already present in:", custom_tasks_path)

# Run import
# Add the custom_tasks_path to sys.path temporarily
from .config import TASKS_DIR
print(f"Importing custom 'ribbon_tasks' package from '{TASKS_DIR}'")
parent_dir = os.path.dirname(TASKS_DIR)
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
