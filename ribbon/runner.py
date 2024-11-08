import ribbon.utils as utils
import ribbon.batch.queue_utils as queue_utils
from pathlib import Path
from ribbon.config import TASKS_DIR, MODULE_DIR
import json
import os

class Task:
    def __init__(self, device='gpu', extra_args=""):
        self.device = device
        self.extra_args = extra_args

    def run(self):
        raise NotImplementedError(f"You are attempting to run a task { self.__class__.__name__ } without defining a run method.")
    
    def queue(self, scheduler, depends_on=[], dependency_type='afterok', job_name=None, output_file=None, n_tasks=1, time='1:00:00', mem='2G', gpus=None, auto_restart=True, other_resources={}):
        ''' Queue the LigandMPNN task using the given scheduler.
        Inputs:
            scheduler: str - the name of the scheduler to use. Options are 'SLURM' or 'SGE'.
            depends_on: list - a jobID or list of jobIDs that this job depends on. (Each is an Int)
            dependency_type: str - the type of dependency. Options are 'afterok', 'afternotok', 'afterany', 'after', 'singleton'. Default is 'afterok'.
            job_name: str - the name of the job. Default is None.
            n_tasks: int - the number of tasks to run. Default is 1.
            time: str - the time to allocate for the task. Default is '1:00:00'.
            mem: str - the memory to allocate for the task. Default is '2G'.
            gpus: int - the number of GPUs to allocate for the task. Default is None.
            other_resources: dict - other resources to allocate for the task. Has the form {"--option": "value"}. Default is empty dict.
        Outputs:
            job_id: str - the ID of the job in the scheduler.
        '''
        # Serialize the task object to a pickle file:
        serialized_task = utils.serialize(self)

        # Retrieve the Ribbon container:
        container_name = 'Ribbon'
        container_path = utils.verify_container(container_name)

        # Correct the scheduler script mapping:
        batch_script_dir = Path(MODULE_DIR) / 'batch' / 'batch_scripts'
        scheduler_script = {'SLURM': str(batch_script_dir / 'slurm_submit.sh'), 
                            'SGE':   str(batch_script_dir / 'sge_submit.sh')}[scheduler]
        deserialize_script = Path(MODULE_DIR) / 'deserialize_and_run.py'
        
        # Prepare job variables:
        job_variables = f"ribbon_container={container_path}," \
                        f"ribbon_deserialize_script={deserialize_script}," \
                        f"serialized_job={serialized_task}," \
                        f"RIBBON_TASKS_DIR={os.getenv('RIBBON_TASKS_DIR')}"

        # Prepare the resources:
        resources = {'time': time, 'mem': mem}

        if depends_on:
            depends_on_str = ':'.join([str(job_id) for job_id in depends_on])
            resources['dependency'] = f'{dependency_type}:{depends_on_str}'

        if gpus:
            resources['gpus'] = gpus

        if job_name:
            resources['job-name'] = job_name

        if auto_restart:
            resources['requeue'] = True  # Use True to indicate a flag without a value

        if output_file:
            resources['output'] = output_file

        # Add other resources:
        resources.update(other_resources)

        # Generate the command using queue_utils
        if scheduler == 'SLURM':
            command = queue_utils.generate_slurm_command(resources, job_variables, scheduler_script)
        elif scheduler == 'SGE':
            command = queue_utils.generate_sge_command(resources, job_variables, scheduler_script)
        else:
            raise ValueError(f"Unsupported scheduler: {scheduler}")

        # Run the task:
        stdout, stderr = utils.run_command(command, capture_output=True)

        # Parse the job ID from the output:
        if scheduler == 'SLURM':
            job_id = queue_utils.parse_slurm_output(stdout)
        elif scheduler == 'SGE':
            job_id = queue_utils.parse_sge_output(stdout)
        else:
            raise ValueError(f"Unsupported scheduler: {scheduler}")

        return job_id
    
    def _run_task(self, task_name, scheduler='local', device='gpu', extra_args="", **kwargs ):
        ''' Run a task with the given name and arguments.
        Inputs:
            task_name: str - the name of the task to run
            device: str - Enables Apptainer to use GPU. Options are 'gpu', 'gpu_wsl' (if using WSL), or 'cpu'. Default is 'gpu'.
            extra_args: str - additional arguments to pass to the task, which is optional. E.g. '--save_frequency 10 --num_steps 1000'
            kwargs: dict - the arguments to pass to the task. These are task-specific.
        Outputs:
            None
        '''
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
        print('--------------------------------------------')
        print('- Task name:', task_name)
        print('- Task description:', task_dict['description'])

        # Verify we have the container associated with the software we want to run. 
        # If not, attempt to download it to the download_dir
        container_path = utils.verify_container(container_name)

        # Add inputs to the command, by replacing the placeholders in the command string:
        command = task_dict['command']
        for input in required_inputs:
            command = command.replace(f'{{{input}}}', str(kwargs[input]))
        
        print('- Command:', command)

        # Set nvidia flag:
        nvidia_flag = {'gpu': '--nv', 'gpu_wsl': '--nvccli', 'cpu': ''}[device]
        
        # Run the task
        apptainer_command = f'apptainer run {nvidia_flag} {container_path} {command}'
        utils.run_command(apptainer_command)
        print('--------------------------------------------')
    
    def _get_task_dict(self, task_name):
        '''Returns the dictionary for a given task'''
        # Which inputs does our task require?
        with open(TASKS_DIR / 'tasks.json') as f:
            tasks = json.load(f)

        return tasks[task_name]

    def _get_task_inputs(self, task_name):
        '''Returns the inputs required for a given task'''
        #Get the command:
        command = self._get_task_dict(task_name)['command']

        #Inputs are surrounded by curly braces. Here we extract them.
        inputs = [i[1:-1] for i in command.split() if i.startswith('{') and i.endswith('}')]

        #Remove duplicates:
        inputs = list(set(inputs))
        
        return inputs
    
    def __repr__(self):
        return f"{self.__class__.__name__} \
            {self.__dict__}"