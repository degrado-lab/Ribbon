# Queueing Pt. 2: Linking Jobs

Often, we'll want to run `Tasks` one after the other, where each depends on the previous. Like in (Let's get Pipelining), this allows us to form complex protein design pipelines. In this example, we'll schedule a job to generate protein sequences using LigandMPNN, and schedule a subsequent job to fold the sequences using RaptorX-Single. (Code: [`/examples/example4`](https://github.com/degrado-lab/Ribbon/tree/main/examples/example4)) 

We'll start as before, defining a LigandMPNN `Task`:
```python
import ribbon

# First, we create 5 new sequences for this structure:
lmpnn_task = ribbon.LigandMPNN(
    structure_list = ['my_structure.pdb'],
    output_dir = './out/lmpnn',
    num_designs = 5
)
```
Then, we'll queue this task. The `queue()` function returns the __job id__, which is a unique identifier for the job we've submitted to the scheduler.
```python
lmpnn_job_id = lmpnn_task.queue(scheduler='SGE')
```

We create and submit a RaptorX-Single `Task`, using the `depends_on` parameter to pass in a _list_ of job IDs.
```python
raptorx_task = ribbon.RaptorXSingle(
        fasta_file_or_dir = './out/lmpnn',
        output_dir = './out/raptorx',
)

raptorx_task.queue(
            scheduler='SGE'
            depends_on = [lmpnn_job_id]
)
```

!!! info "Dependency Types"
    By default, the job will only run after _all dependencies complete successfully_. If using SLURM, more complex behavior can be set using the `dependency_type` parameter, which takes standard SLURM dependency types (default: `afterok`).

Here's our script completed:

```python
import ribbon

# First, we create 5 new sequences for this structure:
lmpnn_task = ribbon.LigandMPNN(
    structure_list = ['my_structure.pdb'],
    output_dir = './out/lmpnn',
    num_designs = 5
)

# We'll queue the job, and get the job ID
lmpnn_job_id = lmpnn_task.queue(scheduler='SLURM')

# Then, we create and queue a RaptorX Task:
raptorx_task = ribbon.RaptorXSingle(
        fasta_file_or_dir = './out/lmpnn',
        output_dir = './out/raptorx',
)
raptorx_task.queue(
            scheduler='SLURM',
            depends_on = [lmpnn_job_id]
)
```