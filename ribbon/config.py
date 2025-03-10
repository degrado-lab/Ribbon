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

# Github link for Tasks repo:
RELEASE_TAG = "v0.1.2"  # update this with your desired release tag
GITHUB_ZIP_URL = f"https://github.com/degrado-lab/Ribbon-Tasks/archive/refs/tags/{RELEASE_TAG}.zip"
# The version-tag is the release tag without the leading 'v':
if RELEASE_TAG[0] == 'v':
    VERSION_TAG = RELEASE_TAG[1:]
else:
    VERSION_TAG = RELEASE_TAG

# This is the default directory of the downloaded REPO.
DEFAULT_TASKS_DIR = ribbon_dir / "ribbon_tasks" / f"Ribbon-Tasks-{VERSION_TAG}"
# The environment variable that points to the directory of the REPO (by default, it's DEFAULT_TASKS_DIR)
RIBBON_TASKS_ENV_VAR = "RIBBON_TASKS_DIR"
# The environment variable that points to the MODULE (by default, it's DEFAULT_TASKS_DIR/ribbon_tasks)
RIBBON_TASKS_MODULE_ENV_VAR = "RIBBON_TASKS_MODULE_DIR"

def get_data_directory():
    """Return the directory where data files should reside."""
    data_dir = os.environ.get(RIBBON_TASKS_ENV_VAR, str(DEFAULT_TASKS_DIR))
    # double check - is it set to an empty string?
    if data_dir.strip() == "":
        data_dir = str(DEFAULT_TASKS_DIR)
    return data_dir

# Setting the variables from above:
os.environ[RIBBON_TASKS_ENV_VAR] = get_data_directory()
os.environ[RIBBON_TASKS_MODULE_ENV_VAR] = str( Path(os.environ[RIBBON_TASKS_ENV_VAR]) / 'ribbon_tasks' )

#TASKS_DIR is a copy of RIBBON_TASKS_DIR, but as a Path object
#TASKS_DIR = Path(os.environ[RIBBON_TASKS_ENV_VAR])
# The MODULE dir has the actual module
TASKS_MODULE_DIR = Path(os.environ[RIBBON_TASKS_MODULE_ENV_VAR])

