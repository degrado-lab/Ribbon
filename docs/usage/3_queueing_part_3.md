# Queueing Pt. 3: Mixed Submission

As seen in the previous tutorial, we can link together complex sets of jobs using the `depends_on` flag. In this way, we can submit many interdependent jobs ahead of time. (Code: [`/examples/example5`](https://github.com/degrado-lab/Ribbon/tree/main/examples/example5)) 

However, it's sometimes useful to run small snippets of python code between jobs, or to have programmatic checks to make sure everything's running smoothly (before we submit thousands of jobs that inevitably fail due to a typo). In these instances, we can use a _mixed submission_ strategy. Rather than submitting all of our `Tasks` to a scheduler at the start, we can queue a set of jobs, wait for them to finish, and check on or modify the results before submitting further jobs. 

In this example, we'll predict sequences using LigandMPNN, but before we fold them with RaptorX-Single, we'll apply mutations to those sequences using a simple python function.

We start by queueing our first job:
```python
import ribbon
lmpnn_task = ribbon.LigandMPNN(
    structure_list = ['my_structure.pdb'],
    output_dir = './out/lmpnn',
    num_designs = 5
)
lmpnn_job_id = lmpnn_task.queue(scheduler='SLURM')
```

Then we'll use ```ribbon.wait_for_jobs()```, to pause our script until our jobs have completed successfully:
```python
ribbon.wait_for_jobs([lmpnn_job_id], queue='SLURM')
```
This simple function periodically queries the scheduler, keeping track of the status of our jobs.

After all of our jobs have completed, we apply a small mutation to each using the following script:
```python
position = 10
mutation = 'A'

import os
os.mkdir('./out/lmpnn/seqs_split_mutated')
for f in os.listdir('./out/lmpnn/seqs_split'):
    with open(os.path.join('./out/lmpnn/seqs_split', f)) as infile, open(os.path.join('./out/lmpnn/seqs_split_mutated', f), 'w') as outfile:
        for line in infile:
                    outfile.write(line if line.startswith('>') else line[:position-1] + mutation + line[position:])

```
You'll likely want at more sophisticated method for mutagenesis - but for a tutorial, this will suffice!

Now, we can fold these mutated structures, as before:
```python
# Then, we create and queue a RaptorX Task:
raptorx_task = ribbon.RaptorXSingle(
        fasta_file_or_dir = './out/lmpnn/seqs_split',
        output_dir = './out/raptorx',
)
raptorx_task.queue(
            scheduler='SLURM',
            depends_on = [lmpnn_job_id]
)
```


All together, our final script looks like:
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

# Wait for it to finish:
ribbon.wait_for_jobs([lmpnn_job_id], scheduler='SLURM')


# For all of our output FASTAs, apply a mutation:
position = 10
mutation = 'A'

import os
os.mkdir('./out/lmpnn/seqs_split_mutated')
for f in os.listdir('./out/lmpnn/seqs_split'):
    with open(os.path.join('./out/lmpnn/seqs_split', f)) as infile, open(os.path.join('./out/lmpnn/seqs_split_mutated', f), 'w') as outfile:
        for line in infile:
                    outfile.write(line if line.startswith('>') else line[:position-1] + mutation + line[position:])


# Then, we create and queue a RaptorX Task:
raptorx_task = ribbon.RaptorXSingle(
        fasta_file_or_dir = './out/lmpnn/seqs_split',
        output_dir = './out/raptorx',
)
raptorx_task.queue(
            scheduler='SLURM'
)
```

If we execute this script manually, it will run until the final jobs are queued. However, if this script exits prematurely - for example, if your ssh connection closes, your final jobs may not be queued.

To overcome this limitation, we can submit this script as the _primary_ SLURM job, which queues the LigandMPNN and RaptorX-Single `Tasks` as _secondary_ jobs. After saving our script, we can create a minimal SLURM submission script called `submit.sh`:
```bash
#!/bin/bash
conda activate ribbon
python mixed_scheduling.py
```

And submit our _primary_ job with the SLURM command-line interface:
```qsub
sbatch submit.sh
```