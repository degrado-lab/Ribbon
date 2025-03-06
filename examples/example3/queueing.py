# Let's queue a Chai-1 Task!

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