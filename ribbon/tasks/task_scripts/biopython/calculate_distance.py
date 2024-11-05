##########################################
### For use in the Biopython Container ###
##########################################

import sys
from Bio import PDB
import argparse

def calculate_atom_distance(pdb_file, res1_id, chain1_id, atom1_name, res2_id, chain2_id, atom2_name):
    # Find out if structure is a PDB or mmCIF file:
    if pdb_file.endswith('.cif'):
        parser = PDB.MMCIFParser(QUIET=True)
    else:
        parser = PDB.PDBParser(QUIET=True)
    
    # Parse the PDB file
    structure = parser.get_structure("structure", pdb_file)
    
    # Get the chains specified by the user
    chain1 = structure[0][chain1_id]
    chain2 = structure[0][chain2_id]
    
    # Get the residues specified by the user, including hetero-residues
    res1 = get_residue(chain1, res1_id)
    res2 = get_residue(chain2, res2_id)
    
    # Get the atoms specified by the user
    atom1 = res1[atom1_name]
    atom2 = res2[atom2_name]
    
    # Calculate the distance between the atoms
    distance = atom1 - atom2
    return distance

def get_residue(chain, res_id):
    """
    Try to retrieve the residue from the chain. First, try a standard residue,
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
    ##if len(sys.argv) != 8:
    #    print("Usage: python3 calculate_distance.py <pdb_file> <chain1_id> <res1_id> <atom1_name> <chain2_id> <res2_id> <atom2_name> [--output_file <output_file>]")
    #    sys.exit(1)

    parser = argparse.ArgumentParser(description="Calculate the distance between two atoms in a PDB file.")
    parser.add_argument("pdb_file", type=str, help="Path to the PDB file")
    parser.add_argument("chain1_id", type=str, help="Chain ID of the first atom")
    parser.add_argument("res1_id", type=str, help="Residue ID of the first atom")
    parser.add_argument("atom1_name", type=str, help="Name of the first atom")
    parser.add_argument("chain2_id", type=str, help="Chain ID of the second atom")
    parser.add_argument("res2_id", type=str, help="Residue ID of the second atom")
    parser.add_argument("atom2_name", type=str, help="Name of the second atom")
    parser.add_argument("--output_file", type=str, help="Path to the output file", default=None)
    args = parser.parse_args()

    pdb_file = args.pdb_file
    chain1_id = args.chain1_id
    res1_id = args.res1_id
    atom1_name = args.atom1_name
    chain2_id = args.chain2_id
    res2_id = args.res2_id
    atom2_name = args.atom2_name
    output_file = args.output_file

    try:
        distance = calculate_atom_distance(pdb_file, res1_id, chain1_id, atom1_name, res2_id, chain2_id, atom2_name)
        print(f"The distance between {atom1_name} in residue {res1_id} (chain {chain1_id}) and {atom2_name} in residue {res2_id} (chain {chain2_id}) is: {distance:.2f} Å")
        if output_file:
            with open(output_file, "w") as f:
                f.write(f"{distance:.2f}")
    except KeyError as e:
        print(f"Error: Residue, chain, or atom not found. {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
