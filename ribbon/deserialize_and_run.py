from ribbon import deserialize
from ribbon.config import TASK_CACHE_DIR
import argparse

if __name__ == '__main__':
    # Parse the arguments
    parser = argparse.ArgumentParser(description='Deserialize and run a task.')

    parser.add_argument('task_name', type=str, help='The name of the task to run.')
    parser.add_argument('--cache_dir', type=str, default=TASK_CACHE_DIR, help='The directory to store the task cache.')

    args = parser.parse_args()

    # Deserialize the task:
    task = deserialize(args.task_name, cache_dir=args.cache_dir)

    # Run the task:
    task.run()