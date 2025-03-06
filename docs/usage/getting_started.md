# How to use Ribbon

Ribbon is an easy-to-use python package, which simplifies the installation and running of protein design software.

Want to fold a protein? Once Ribbon is [installed](installation.md), it's as easy as:
```python
import ribbon
ribbon.Chai1(
        fasta_file = 'my_sequence.fasta',   # Input FASTA
        output_dir = './out'                # Where the outputs will be stored
).run()
```

To get started, move on to our initial tutorial: [A Simple Example: Protein Folding](1_protein_folding)