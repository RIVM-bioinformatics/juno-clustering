import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(
        description="Input folder"
    )

    parser.add_argument(
        "-i", "--input-dir", required=True, type=Path,
        help="Path to the input directory")
    parser.add_argument(
        "-ic", "--input_coll", required=True, type=str,
        help="Input Collection name")

    return parser.parse_args()


def rewrite_fasta_header(src: Path, dst: Path) -> None:
    '''
    change the fasta header to contain the renamed filename
    '''
    new_id = dst.stem  # or src.stem — choose intentionally

    with src.open() as fin, dst.open("w") as fout:
        header = fin.readline()

        if not header.startswith(">"):
            raise ValueError("FASTA file does not start with a header")

        parts = header[1:].strip().split(maxsplit=1)
        rest = f" {parts[1]}" if len(parts) > 1 else ""

        fout.write(f">{new_id}{rest}\n")

        # copy the remainder verbatim
        fout.writelines(fin)


def rename_files():
    '''
    Rename files in an input directory to make the names unique by adding the collection name as a prefix
    Depends the source of the data. If in iRODS a runsheet is used with multiple input collections the
    data will be on a  
    '''
        
    args = parse_args()

    input_dir = args.input_dir
    input_coll = args.input_coll
    
    # Find files in the directory  
    input_dir = Path(input_dir)
    
    # define new folders
    fasta_folder = input_dir / "mtb_typing" / "consensus"
    json_folder = input_dir / "mtb_typing" / "seq_exp_json"
    audit_trail = input_dir / "audit_trail"
    
    # create folders to store the data
    fasta_folder.mkdir(parents=True, exist_ok=True)
    json_folder.mkdir(parents=True, exist_ok=True)
    audit_trail.mkdir(parents=True, exist_ok=True)
    dir_length = len(input_dir.parts)
    
    paths = list(input_dir.rglob("*"))
    
        
    # move and rename files
    for path in paths:
        
        if not path.is_file():
            continue
        
        new_folder = path.parent
        
        # only move and rename fasta and json files from old folder, so exclude the newly created ones
        if path.parts[1] != 'mtb_typing' and path.suffix in ['.fasta', '.json']:
            # determine collection name
            name_extension = input_coll.split('/')[-1]
            # append collection name to file name
            new_name = f'{path.stem}_{name_extension}{path.suffix}'
            new_path = new_folder / new_name
            
            # rewrite fasta header to correspond with file name and move file
            if path.suffix == '.fasta':
                rewrite_fasta_header(path, new_path)
            # move and rename json file
            if path.suffix == '.json':
                path.rename(new_path)
            
            print(f'Moved {path} to {new_path}')
       

if __name__ == "__main__":
    
    rename_files()


