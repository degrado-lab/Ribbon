def generate_slurm_command(resources, other_resources, job_variables, scheduler_script):
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

def parse_slurm_resources(resources):
    resource_mappings = {
        'time': '--time',
        'mem': '--mem',
        'dependency': '--dependency',
        'gpus': '--gpus',
        'job-name': '--job-name',
        'requeue': '--requeue',
        'output': '--output',
        'queue': '--partition',
        # Add other resource mappings as needed
    }

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

def generate_sge_command(resources, other_resources, job_variables, scheduler_script):
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

def parse_sge_resources(resources):
    resource_mappings = {
        'time': '-l h_rt',
        'mem': '-l mem_free',
        'dependency': '-hold_jid',
        'gpus': '-l gpu',
        'job-name': '-N',
        'output': '-o',
        'queue': '-q',
        # Add other resource mappings as needed
    }

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