from ribbon.utils import make_directories, make_directory, list_files
from pathlib import Path
from ribbon.runner import Task
import tempfile
import shutil
import json

class LigandMPNN(Task):
    def __init__(self, output_dir, structure_list, num_designs=1):
        ''' Initialize a LigandMPNN task. 
        Args:
            output_dir (str): 
                The directory to save the output files.
            structure_list (list):
                A list of pdb or cif files to use as input structures.
            num_designs (int): The number of designs to generate per input structure.
        Returns:
            None
            Outputs the following directories:
                output_dir:
                    - backbones: The generated backbones
                    - packed: The packed structures, including sidechains
                    - sequences: The generated sequences as FASTA files. Multiple chains are separated by ':'. Each line is a different design.
                    - seqs_split: The sequences split into separate FASTA files, one per design. Each line is a separate chain. 
        '''
        # Initialize the Task class
        super().__init__()

        # This Task name matches the name in the tasks.json file
        self.task_name = "LigandMPNN"
        
        # Your arguments here:
        self.output_dir = output_dir
        self.structure_list = structure_list
        self.num_designs = num_designs

    def run(self):
        ''' Run the LigandMPNN task.'''
        
        ###### HELPER FUNCTIONS #######
        def split_ligandmpnn_fasta(fasta_file, split_output_dir):
            # Each LigandMPNN input produces a FASTA with multiple outputs as > lines. Each line has 1 or more chains separated by ':'.
            # Here, we separate each output into it's own FASTA file, with chains as separate > lines.
            split_output_dir.mkdir(parents=True, exist_ok=True)
            
            with open(fasta_file) as f:
                # Skip the first two lines (original input)
                lines = f.readlines()[2:]
                
                for i in range(0, len(lines), 2):
                    if not lines[i].startswith('>'):
                        continue
                    
                    name = lines[i].strip()
                    chains = lines[i + 1].strip().split(':')
                    index = 0
                    output_path = split_output_dir / f'{fasta_file.stem}_{index}.fasta'
                    
                    # Increment the index to avoid overwriting existing files
                    while output_path.exists():
                        index += 1
                        output_path = split_output_dir / f'{fasta_file.stem}_{index}.fasta'
                    
                    print(f'Writing to {output_path}')
                    with open(output_path, 'w') as g:
                        for chain_index, chain in enumerate(chains):
                            name_with_chain = f"{name.split(',')[0]}_{chain_index}" +', ' + ','.join(name.split(',')[1:])# Add chain to name
                            g.write(f'{name_with_chain}\n{chain}\n')

        # Make directories:
        self.output_dir = make_directory(self.output_dir)

        # Then, write out the files within pdb_input_dir to a json file:
        pdb_input_json = self.output_dir / 'pdb_input.json'
        with open(pdb_input_json, 'w') as f:
            json.dump(self.structure_list, f)
        
        # Run the task:
        self._run_task(self.task_name, 
                    pdb_input_json = pdb_input_json, 
                    output_dir = self.output_dir, 
                    num_designs = self.num_designs,
                    extra_args = self.extra_args,
                    device = self.device)
        
        # Split the FASTA files:
        for file in (self.output_dir / 'seqs').iterdir():
            print(f'Splitting {file}')
            split_ligandmpnn_fasta(file, self.output_dir / 'seqs_split')
        
        return 

class FastRelax(Task):
    def __init__(self, output_dir, pdb_input_file=None, pdb_input_dir=None, device='cpu'):
        ''' 
        TODO: fill out
        Also, change to accept list of PDBs instead of input file/dir system
        '''
         # Initialize the Task class
        super().__init__()

        # This Task name matches the name in the tasks.json file
        self.task_name = "FastRelax"
        
        # Task-specific variables
        if pdb_input_file is None and pdb_input_dir is None:
            raise ValueError('Must specify either pdb_input_file or pdb_input_dir')
        self.output_dir = make_directory(output_dir)
        self.pdb_input_file = pdb_input_file
        self.pdb_input_dir = pdb_input_dir
        self.device = device

    def run(self):
        # Handle input files
        if self.pdb_input_file is not None:
            temp_dir = tempfile.mkdtemp()
            shutil.copy(self.pdb_input_file, temp_dir)
            pdb_input_dir = temp_dir
        else:
            pdb_input_dir = self.pdb_input_dir

        # Prepare PDB files
        pdb_list = list_files(pdb_input_dir, '.pdb')
        pdb_string = " ".join(map(str, pdb_list)) + " "

        # Run the task
        self._run_task(
            self.task_name,
            pdb_string=pdb_string,
            output_dir=str(self.output_dir),
            device=self.device
        )

