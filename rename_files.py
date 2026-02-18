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


def rewrite_fasta_header(src: Path, dst: Path) -> None:
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


def main():
    args = parse_args()

    input_dir = args.input_dir
    
    # Find files in the directory  
    input_dir = Path(input_dir)
    
    # define new folders
    fasta_folder = input_dir / "mtb_typing" / "consensus"
    json_folder = input_dir / "mtb_typing" / "seq_exp_json"
    
    # create folders to store the data
    fasta_folder.mkdir(parents=False, mode=755, exist_ok=True)
    json_folder.mkdir(parents=False, mode=755, exist_ok=True)
    dir_length = len(input_dir.parts)
    
    paths = list(input_dir.rglob("*"))
        
    # move and rename files
    for path in paths:
        
        if path.is_file():
            new_folder = path.parent
            # determine new path
            if path.suffix == '.fasta':
                new_folder = fasta_folder
            if path.suffix == '.json':
                new_folder = json_folder
            
            # only move and rename fasta and json files from old folder, so exclude the newly created ones
            if path.parts[1] != 'mtb_typing' and path.suffix in ['.fasta', '.json']:
                # determine collection name
                name_extension = path.parts[dir_length + 3]
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
    main()

