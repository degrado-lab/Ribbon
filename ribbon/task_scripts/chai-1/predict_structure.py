##########################################
#### For use in the Chai-1 Container #####
##########################################

from pathlib import Path
import numpy as np
import torch
from chai_lab.chai1 import run_inference
import argparse
import tempfile
import shutil


''' 
Takes modified FASTA in the form of:
>protein|name=example-of-long-protein
AGSHSMRYFSTSVSRPGRGEPRFIAVGYVDD
>ligand|name=example-ligand-as-smiles
CCCCCCCCCCCCCC(=O)O
'''

def make_chai_fasta(input_fasta, output_fasta, smiles):
    with open(input_fasta, 'r') as infile, open(output_fasta, 'w') as outfile:
        for line in infile:
            if line.startswith(">"):
                # Modify header lines
                name = line.strip().replace(">", "")
                outfile.write(f">protein|name={name}\n")
            else:
                # Write the sequence lines as is
                outfile.write(line)
        
        # Add the SMILES string as a new entry for the ligand
        outfile.write(f">ligand|name=LIG\n")
        outfile.write(f"{smiles}\n")

def rename_files(output_dir, prefix):
    for file in output_dir.iterdir():
        if file.suffix in [".cif", ".npz"]:
            new_name = file.stem.replace("pred.model", prefix).replace("scores.model", prefix)
            new_file = file.with_name(new_name + file.suffix)
            file.rename(new_file)

if __name__=="__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description="Predict the structure of a protein-ligand complex.")
    parser.add_argument("fasta_file", type=str, help="Path to the FASTA file")
    parser.add_argument("SMILES_string", type=str, help="Ligand smiles string")
    parser.add_argument("output_dir", type=str, help="Path to the output directory")
    parser.add_argument("--num_trunk_recycles", type=int, help="Number of trunk recycles", default=3)
    parser.add_argument("--num_diffn_timesteps", type=int, help="Number of differentiable timesteps", default=200)
    parser.add_argument("--seed", type=int, help="Random seed", default=42)

    # Parse arguments
    args = parser.parse_args()
    fasta_file = args.fasta_file
    smiles = args.SMILES_string
    output_dir = args.output_dir
    num_trunk_recycles = args.num_trunk_recycles
    num_diffn_timesteps = args.num_diffn_timesteps
    seed = args.seed

    # Make a new FASTA file with the SMILES string as tempfile:
    temp_fasta = tempfile.NamedTemporaryFile(delete=False)
    make_chai_fasta(fasta_file, temp_fasta.name, smiles)

    # Store initial outputs to a temporary directory:
    temp_output = tempfile.TemporaryDirectory()
    
    fasta_path = Path(fasta_file)
    
    output_cif_paths = run_inference(
        fasta_file=Path(temp_fasta.name),
        output_dir=Path(temp_output.name),
        num_trunk_recycles=num_trunk_recycles,
        num_diffn_timesteps=num_diffn_timesteps,
        seed=seed,
        device=torch.device("cuda:0"),
        use_esm_embeddings=True,
    )

    # Rename the output files and move them to the output directory:
    rename_files(Path(temp_output.name), fasta_path.stem)
    for file in Path(temp_output.name).iterdir():
        shutil.move(str(file), str(Path(output_dir) / file.name))

# Load pTM, ipTM, pLDDTs and clash scores for sample 2
#scores = np.load(output_dir.joinpath("scores.model_idx_2.npz"))