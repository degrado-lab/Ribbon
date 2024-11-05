import sys
from Bio import PDB
import argparse

def calculate_sasa(pdb_file, chain_id=None, res_id=None):
    # Determine if the structure is a PDB or mmCIF file
    if pdb_file.endswith('.cif'):
        parser = PDB.MMCIFParser(QUIET=True)
    else:
        parser = PDB.PDBParser(QUIET=True)
    
    # Parse the PDB file
    structure = parser.get_structure("structure", pdb_file)
    model = structure[0]  # Assuming single-model structures
    
    # Create a ShrakeRupley object for SASA calculation
    sr = PDB.ShrakeRupley()
    sr.compute(model, level="R")  # Compute at the residue level
    
    # Retrieve SASA for the specified chain or residue
    if chain_id:
        chain = model[chain_id]
        if res_id:
            # Get the specified residue
            residue = get_residue(chain, res_id)
            sasa = residue.sasa
            return sasa
        else:
            # Sum SASA over all residues in the chain
            sasa = sum(residue.sasa for residue in chain)
            return sasa
    else:
        # Sum SASA over all residues in the structure
        sasa = sum(residue.sasa for residue in model.get_residues())
        return sasa

def get_residue(chain, res_id):
    """
    Retrieve the residue from the chain. First, try a standard residue,
    and if that fails, attempt to retrieve a hetero-residue.
    """
    try:
        # Try to get a standard residue (hetfield = ' ')
        residue = chain[(' ', int(res_id), ' ')]
    except KeyError:
        # If standard residue is not found, search through hetero-residues
        hetero_residues = [res for res in chain.get_list() if res.id[0] != ' ']
        for res in hetero_residues:
            if res.id[1] == int(res_id):
                return res
        raise KeyError(f"Residue {res_id} not found in chain {chain.id}")
    return residue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate the solvent accessible surface area (SASA) of a chain or residue in a PDB file.")
    parser.add_argument("pdb_file", type=str, help="Path to the PDB file")
    parser.add_argument("--chain_id", type=str, help="Chain ID (optional)", default=None)
    parser.add_argument("--res_id", type=str, help="Residue ID (optional)", default=None)
    parser.add_argument("--output_file", type=str, help="Path to the output file", default=None)
    args = parser.parse_args()

    pdb_file = args.pdb_file
    chain_id = args.chain_id
    res_id = args.res_id
    output_file = args.output_file

    try:
        sasa = calculate_sasa(pdb_file, chain_id, res_id)
        if chain_id and res_id:
            print(f"The SASA of residue {res_id} in chain {chain_id} is: {sasa:.2f} Å²")
        elif chain_id:
            print(f"The SASA of chain {chain_id} is: {sasa:.2f} Å²")
        else:
            print(f"The total SASA of the structure is: {sasa:.2f} Å²")
        if output_file:
            with open(output_file, "w") as f:
                f.write(f"{sasa:.2f}")
    except KeyError as e:
        print(f"Error: Residue or chain not found. {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
