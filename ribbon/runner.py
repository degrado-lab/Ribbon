import ribbon.utils as utils

def run_task(task_name, device='gpu', extra_args="", **kwargs ):
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
    required_inputs = utils.get_task_inputs(task_name)

    # Check that we have all the required inputs
    for input in required_inputs:
        if input not in kwargs:
            raise ValueError(f'Input {input} is required for task {task_name}')

    # Get Information about the task:
    task_dict = utils.get_task_dict(task_name)
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