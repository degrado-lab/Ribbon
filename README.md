# Ribbon

> [!WARNING]
> 🚧 This Page is Under Construction! 🚧

Ribbon is a python package which simplifies the usage and pipelining of biological software. Installing and running state-of-the-art tools can be done with a simple python script.

## Quick Start
__Under Construction__

## Installation
Apptainer is the only requirement to run Ribbon. Install apptainer for your system [here](https://apptainer.org/docs/admin/main/installation.html#install-ubuntu-packages).
Then, install Ribbon in a clean python environment:
```
pip install ribbon-toolkit
```

## Running Tasks with Ribbon
Each type of job we want to run (e.g. structure prediction with Chai-1) is a _Task_ in Ribbon. To create and run a task, we use a script like the following:
```
import ribbon

ribbon.Chai1(
        fasta_file = 'my_sequence.fasta',
        output_prefix = 'chai_output', # Our output will be named this, + '_pred_X.cif'
    ).run()
```

The first time a job is run, Ribbon will automatically download the pre-packaged software to the `~/ribbon_containers` directory.

Currently, there are Ribbon Tasks defined for Chai-1, LigandMPNN, Rosetta Relax, as well as distance and SASA calculations with BioPython. Users can [define new tasks](## Advanced: Make your own Tasks) to expand their library.

## Queueing Tasks to a Cluster
Ribbon can optionally queue tasks to a compute cluster using SLURM or SGE. 
As before, we define a simple task. Then, instead of running it with `run()`, we `queue()` the task:
```
import ribbon

ribbon.Chai1(
        fasta_file = 'my_sequence.fasta',
        output_prefix = 'chai_output', # Our output will be named this, + '_pred_X.cif'
    ).queue(scheduler='SLURM')
```

Queuing a Task returns the scheduler ID for the job. This allows us to chain several jobs together:
```
import ribbon

job_id = ribbon.LigandMPNN(
        output_dir = './ligandmpnn_output/',
        structure_list = ['my_structure.cif'],
    ).queue(
        scheduler='SLURM')


ribbon.Chai1(
        fasta_file = './ligandmpnn_output/seqs_split/my_structure.cif_0.fasta',
        output_prefix = 'chai_output', # Our output will be named this, + '_pred_X.cif'
    ).queue(
        scheduler='SLURM',
        depends_on = str(job_id))
```

In this way, complex design and evaluation workflows can be built.


## Advanced: Make your own Tasks
__Under Construction__

## License

This project is licensed under the [MIT License](LICENSE).

## Contact
- [Nicholas Freitas](https://github.com/Nicholas-Freitas)
- [Project Repository](https://github.com/degrado-lab/Ribbon)







