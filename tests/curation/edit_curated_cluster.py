#!/usr/bin/env python3

import pandas as pd
import argparse
import logging


def main():
    parser = argparse.ArgumentParser(description="Edit clustering file")
    parser.add_argument("--input", help="Input curated cluster file")
    parser.add_argument("--sample", help="Sample name", type=str)
    parser.add_argument("--cluster", help="Curated cluster name", type=str)
    parser.add_argument("--output", help="Output curated cluster file")
    args = parser.parse_args()

    # read input file
    df = pd.read_csv(args.input, dtype=str)
    assert (
        "curated_cluster" in df.columns
    ), "curated_cluster column not found in input file"
    assert "sample" in df.columns, "sample column not found in input file"

    # check if sample occurs once
    if not len(df.loc[df["sample"] == args.sample]) == 1:
        logging.warning(f"Sample {args.sample} occurs more than once in input file")

    # check if sample already has a curated cluster
    if not all(df.loc[df["sample"] == args.sample, "curated_cluster"].isna()):
        logging.warning(f"Sample {args.sample} already has a curated cluster assigned")

    # edit curated cluster and output
    df.loc[df["sample"] == args.sample, "curated_cluster"] = args.cluster
    df.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
