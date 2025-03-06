# Import some utility functions to top level
from .utils import clean_cache, serialize, deserialize, wait_for_jobs

# Import ribbon_tasks, if necessary:
import os
import sys
import importlib.util

# Check for the environment variable
custom_tasks_path = os.environ.get('RIBBON_TASKS_DIR')

if custom_tasks_path:
    # Validate that the specified path exists
    if not os.path.isdir(custom_tasks_path):
        raise FileNotFoundError(f"The directory '{custom_tasks_path}' does not exist.")
    
    # To import, we need to go up one level:
    #print(custom_tasks_path)
    #custom_tasks_path = os.path.dirname(custom_tasks_path)

    # Construct the path to the ribbon_tasks package
    ribbon_tasks_path = custom_tasks_path

    print(f"Importing custom 'ribbon_tasks' package from '{ribbon_tasks_path}'")

    if not os.path.isdir(ribbon_tasks_path):
        raise FileNotFoundError(f"'ribbon_tasks' package not found in '{custom_tasks_path}'.")

    # Add the custom_tasks_path to sys.path temporarily
    sys.path.insert(0, custom_tasks_path)

    try:
        # Import the custom ribbon_tasks package
        import ribbon_tasks
        from ribbon_tasks import *
    except ImportError as e:
        raise ImportError(f"Failed to import custom 'ribbon_tasks' package: {e}")
    finally:
        # Remove the custom_tasks_path from sys.path to avoid side effects
        sys.path.pop(0)
else:
    # Import the default ribbon_tasks package
    print("Importing default 'ribbon_tasks' package")
    from .ribbon_tasks.ribbon_tasks import *