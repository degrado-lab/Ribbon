from ribbon import deserialize
from ribbon.config import TASK_CACHE_DIR
import argparse
import os
import sys

if __name__ == '__main__':
    """
    This script is used to deserialize and run a task from the command line.
    
    Args:
        task_name (str): The name of the task to run.
        cache_dir (str): The directory to store the task cache.

    Returns:
        None

    Example:
        python ribbon/deserialize_and_run.py MyTask --cache_dir /path/to/cache
    """
    # Parse the arguments
    parser = argparse.ArgumentParser(description='Deserialize and run a task.')

    parser.add_argument('task_name', type=str, help='The name of the task to run.')
    parser.add_argument('--cache_dir', type=str, default=TASK_CACHE_DIR, help='The directory to store the task cache.')

    args = parser.parse_args()

    # Check if RIBBON_TASKS_DIR is set, and add it to sys.path if so.
    # This is necessary because of how pickles handle paths and module references.
    ribbon_tasks_dir = os.getenv("RIBBON_TASKS_DIR")
    if ribbon_tasks_dir:
        sys.path.insert(0, ribbon_tasks_dir)
    
    # Deserialize the task:
    task = deserialize(args.task_name, cache_dir=args.cache_dir)

    # Run the task:
    task.run()