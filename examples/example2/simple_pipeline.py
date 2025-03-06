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