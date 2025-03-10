#!/bin/bash
##SBATCH --job-name=your_job_name   # Job name
##SBATCH --output=job_output.log    # Standard output and error log
##SBATCH --ntasks=1                 # Run on a single CPU
##SBATCH --time=01:00:00            # Time limit hrs:min:sec
#SBATCH  --requeue                  # Requeue the job if it fails

echo "Running on $(hostname)"
echo "Starting at $(date)"
echo "TASK_DIR: $RIBBON_TASKS_MODULE_DIR"

echo apptainer run --nv $ribbon_container python $ribbon_deserialize_script $serialized_job

apptainer run --nv $ribbon_container python $ribbon_deserialize_script $serialized_job

## End-of-job summary, if running as a job
[[ -n "$SLURM_JOB_ID" ]] && scontrol show job "$SLURM_JOB_ID"  # This is useful for debugging and usage purposes,
                                                               # e.g. "did my job exceed its memory request?"