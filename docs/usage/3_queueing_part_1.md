# Queueing Pt. 1: Submitting Jobs

If we want to run hundreds or thousands of `Tasks`, it's impractical to run them one-by-one. We can use a _scheduler_ like SLURM or SGE to queue `Tasks` (called jobs, in this context). A high-performance compute cluster will use one of these tools to manage jobs. (Code: [`/examples/example3`](https://github.com/degrado-lab/Ribbon/tree/main/examples/example3)) 

In this tutorial, we will not cover how to use SGE or SLURM. We recommend becoming familiar with these tools on your compute cluster before continuing.

To start, let's make a new `Task` object to fold a protein with Chai-1:
```python
import ribbon
my_folding_task = ribbon.Chai1(
        fasta_file = 'my_sequence.fasta',   # Input FASTA
        output_dir = './out'                # Where the outputs will be stored
)
```

Before, we ran the task locally using ```my_folding_task.run()```.

To queue the job, we instead use the ```.queue()``` function:
```python
my_folding_task.queue(
		scheduler='SLURM',
	)
```
In this case, I've specified that the scheduler our cluster is using is SLURM.

Let's instead submit a job to an SGE cluster. We can also specify add a job name and a named output file. Additionally, let's make sure we're running on the GPU queue for our cluster, and ask only for nodes that have an A40 GPU. Finally, we'll have our job quit early if it runs longer than 30 minutes.
```python
my_folding_task.queue(
            scheduler='SGE', 
			queue='gpu.q',
			job_name='my_chai1_job',
            output_file='my_chai1_job.out', 
			node_name = 'qb3-atgpu*',
            time='00:30:00')
```


Putting it all together:
```python
import ribbon
my_task = ribbon.Chai1(
        fasta_file = 'my_sequence.fasta',   # Input FASTA
        output_dir = './out'                # Where the outputs will be stored
)

my_task.queue(scheduler='SGE',
              job_name='my_chai1_job',
              output_file='my_chai1_job.out', 
              time='00:30:00',
              queue='gpu.q')
```

!!! info "RTFM"
    These specific parameters (including queue and node names) will vary for your compute cluster. Make sure to read your cluster's documentation, and test using the SLURM or SGE command line interface.