import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(
        description="Process data from an input directory to an output directory"
    )

    parser.add_argument(
        "-i",
        "--input-dir",
        required=True,
        type=Path,
        help="Path to the input directory"
    )

    return parser.parse_args()

def main():
    args = parse_args()

    input_dir = args.input_dir
    
    # Find files in the directory  
    input_dir = Path(input_dir)
    
    # define new folders
    fasta_folder = input_dir / "mtb_typing" / "consensus"
    json_folder = input_dir / "mtb_typing" / "seq_exp_json"
    
    # create folders to store the data
    fasta_folder.mkdir(parents=True, exist_ok=True)
    json_folder.mkdir(parents=True, exist_ok=True)
    
    # move and rename files
    for path in input_dir.rglob("*"):
        
        if path.is_file():
            new_folder = path.parent
            # determine new path
            if path.suffix == '.fasta':
                new_folder = fasta_folder
            if path.suffix == '.json':
                new_folder = json_folder
            
            # only move and rename fasta and json files from old folder 
            if len(path.parts) > 4 and path.suffix in ['.fasta', '.json']:
                # determine collection name
                name_extension = path.parts[4]
                # append collection name to file name
                new_name = f'{path.stem}_{name_extension}{path.suffix}'
                new_path = new_folder / new_name
                # move and rename file
                path.rename(new_path)
       
if __name__ == "__main__":
    main()

