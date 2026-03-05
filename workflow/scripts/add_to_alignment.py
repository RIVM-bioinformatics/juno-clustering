#!/usr/bin/env python3

import logging
from pathlib import Path
import pyfastx
from typing import List, Tuple
import shutil
import json
import re


def read_fasta(filepath: Path) -> pyfastx.Fasta:
    """
    Read a fasta file using pyfastx.

    Parameters
    ----------
    filepath : Path
        Path to the fasta file. Is parsed as str, as pyfastx does not accept Path objects.

    Returns
    -------
    pyfastx.Fasta
        Fasta object.

    """
    try:
        logging.debug(f"Reading {filepath} as fasta.")
        fasta = pyfastx.Fasta(str(filepath), build_index=True)
    except Exception as e:
        logging.error(f"Error reading {filepath} as fasta: {e}")
        raise
    return fasta


def read_names_previous_aln(previous_aln: Path) -> List[str]:
    """
    List names from a previous alignment.

    Parameters
    ----------
    previous_aln : Path
        Path to the previous alignment.

    Returns
    -------
    List[str]
        List of names in the alignment.

    """
    logging.debug(f"Reading names from previous alignment {previous_aln}.")
    aln = read_fasta(previous_aln)
    logging.info(f"Found {len(aln)} sequences in {previous_aln}.")
    list_names = [name for name in aln.keys()]
    return list_names


def check_N_content(filepath: Path) -> float:
    """
    Calculate the proportion of Ns in a fasta file.

    Parameters
    ----------
    filepath : str
        Path to the fasta file.

    Returns
    -------
    float
        Proportion of Ns in the fasta file.

    """
    logging.debug(f"Checking N content in {filepath}.")
    # TODO: check if generator here can be reused higher up
    fasta = read_fasta(filepath)
    fa_composition = fasta.composition
    fa_size = fasta.size
    logging.debug(f"Composition of {filepath}: {fa_composition}, total {fa_size}.")
    N_content = fa_composition.get("N", 0)
    N_pct = N_content / fa_size
    logging.info(f"Found {N_content} Ns in {filepath} ({N_pct:.2%}).")
    return N_pct


def select_from_input_fasta(
    new_input: List[Path], N_pct_threshold: float, list_already_present: List[str]
) -> Tuple[List[str], List[str]]:
    """
    Select sequences from input fasta files based on N content and presence in previous alignment.

    Parameters
    ----------
    new_input : List[Path]
        List of paths to new input fasta files.
    N_pct_threshold : float
        Threshold for N content in input sequences.
    list_already_present : List[str]
        List of names already present in the previous alignment.

    Returns
    -------
    Tuple[List[str], List[str]]
        List of fasta sequences and list of names to be added to the alignment.

    """
    list_new_fa = []
    list_new_names = []
    for file in new_input:
        logging.info(f"Reading input fasta {file}.")
        N_pct = check_N_content(file)
        if N_pct > N_pct_threshold:
            logging.error(f"Input fasta {file} FAILED: too many Ns ({N_pct:.2%}).")
        else:
            logging.info(f"Input fasta {file} PASSED: N content ({N_pct:.2%}).")
            fa = read_fasta(file)
            for seq in fa:
                if seq.name in list_already_present:
                    # TODO: Discuss: overwrite or skip if already in alignment? Old sequence could be extracted and written to a new file.
                    logging.warning(
                        f"Sequence {seq.name} already in alignment. Skipping."
                    )
                else:
                    list_new_fa.append(seq.raw)
                    list_new_names.append(seq.name)
    logging.info(f"Selected {len(list_new_fa)} sequences to add to alignment.")
    return list_new_fa, list_new_names


