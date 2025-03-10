import ribbon.utils as utils
import ribbon.batch.queue_utils as queue_utils
from pathlib import Path
from ribbon.config import TASKS_MODULE_DIR
import json
import os
import re

class Task:
    def __init__(self, device='cpu', extra_args=""):
        """
        The Task class is the parent class for all tasks in the Ribbon framework.
        It contains the basic functionality for running tasks, queuing tasks, and managing task dependencies.
        
        Args:
            device (str): Enables Apptainer to use GPU. Options are 'gpu', 'gpu_wsl' (if using WSL), or 'cpu'. Default is 'gpu'.
            extra_args (str, optional): Additional arguments to pass to the task

        Returns:
            None
        """
        self.device = device
        self.extra_args = extra_args
        self.task_name = None

    def run(self):
        """
        Run the task. This method should be overridden by the child class.
        """
        raise NotImplementedError(f"You are attempting to run a task { self.__class__.__name__ } without defining a run method.")
    
    def queue(self, scheduler, depends_on=[], dependency_type='afterok', n_tasks=1, time='1:00:00', mem='2G', auto_restart=True, other_resources={}, job_name=None, output_file=None, queue=None,  gpus=None, node_name=None):
        """
        Queue the LigandMPNN task using the given scheduler.

        Args:
            scheduler (str): The name of the scheduler to use. Options are 'SLURM' or 'SGE'.
            depends_on (list, optional): A jobID or list of jobIDs that this job depends on. (Each is an int or str). Defaults to [].
            dependency_type (str, optional): The type of dependency. Options are 'afterok', 'afternotok', 'afterany', 'after', 'singleton'. Defaults to 'afterok'.
            n_tasks (int, optional): The number of tasks to run. Defaults to 1.
            time (str, optional): The time to allocate for the task. Defaults to '1:00:00'.
            mem (str, optional): The memory to allocate for the task. Defaults to '2G'.
            auto_restart (bool, optional): Whether to automatically restart the task if it fails. Defaults to True.
            other_resources (dict, optional): Other resources to allocate for the task. Has the form {"--option": "value"}. Defaults to {}.
            job_name (str, optional): The name of the job. Defaults to None.
            output_file (str, optional): The file to write the output to. Defaults to None.
            queue (str, optional): The queue to submit the task to. Defaults to None.
            gpus (int, optional): The number of GPUs to allocate for the task. Defaults to None.
            node_name (str, optional): The name of the node to run the task on. Defaults to None.
            
        Returns:
            str: The ID of the job in the scheduler.
        """
        # Serialize the task object to a pickle file:
        serialized_task = utils.serialize(self)

        # Retrieve the Ribbon container:
        ribbon_container_name = 'Ribbon'
        container_path = utils.verify_container(ribbon_container_name)

        # Retrieve the job's container:
        task_dict = self._get_task_dict(self.task_name)
        job_container_name = task_dict['container']
        utils.verify_container(job_container_name)

        # Correct the scheduler script mapping:
        MODULE_DIR = Path(__file__).resolve().parent
        batch_script_dir = Path(MODULE_DIR) / 'batch' / 'batch_scripts'
        scheduler_script = {'SLURM': str(batch_script_dir / 'slurm_submit.sh'), 
                            'SGE':   str(batch_script_dir / 'sge_submit.sh')}[scheduler]
        deserialize_script = Path(MODULE_DIR) / 'deserialize_and_run.py'
        
        # Prepare job variables:
        job_variables = f"ribbon_container={container_path}," \
                        f"ribbon_deserialize_script={deserialize_script}," \
                        f"serialized_job={serialized_task}," \
                        f"RIBBON_TASKS_DIR={os.getenv('RIBBON_TASKS_DIR')}," \
                        f"DEVICE={self.device}"
        

        ###################################### 
        # Prepare the resources:
        # TODO: this is messy, we should clean this up later
        resources = {'time': time, 'mem': mem}

        if depends_on:
            resources['dependency'] = depends_on

        if gpus:
            resources['gpus'] = gpus

        if job_name:
            resources['job-name'] = job_name

        if auto_restart:
            resources['requeue'] = True  # Use True to indicate a flag without a value

        if output_file:
            resources['output'] = output_file
        
        if queue:
            resources['queue'] = queue

        if node_name:
            resources['node-name'] = node_name

        # Note: We don't parse other_resouces in the same way - we just pass them through as-is,
        # assuming the user has formatted them correctly.
        #########################################################

        # Generate the command using queue_utils
        if scheduler == 'SLURM':
            command = queue_utils.generate_slurm_command(resources, other_resources, job_variables, scheduler_script)
        elif scheduler == 'SGE':
            command = queue_utils.generate_sge_command(resources, other_resources, job_variables, scheduler_script)
        else:
            raise ValueError(f"Unsupported scheduler: {scheduler}")

        # Run the task:
        stdout, stderr = utils.run_command(command, capture_output=True)

        print(stdout, stderr)

        # Parse the job ID from the output:
        if scheduler == 'SLURM':
            job_id = queue_utils.parse_slurm_output(stdout)
        elif scheduler == 'SGE':
            job_id = queue_utils.parse_sge_output(stdout)
        else:
            raise ValueError(f"Unsupported scheduler: {scheduler}")

        return job_id
    
    def _run_task(self, task_name, scheduler='local', device='gpu', extra_args="", container_override=None, **kwargs ):
        """
        Run a task with the given name and arguments.
        In the child Task class, this method should be called from within the user-facing run() method.

        Args:
            task_name (str): The name of the task to run.
            device (str): Enables Apptainer to use GPU. Options are 'gpu', 'gpu_wsl' (if using WSL), or 'cpu'. Default is 'gpu'.
            extra_args (str, optional): Additional arguments to pass to the task, e.g. '--save_frequency 10 --num_steps 1000'.
            container_override (str, optional): The name of the container to use for the task. If not provided, the default container for that Task will be used.
            kwargs (dict): Task-specific keyword arguments.

        Returns:
            None
        """
        # Add extra_args to kwargs:
        kwargs['extra_args'] = extra_args

        # Which inputs does our task require?
        required_inputs = self._get_task_inputs(task_name)

        # Check that we have all the required inputs
        for input in required_inputs:
            if input not in kwargs:
                raise ValueError(f'Input {input} is required for task {task_name}')

        # Get Information about the task:
        task_dict = self._get_task_dict(task_name)
        task_name = task_dict['name']
        container_name = task_dict['container']
        
        # Allow user to override the default container (used for the Custom task):
        if container_override is not None:
            container_name = container_override
        print('--------------------------------------------')
        print('- Task name:', task_name)
        print('- Task description:', task_dict['description'])

        # Verify we have the container associated with the software we want to run. 
        # If not, attempt to download it to the download_dir
        container_path = utils.verify_container(container_name)
        
        # Add inputs to the command, by replacing the placeholders in the command string:
        command = task_dict['command']
        for input in required_inputs:
            command = command.replace(f'{{{input}}}', str(kwargs[input])) #We need three sets of braces. Two sets are needed to escape them, and the third set is the actual placeholder.
        
        print('- Command:', command)

        # Set nvidia flag:
        nvidia_flag = {'gpu': '--nv', 'gpu_wsl': '--nvccli', 'cpu': ''}[device]

        # Set user-provided environment variables:
        env_variables_string = ''
        if 'environment_variables' in task_dict:
            if len(task_dict['environment_variables']) > 0:
                env_variables_string = '--env '
                # Join each key-value pair with a comma:
                env_variables_string += ','.join([f'{key}={value}' for key, value in task_dict['environment_variables'].items()])
        
        # Run the task
        apptainer_command = f'apptainer run {nvidia_flag} {env_variables_string} {container_path} {command}'
        utils.run_command(apptainer_command)
        print('--------------------------------------------')
    
    def _get_task_dict(self, task_name):
        """
        Returns the dictionary for a given task.
        """
        # Which inputs does our task require?
        with open(TASKS_MODULE_DIR / 'tasks.json') as f:
            tasks = json.load(f)

        return tasks[task_name]

    def _get_task_inputs(self, task_name):
        """Returns the inputs required for a given task"""
        # Get the command:
        command = self._get_task_dict(task_name)['command']

        # Use regex to find all occurrences of text inside curly braces.
        # The pattern '\{([^{}]+)\}' matches a '{', then captures any characters except '{' or '}', then a '}'.
        inputs = re.findall(r'\{([^{}]+)\}', command)

        # Remove duplicates:
        inputs = list(set(inputs))
        
        return inputs
    
    def __repr__(self):
        """
        Returns a string representation of the Task object.
        """
        return f"{self.__class__.__name__} \
            {self.__dict__}"