# Cookbook

!!! warning 
    🚧 This page is under construction! We are still adding recipes for several `Tasks`. 🚧

## Chai-1
Chai-1 is a high accuracy, ligand-aware protein folding tool.
It takes as input a FASTA file, and outputs a directory of folded PDB structures.
Chai-1 scores are output as .npz files.

### Simple
Fold a protein from a sequence
``` python
ribbon.Chai1(
        fasta_file = 'my_sequence.fasta',   # A single input FASTA. If there are multiple sequences, they will be folded in the same structure.
        output_dir = './out'                # Where the outputs will be stored
    ).run()
```

### Advanced
Fold a protein from a sequence. Include two copies of ligand 
``` python
ribbon.Chai1(
        fasta_file = 'my_sequence.fasta',   # A single input FASTA. If there are multiple sequences, they will be folded in the same structure.
        output_dir = './out',               # Where the outputs will be stored
        smiles_string = 'C1=CC=CC=C1',      # SMILES string of our ligand
        num_ligands = 2,                    # How many copies of our ligand?
        device = 'gpu'                      # Run on GPU (necessary for Chai-1)
    ).run()
```

## LigandMPNN
LigandMPNN is a ligand-aware tool for designing sequences for a backbone structure.
It takes as input a list of PDB files, and outputs a sequence (or sequences) that are predicted to fold into that structure.
While LigandMPNN is gpu-accelerated, it seems to run fast on the CPU as well.

### Simple
Design a sequence for a backbone:
``` python
ribbon.LigandMPNN(
        structure_list = ['my_structure.pdb'],  # List of PDB files
        output_dir = './out'                    # Output directory
        num_designs = 5                         # How many sequences should we generate?
    ).run()
```
The output folder will have the following structure:
``` python
output_dir/
├─ backbones/    # Backbone structures with labeled AAs (but no sidechains)
├─ packed/       # (Optional) Backbone structures with packed sidechains
├─ seqs/         # A single FASTA containing the reference sequence and all designed sequences
└─ seqs_split/   # Individual FASTA files for each designed sequence
```

### Advanced
Design a homodimeric sequence, keeping crucial residues fixed.
This example uses the `extra_args` parameter to add extra parameters into your run command.
Note that this can inject arbitrary code into your container - use with caution!
```python
ligandmpnn_task = ribbon.LigandMPNN(
        structure_list = ['my_structure.pdb'],  # List of PDB files
        output_dir = './out'                    # Output directory
        num_designs = 5                         # How many sequences should we generate?
		extra_args= '--fixed_residues \"' + RESIDUES_TO_KEEP + '\" --homo_oligomer 1'	# Make sure to keep my catalytric residues, and make two chains identical.
	)
```

## RaptorX-Single
RaptorX-Single is a fast protein folding tool. It can fold small structures in as little as 5 seconds, after an initial loading period.
It takes as input a FASTA file (or directory containing FASTAs), and outputs a directory of folded PDB structures.

### Simple
Fold a directory of FASTA files
```python
    ribbon.RaptorXSingle(
            fasta_file_or_dir = './my_FASTA_directory/',
            output_dir = './out'
    ).run()
```

### Advanced
Fold a directory of FASTA files using a non-default model checkpoint (param). Run on the CPU (slower; GPU is default).
```python
    ribbon.RaptorXSingle(
            fasta_file_or_dir = './my_FASTA_directory/',
            output_dir = './out',
            param = 'RaptorX-Single-ESM1b-ESM1v-ProtTrans-Ab.pt',
            device='cpu'
    ).run()
```
The available model parameters are:
```python
'RaptorX-Single-ESM1b.pt',
'RaptorX-Single-ESM1v.pt',
'RaptorX-Single-ProtTrans.pt',
'RaptorX-Single-ESM1b-ESM1v-ProtTrans.pt',
'RaptorX-Single-ESM1b-Ab.pt',
'RaptorX-Single-ESM1v-Ab.pt',
'RaptorX-Single-ProtTrans-Ab.pt',
'RaptorX-Single-ESM1b-ESM1v-ProtTrans-Ab.pt'
```







