# Import some utility functions to top level
from ribbon.utils import clean_cache, serialize, deserialize, wait_for_jobs
from pathlib import Path
import os
import sys

def data_already_downloaded(repo_dir):
    """
    Check if data appears to be downloaded.
    For example, by checking for a marker file that should be present.
    """
    marker_file = os.path.join(repo_dir.parent, "README.md")  # adjust this to a file that should exist
    return os.path.exists(marker_file)

def download_and_extract_data(data_dir, repo_name, github_zip_url):
    """Download the repo ZIP from GitHub and extract it into data_dir with a custom name."""
    print(f"Downloading Ribbon Task files from GitHub to {data_dir}...")
    import urllib.request
    import zipfile
    import io
    import shutil
    
    # Get existing items before extraction
    existing_items = set(os.listdir(data_dir)) if os.path.exists(data_dir) else set()
    
    try:
        with urllib.request.urlopen(github_zip_url) as response:
            zip_data = response.read()
    except Exception as e:
        raise RuntimeError("Failed to download data: " + str(e))
    
    try:
        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            z.extractall(data_dir)
    except Exception as e:
        raise RuntimeError("Failed to extract data: " + str(e))
    
    # Find the newly extracted directory
    current_items = set(os.listdir(data_dir))
    new_items = current_items - existing_items
    new_dirs = [item for item in new_items if os.path.isdir(os.path.join(data_dir, item))]
    
    if len(new_dirs) == 1:
        original_dir = os.path.join(data_dir, new_dirs[0])
        target_dir = os.path.join(data_dir, repo_name)
        if original_dir != target_dir:
            shutil.move(original_dir, target_dir)
            #print(f"Renamed extracted directory to: {repo_name}")
    elif len(new_dirs) > 1:
        print(f"Warning: Multiple new directories found after extraction: {new_dirs}")
    else:
        print("Warning: No new directory found after extraction")

def initialize():
    """Initialize Ribbon by loading config, downloading tasks if needed, and importing ribbon_tasks."""
    # Reload config variables
    from ribbon.config.config import reload_config_vars
    config_vars = reload_config_vars()
    
    CONTAINER_DIR = config_vars["CONTAINER_DIR"]
    CACHE_DIR = config_vars["CACHE_DIR"] 
    TASKS_DIR = config_vars["TASKS_DIR"]
    TASKS_MODULE_DIR = config_vars["TASKS_MODULE_DIR"]
    TASKS_VERSION = config_vars["TASKS_VERSION"]
    GITHUB_ZIP_PREFIX = config_vars["GITHUB_ZIP_PREFIX"]
    GITHUB_API_URL = config_vars["GITHUB_API_URL"]

    # Can this go elsewhere?
    GITHUB_ZIP_URL = f"{GITHUB_ZIP_PREFIX}/{TASKS_VERSION}.zip"

    # Update module-level variables
    globals().update(config_vars)
    
    ### Ensure that the required data files are available.
    if not os.path.exists(TASKS_DIR):
        os.makedirs(TASKS_DIR, exist_ok=True)

    if not data_already_downloaded(TASKS_MODULE_DIR):
        # Download task files using the configured version
        download_and_extract_data(TASKS_DIR / TASKS_VERSION, TASKS_MODULE_DIR.parent.name, GITHUB_ZIP_URL)
    else:
        #print("Data files already present in:", TASKS_MODULE_DIR)
        pass

    # Import ribbon_tasks
    parent_dir = os.path.dirname(TASKS_MODULE_DIR)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    try:
        # Remove existing ribbon_tasks from sys.modules to force reimport
        modules_to_remove = [mod for mod in sys.modules.keys() if mod.startswith('ribbon_tasks')]
        for mod in modules_to_remove:
            del sys.modules[mod]
            
        # Import the custom ribbon_tasks package
        import ribbon_tasks
        #from ribbon_tasks import *
        
        # Add to globals so they're available at module level
        globals()['ribbon_tasks'] = ribbon_tasks
        
    except ImportError as e:
        raise ImportError(f"Failed to import custom 'ribbon_tasks' package: {e}")

# Initialize on first import
initialize()
