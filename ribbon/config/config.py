from pathlib import Path
import os

### Github URL:
GITHUB_API_URL = "https://api.github.com/repos/Degrado-lab/Ribbon-Tasks/releases"
GITHUB_ZIP_PREFIX = "https://github.com/degrado-lab/Ribbon-Tasks/archive/refs/tags"

### Main Directory:
# where Task definitions, Containers, and cached Ribbon tasks are stored
# Can be customized by setting RIBBON_HOME environment variable
RIBBON_HOME = Path(os.environ.get('RIBBON_HOME', '~/.ribbon')).expanduser()

# Config file has the remaining paths. There are defaults if not found in the config.
CONFIG_FILE = RIBBON_HOME / "config.toml"

def reload_config_vars():
    """Reload configuration variables from config file."""
    from ribbon.config.parse_config import load_config
    config = load_config(CONFIG_FILE, RIBBON_HOME)

    # Load paths from config
    TASKS_VERSION = config["tasks_version"]
    CONTAINER_DIR = Path(config.get("containers_path", RIBBON_HOME / "ribbon_containers"))
    TASKS_DIR = Path(config.get("tasks_path", RIBBON_HOME / "ribbon_tasks"))
    CACHE_DIR = Path(config.get("cache_path", RIBBON_HOME / "ribbon_cache"))
    TASKS_MODULE_DIR = TASKS_DIR / TASKS_VERSION / "Ribbon-Tasks" / "ribbon_tasks"

    

    return {
        "TASKS_VERSION": TASKS_VERSION,
        "CONTAINER_DIR": CONTAINER_DIR,
        "TASKS_DIR": TASKS_DIR,
        "CACHE_DIR": CACHE_DIR,
        "TASKS_MODULE_DIR": TASKS_MODULE_DIR,
        # Let's put the other variables in here for too, for convenience
        "GITHUB_ZIP_PREFIX": GITHUB_ZIP_PREFIX,
        "GITHUB_API_URL": GITHUB_API_URL,
        "RIBBON_HOME": RIBBON_HOME,
        "CONFIG_FILE": CONFIG_FILE
    }

# Load the variables from config
vars_from_config = reload_config_vars()
TASKS_VERSION = vars_from_config["TASKS_VERSION"]
CONTAINER_DIR = vars_from_config["CONTAINER_DIR"]
TASKS_DIR = vars_from_config["TASKS_DIR"]
CACHE_DIR = vars_from_config["CACHE_DIR"]
TASKS_MODULE_DIR = vars_from_config["TASKS_MODULE_DIR"]
