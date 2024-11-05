import sys
from Bio import PDB
import argparse
import math
import numpy as np

def calculate_plane_angle(pdb_file, atoms1, atoms2):
    # Determine if the structure is a PDB or mmCIF file
    if pdb_file.endswith('.cif'):
        parser = PDB.MMCIFParser(QUIET=True)
    else:
        parser = PDB.PDBParser(QUIET=True)
    
    # Parse the PDB file
    structure = parser.get_structure("structure", pdb_file)
    model = structure[0]  # Assuming single-model structures

    # Get the coordinates of the six atoms
    coords1 = get_atom_coords(structure, atoms1)
    coords2 = get_atom_coords(structure, atoms2)

    # Calculate the normal vectors of the two planes
    normal1 = calculate_normal(coords1)
    normal2 = calculate_normal(coords2)

    # Calculate the angle between the normals
    angle = calculate_angle_between_normals(normal1, normal2)

    return angle

def get_atom_coords(structure, atom_specs):
    """
    Given the structure and a list of atom specifications (chain_id, res_id, atom_name),
    returns a list of numpy arrays of the coordinates of these atoms.
    """
    coords = []
    for chain_id, res_id, atom_name in atom_specs:
        chain = structure[0][chain_id]
        residue = get_residue(chain, res_id)
        atom = residue[atom_name]
        coord = atom.get_coord()
        coords.append(coord)
    return coords

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

def calculate_normal(coords):
    """
    Given three coordinates (numpy arrays), calculate the normal vector of the plane.
    """
    p1, p2, p3 = coords
    v1 = p2 - p1
    v2 = p3 - p1
    normal = np.cross(v1, v2)
    # Normalize the normal vector
    normal = normal / np.linalg.norm(normal)
    return normal

def calculate_angle_between_normals(n1, n2):
    """
    Calculate the angle between two normal vectors in degrees.
    """
    # Dot product and norms
    dot_product = np.dot(n1, n2)
    # Ensure the dot product is in the range [-1, 1] to avoid numerical errors
    dot_product = np.clip(dot_product, -1.0, 1.0)
    angle_rad = np.arccos(dot_product)
    angle_deg = np.degrees(angle_rad)
    return angle_deg

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate the angle between two planes defined by three atoms each.")
    parser.add_argument("pdb_file", type=str, help="Path to the PDB file")
    parser.add_argument("atom_specs", type=str, nargs=6, help="Atom specifications in the format chain_id:res_id:atom_name")
    parser.add_argument("--output_file", type=str, help="Path to the output file", default=None)
    args = parser.parse_args()

    pdb_file = args.pdb_file
    atom_specs = args.atom_specs
    output_file = args.output_file

    # Parse the atom specifications
    atoms1 = []
    atoms2 = []
    for i in range(6):
        spec = atom_specs[i]
        try:
            chain_id, res_id, atom_name = spec.split(":")
            atom_spec = (chain_id, res_id, atom_name)
            if i < 3:
                atoms1.append(atom_spec)
            else:
                atoms2.append(atom_spec)
        except ValueError:
            print(f"Error: Atom specification '{spec}' is invalid. Should be in the format chain_id:res_id:atom_name")
            sys.exit(1)

    try:
        angle = calculate_plane_angle(pdb_file, atoms1, atoms2)
        print(f"The angle between the two planes is: {angle:.2f} degrees")
        if output_file:
            with open(output_file, "w") as f:
                f.write(f"{angle:.2f}")
    except KeyError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
