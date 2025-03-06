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