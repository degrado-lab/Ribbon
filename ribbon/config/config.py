from pathlib import Path
import os

### Main Directory:
# where Task definitions, Containers, and cached Ribbon tasks are stored
# Can be customized by setting RIBBON_HOME environment variable
ribbon_dir = Path(os.environ.get('RIBBON_HOME', '~/.ribbon')).expanduser()

# Config file has the remaining paths. There are defaults if not found in the config.
CONFIG_FILE = ribbon_dir / "config.toml"

### Load config!
from ribbon.config.parse_config import load_config
config = load_config(CONFIG_FILE, ribbon_dir)

# Load paths from config
TASKS_VERSION = config["tasks_version"]
CONTAINER_DIR = Path(config.get("containers_path", ribbon_dir / "ribbon_containers"))
TASKS_DIR = Path(config.get("tasks_path", ribbon_dir / "ribbon_tasks"))
CACHE_DIR = Path(config.get("cache_path", ribbon_dir / "ribbon_cache"))
# The MODULE dir has the actual module
TASKS_MODULE_DIR = TASKS_DIR / TASKS_VERSION / "Ribbon-Tasks" / "ribbon_tasks"

### Github URL:
GITHUB_API_URL = "https://api.github.com/repos/Degrado-lab/Ribbon-Tasks/releases"

