
# A Simple Example: Protein Folding

For this series of tutorials, all the code will be in the `examples` directory in the [repo](https://github.com/degrado-lab/Ribbon). After [installing](installation.md), Apptainer and ribbon, use the code in [`/examples/example1`](https://github.com/degrado-lab/Ribbon/tree/main/examples/example1) to follow along!

Let's say we want to fold a protein from an amino acid sequence. We'll use [Chai-1](https://github.com/chaidiscovery/chai-lab), a high-accuracy, ligand aware protein folding method. This requires a gpu!

First, we create a `Task` object, which sets up our Chai-1 job:

```python
import ribbon
my_folding_task = ribbon.Chai1(
        fasta_file = 'my_sequence.fasta',   # Input FASTA
        output_dir = './out'                # Where the outputs will be stored
)
```

Then, we run the `Task`:
```python
my_folding_task.run()
```

This can be shortened to a single command:
```python
import ribbon
ribbon.Chai1(
        fasta_file = 'my_sequence.fasta',   # Input FASTA
        output_dir = './out'                # Where the outputs will be stored
).run()
```

!!! info "Why the long wait?"
    When you run a `Task` for the first time, Ribbon will download all of the relevant software and scripts to your computer inside of a virtual machine. __This only happens once__!

