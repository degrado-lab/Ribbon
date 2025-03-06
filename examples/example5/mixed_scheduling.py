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