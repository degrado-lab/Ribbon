# Let's make a structure with RFDiffusionAA!

import ribbon
ribbon.RFDiffusionAA(
        input_structure = "my_structure.pdb",
        output_dir = "./out",
        contig_map = "[150-150]",
).run()

