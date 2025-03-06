# Ribbon

Ribbon is a python package which simplifies the usage and pipelining of biological software. Installing and running state-of-the-art tools can be done with a simple python script.

## Quick Start
Want to fold a protein? Once Ribbon is [installed](https://degrado-lab.github.io/Ribbon/installation/), it's as easy as:

```python
import ribbon
ribbon.Chai1(
        fasta_file = 'my_sequence.fasta',   # Input FASTA
        output_dir = './out'                # Where the outputs will be stored
).run()
```

Please visit our [documentation](https://degrado-lab.github.io/Ribbon/) for full tutorials on using Ribbon.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact
- [Nicholas Freitas](https://github.com/Nicholas-Freitas)
- [Project Repository](https://github.com/degrado-lab/Ribbon)







