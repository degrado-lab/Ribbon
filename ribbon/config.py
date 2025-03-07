from pathlib import Path
import os

### Main Directory:
# where Task definitions, Containers, and cached Ribbon tasks are stored
ribbon_dir = Path('~/.ribbon').expanduser()

### Ribbon Containers:
DOWNLOAD_DIR = ribbon_dir / "ribbon_containers"

### Ribbon Cached Tasks:
# Here's where we store serialized tasks, to be queued on a cluster
TASK_CACHE_DIR = ribbon_dir / "ribbon_cache"

### Ribbon Task Definitions:
# This section is more complicated. We want the user to be able to define or modify tasks,
# and for those changes to be received by whatever virtual machine their jobs run on in a cluster or scheduler.
# So, at init we will download the Ribbon-Tasks repo from GitHub, and add it to path at runtime. We import this as a module.
# When virtual machines are run, they will have access to the same module, and can import the same tasks.
# This way, the user can define tasks in their local environment, and have them run on a cluster without any extra steps.

# Github link:
GITHUB_ZIP_URL = "https://github.com/degrado-lab/Ribbon-Tasks/archive/refs/heads/main.zip"  # main branch

# The environment variable that points to the directory where the REPO will be downloaded.
RIBBON_TASKS_ENV_VAR = "RIBBON_TASKS_DIR"
# The environment variable that points to the directory where the MODULE is, which is $RIBBON_TASKS_DIR/[RIBBON_TASKS_REPO_NAME]/ribbon_tasks
RIBBON_TASKS_MODULE_ENV_VAR = "RIBBON_TASKS_MODULE_DIR"
# If not set, the REPO will be downloaded to the default directory.
DEFAULT_TASKS_DIR = ribbon_dir / "ribbon_tasks"
# When we download it, we'll rename the directory to this (otherwise, it'll have a branch suffix):
RIBBON_TASKS_REPO_NAME = "Ribbon-Tasks"

def get_data_directory():
    """Return the directory where data files should reside."""
    env_var = os.environ[RIBBON_TASKS_ENV_VAR]
    if env_var:
        return env_var
    else:
        return str(DEFAULT_TASKS_DIR)

# Setting the variables from above:
os.environ[RIBBON_TASKS_ENV_VAR] = get_data_directory()
os.environ[RIBBON_TASKS_MODULE_ENV_VAR] = str( Path(os.environ[RIBBON_TASKS_ENV_VAR]) / RIBBON_TASKS_REPO_NAME / 'ribbon_tasks' )

# TASKS_DIR is a copy of RIBBON_TASKS_MODULE_DIR, but as a Path object
TASKS_DIR = Path(os.environ[RIBBON_TASKS_MODULE_ENV_VAR])

