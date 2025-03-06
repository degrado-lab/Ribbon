
# Let's Get Pipelining

Since running a job is so simple, we can string many jobs together into a __pipeline__. (Code: `/examples/example2`) 

For example, we'll start with an initial PDB structure. We'll redesign the sequence using LigandMPNN, which will output several FASTA files that it thinks could fold into our input structure:
```python
ribbon.LigandMPNN(
    structure_list = ['my_structure.pdb'],
    output_dir = './out/lmpnn',
    num_designs = 5
).run()
```

I wonder how well LigandMPNN did? We can easily fold these sequences using the fast [RaptorX-Single]() software:
```python
ribbon.RaptorXSingle(
        fasta_file_or_dir = './out/lmpnn',
        output_dir = './out/raptorx'
).run()
```

Chaining these together, we get our first protein design pipeline:
```python
import ribbon

# First, we create 5 new sequences for this structure:
ribbon.LigandMPNN(
    structure_list = ['my_structure.pdb'],
    output_dir = './out/lmpnn',
    num_designs = 5
).run()
# These sequences are split into individual files, and are stored in 'out/seqs_split'

# Then, we fold using RaptorX:
ribbon.RaptorXSingle(
        fasta_file_or_dir = './out/lmpnn',
        output_dir = './out/raptorx'
).run()
```

!!! info "What are these files?"
    Certain `Tasks` need to create temporary files in the current directory while running (Such as a the `LigandMPNN/` folder, or `RaptorX-Single` symlink). In the future, I'd like Ribbon to clean these up better. For now, these files are safe to delete __as long as no `Tasks` are running__.