def check_names_in_fa(fasta_path: Path, list_names: List[str]) -> None:
    """
    Check if all names are present in the fasta file.

    Parameters
    ----------
    fasta_path : Path
        Path to the fasta file.
    list_names : List[str]
        List of names to check.

    Raises
    ------
    ValueError
        If any of the names are not found in the fasta file.

    """
    errors = []
    fa = read_fasta(fasta_path)
    for name in list_names:
        if name not in fa:
            logging.error(f"Name {name} not found in {fasta_path}.")
            errors.append(ValueError(f"Name {name} not found in {fasta_path}."))
    if errors:
        raise BaseException(errors)
    else:
        logging.info(f"All names found in {fasta_path}.")


def rename_fasta_headers_with_date(fasta_path: Path, sample_date_map: dict):
    """
    Rename fasta headers by appending date from sample_date_map to sample name.

    Parameters
    ----------
    fasta_path : Path
        Path to the fasta file.
    sample_date_map : dict
        Mapping from sample name to date.
    """
    temp_path = fasta_path.with_suffix(".tmp")
    pattern = re.compile(r"^>(\S+)\s(.*)$")
    with open(fasta_path, "r") as infile, open(temp_path, "w") as outfile:
        for line in infile:
            if line.startswith(">"):
                m = pattern.match(line)
                if m:
                    sample = m.group(1)
                    rest = m.group(2)
                    if sample == "WGS_controle":
                        sample_prefix = sample
                    else:
                        sample_prefix = sample.split("_")[0]
                    date = sample_date_map.get(sample_prefix)
                    if date:
                        new_header = f">{sample_prefix}_{date} {rest}\n"
                        outfile.write(new_header)
                    else:
                        outfile.write(line)
                else:
                    outfile.write(line)
            else:
                outfile.write(line)
    fasta_path.unlink()
    temp_path.rename(fasta_path)

def main(args, sample_date_map=None) -> None:
    if args.previous_aln:
        list_previous_names = read_names_previous_aln(args.previous_aln)
        shutil.copyfile(args.previous_aln, args.output)
    else:
        list_previous_names = []
    list_new_fa, list_new_names = select_from_input_fasta(
        args.new_input, args.N_threshold, list_previous_names
    )
    with open(args.output, "a") as f:
        for seq in list_new_fa:
            f.write(seq)
    check_names_in_fa(args.output, list_previous_names + list_new_names)

    # Rename headers if mapping is provided
    if sample_date_map:
        rename_fasta_headers_with_date(args.output, sample_date_map)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Check and add sequences to an alignment."
    )

    parser.add_argument(
        "--previous-aln",
        type=Path,
        metavar="STR",
        help="Path to previous alignment.",
    )
    parser.add_argument(
        "--new-input",
        type=Path,
        metavar="STR",
        help="Path to new input sequences.",
        nargs="+",
    )
    parser.add_argument(
        "--N-content-threshold",
        dest="N_threshold",
        type=float,
        metavar="FLOAT",
        help="Exclude sample if N content in input sequence surpasses this ratio (range: 0.0-1.0).",
        default=0.5,
    )
    parser.add_argument(
        "--output",
        type=Path,
        metavar="STR",
        help="Path to output alignment.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Increase verbosity.",
    )
    parser.add_argument(
        "--sample-date-map",
        type=str,
        metavar="STR",
        help="Dict with sample-to-date mapping.",
        required=False,
    )

    args = parser.parse_args()

    #sohana added 050326
    # Expand directories to files
    expanded_new_inputs = []
    valid_exts = {".fa", ".fasta", ".fna", ".fa.gz"}
    for p in args.new_input:
        if p.is_dir():
            expanded_new_inputs.extend([f for f in p.iterdir() if f.suffix in valid_exts])
        else:
            if p.suffix in valid_exts:
                expanded_new_inputs.append(p)
    args.new_input = expanded_new_inputs
    ###############################################
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
    # Parse sample_date_map if provided
    if args.sample_date_map:
        sample_date_map = json.loads(args.sample_date_map)
    else:
        sample_date_map = None

    main(args, sample_date_map=sample_date_map)

    # main(args)