class Chai1(Task):
    def __init__(self, fasta_file, smiles_string, output_prefix, output_dir, device='gpu'):
        ''' Run the Chai-1 task.
        Args:
            fasta_file (str): 
                The FASTA file containing the protein sequence (no ligand). Only runs 1 system, with multiple chains/ligands optional.
            smiles_string (str): 
                The SMILES string of the ligand.
            output_prefix (str):
                The prefix for the output files. The output will be named this, + '_pred.model_idx_X.cif'
            output_dir (str):
                The directory to save the output files.
        '''
        # Initialize the Task class
        super().__init__()

        # This Task name matches the name in the tasks.json file
        self.task_name = "Chai-1"

        # Task-specific variables
        self.fasta_file = fasta_file
        self.smiles_string = smiles_string
        self.output_prefix = output_prefix
        self.output_dir = output_dir
        self.device = device

    def run(self):
        # Make the directory:
        self.output_dir = make_directory(self.output_dir)

        # Run the task
        self._run_task(
            self.task_name,
            fasta_file=self.fasta_file,
            smiles_string=self.smiles_string,
            output_dir=str(self.output_dir),
            output_prefix=self.output_prefix,
            device=self.device
        )

class CalculateDistance(Task):
    def __init__(self, pdb_file, chain1_id, res1_id, atom1_name,
                 chain2_id, res2_id, atom2_name, output_file, device='cpu'):
        ''' Calculate the distance between two atoms in a PDB file.
        Args:
            pdb_file (str): Path to the PDB file
            chain1_id (str): Chain ID of the first atom
            res1_id (str): Residue ID of the first atom
            atom1_name (str): Name of the first atom
            chain2_id (str): Chain ID of the second atom
            res2_id (str): Residue ID of the second atom
            atom2_name (str): Name of the second atom
            output_file (str): Path to the output file. Suffixed with '.dist'
        Returns:
            None
        ''' 
        # Initialize the Task class
        super().__init__()

        # This Task name matches the name in the tasks.json file
        self.task_name = "Calculate SASA"
        
        # Task-specific variables
        self.pdb_file = pdb_file
        self.chain1_id = chain1_id
        self.res1_id = res1_id
        self.atom1_name = atom1_name
        self.chain2_id = chain2_id
        self.res2_id = res2_id
        self.atom2_name = atom2_name
        self.output_file = output_file
        self.device = device

    def run(self):
        # Ensure output directory exists
        make_directory(Path(self.output_file).parent)

        # Run the task
        self._run_task(
            self.task_name,
            pdb_file=self.pdb_file,
            chain1_id=self.chain1_id,
            res1_id=self.res1_id,
            atom1_name=self.atom1_name,
            chain2_id=self.chain2_id,
            res2_id=self.res2_id,
            atom2_name=self.atom2_name,
            output_file=self.output_file,
            device=self.device
        )

class CalculateSASA(Task):
    def __init__(self, pdb_file, output_file, atom_1, atom_2, atom_3, atom_4, atom_5, atom_6, device='cpu'):
        ''' Calculate the distance between two atoms in a PDB file.
        Args:
            pdb_file (str):             Path to the PDB file
            output_file (str):          Path to the output file. Suffixed with '.angle'
            atom_1 - atom_6 (str):               Atom specifications, in format chain_id:res_id:atom_name.
        Returns:
            None
        '''
        # Initialize the Task class
        super().__init__()

        # This Task name matches the name in the tasks.json file
        self.task_name = "Calculate SASA"
        
        # Task-specific variables
        self.pdb_file = pdb_file
        self.output_file = output_file
        self.atom_1 = atom_1
        self.atom_2 = atom_2
        self.atom_3 = atom_3
        self.atom_4 = atom_4
        self.atom_5 = atom_5
        self.atom_6 = atom_6
        self.device = device

    def run(self):
        # Ensure output directory exists
        make_directory(Path(self.output_file).parent)

        # Run the task
        self._run_task(
            self.task_name,
            pdb_file=self.pdb_file,
            output_file=self.output_file,
            atom_1=self.atom_1,
            atom_2=self.atom_2,
            atom_3=self.atom_3,
            atom_4=self.atom_4,
            atom_5=self.atom_5,
            atom_6=self.atom_6,
            device=self.device
        )