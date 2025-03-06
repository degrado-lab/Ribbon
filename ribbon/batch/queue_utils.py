import subprocess

#################################################################
#################### SLURM Scheduler Functions ##################
#################################################################

def generate_slurm_command(resources, other_resources, job_variables, scheduler_script):
    """
    Generate a SLURM command to submit a job to the scheduler.

    Args:
        resources (dict): A dictionary of resources to request for the job.
        other_resources (dict): A dictionary of other resources to pass to the scheduler.
        job_variables (str): A string of environment variables to pass to the job.
        scheduler_script (str): The path to the script to run.

    Returns:
        str: The SLURM command to submit
    """
    scheduler_command = 'sbatch'
    # Map resources to SLURM options
    resources_string = parse_slurm_resources(resources)
    # Add other resources as-is, from dict:
    for key, value in other_resources.items():
        if value == '': # If value is empty, assume it's a flag without a value
            resources_string += f" {key}"
        else:
            resources_string += f" {key}={value}"
    # Construct the command
    command = f"{scheduler_command} --export={job_variables} {resources_string} {scheduler_script}"
    return command

def parse_slurm_resources(resources, dependency_type='afterok'):
    """
    Parse a dictionary of resources into a string of SLURM options.

    Args:
        resources (dict): A dictionary of resources to request for the job.
        dependency_type (str): The type of dependency to use (e.g. 'afterok', 'afterany', 'afternotok')

    Returns:
        str: A string of SLURM options
    """
    resource_mappings = {
        'time': '--time',
        'mem': '--mem',
        'dependency': '--dependency',
        'gpus': '--gpus',
        'job-name': '--job-name',
        'requeue': '--requeue',
        'output': '--output',
        'queue': '--partition',
        'node-name': '--nodelist',
        # Add other resource mappings as needed
    }

    # Parse dependencies:
    if 'dependency' in resources:
        dependencies = resources['dependency']
        if isinstance(dependencies, list):
            dependencies = ':'.join([str(job_id) for job_id in dependencies])
        resources['dependency'] = dependency_type + ':'+ dependencies

    resources_list = []
    for key, value in resources.items():
        if key not in resource_mappings:
            print(f"Warning: Unrecognized resource key: {key}. Skipping.")
            continue
        slurm_option = resource_mappings.get(key, key)
        if value is True:
            # Flags without values
            resources_list.append(f"{slurm_option}")
        else:
            resources_list.append(f"{slurm_option}={value}")

    resources_string = ' '.join(resources_list)
    return resources_string

def parse_slurm_output(output):
    job_id = int(output.split()[-1])
    return job_id

#################################################################
########### SGE (Sun Grid Engine) Scheduler Functions ###########
#################################################################
def generate_sge_command(resources, other_resources, job_variables, scheduler_script):
    """
    Generate an SGE command to submit a job to the scheduler.

    Args:
        resources (dict): A dictionary of resources to request for the job.
        other_resources (dict): A dictionary of other resources to pass to the scheduler.
        job_variables (str): A string of environment variables to pass to the job.
        scheduler_script (str): The path to the script to run.

    Returns:
        str: The SGE command to submit
    """

    scheduler_command = 'qsub'
    # Map resources to SGE options
    resources_string = parse_sge_resources(resources)
    # Add other resources as-is, from dict:
    for key, value in other_resources.items():
        if value == '': # If value is empty, assume it's a flag without a value
            resources_string += f" {key}"
        else:
            if key.startswith('-l'):
                resources_string += f" {key}={value}"
            else:
                resources_string += f" {key} {value}"
    # Construct the command
    command = f"{scheduler_command} -v {job_variables} {resources_string} {scheduler_script}"
    return command

def parse_sge_resources(resources, dependency_type=None):
    """
    Parse a dictionary of resources into a string of SGE options.

    Args:
        resources (dict): A dictionary of resources to request for the job.

    Returns:
        str: A string of SGE options

    TODO: implement dependency handling
    """
    resource_mappings = {
        'time': '-l h_rt',
        'mem': '-l mem_free',
        'dependency': '-hold_jid',
        'gpus': '-l gpu',
        'job-name': '-N',
        'output': '-o',
        'queue': '-q',
        'node-name': '-l hostname',
        # Add other resource mappings as needed
    }

    # Parse dependencies:
    if 'dependency' in resources:
        dependencies = resources['dependency']
        if isinstance(dependencies, list):
            dependencies = ','.join([str(job_id) for job_id in dependencies])
        resources['dependency'] = dependencies

    resources_list = []
    for key, value in resources.items():
        if key == 'dependency':
            # Handle dependencies specifically
            resources_list.append(f"-hold_jid {value}")
        else:
            if key not in resource_mappings:
                print(f"Warning: Unrecognized resource key: {key}. Skipping.")
                continue
            sge_option = resource_mappings.get(key)
            if sge_option:
                if sge_option.startswith('-l'):
                    resources_list.append(f"{sge_option}={value}")
                else:
                    resources_list.append(f"{sge_option} {value}")
            else:
                # For unrecognized keys, assume they are '-l key=value'
                resources_list.append(f"-l {key}={value}")

    resources_string = ' '.join(resources_list)
    return resources_string

def parse_sge_output(output):
    job_id = int(output.strip().split()[2])
    return job_id

def sge_check_job_status(job_ids):
    """
    Check if SGE jobs are still running or have completed.

    Parameters:
        job_ids (list): A list of job IDs (as integers or strings)

    Returns:
        dict: A dictionary with job IDs as keys and statuses as values ('running' or 'completed')
    """
    status_dict = {}
    for jobid in job_ids:
        try:
            # Run 'qstat -j <jobid>' and suppress output
            result = subprocess.run(
                ['qstat', '-j', str(jobid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if result.returncode == 0:
                status = 'not completed'
            else:
                status = 'completed'
            status_dict[jobid] = status
        except Exception as e:
            status_dict[jobid] = f'Error: {e}'
    return status_dict

def slurm_check_job_status(job_ids):
    """
    Check if SLURM jobs are still running or have completed.

    Parameters:
        job_ids (list): A list of job IDs (as integers or strings)

    Returns:
        dict: A dictionary with job IDs as keys and statuses as values ('running' or 'completed')
    """
    status_dict = {}
    for jobid in job_ids:
        try:
            # Run 'squeue -j <jobid> --noheader' and capture the output.
            result = subprocess.run(
                ['squeue', '-j', str(jobid), '--noheader'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )
            # If any output is returned, the job is still in the queue (running or pending)
            if result.stdout.strip():
                status = 'not completed'
            else:
                status = 'completed'
            status_dict[jobid] = status
        except Exception as e:
            status_dict[jobid] = f'Error: {e}'
    return status_dict