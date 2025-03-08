# Let's make a structure with RFDiffusionAA!

import ribbon
ribbon.RFDiffusionAA(
        input_structure = "my_structure.pdb",
        output_dir = "./out4",
        contig_map = "[\\'A1-103,30-50,A109-125\\']",
        ligand = "LIG",
        diffuser_steps = 100,
        design_startnum = 5,
).run()