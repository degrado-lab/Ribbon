import ribbon

# First, we create 5 new sequences for this structure:
lmpnn_task = ribbon.LigandMPNN(
    structure_list = ['my_structure.pdb'],
    output_dir = './out/lmpnn',
    num_designs = 5
).run()