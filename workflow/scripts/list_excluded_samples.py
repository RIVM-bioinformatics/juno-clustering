import argparse
import json
from pathlib import Path
import pandas as pd
import datetime
import logging


def read_input_data(input_files):
    data = {}
    for file in input_files:
        with open(file) as f:
            data[file.stem] = json.load(f)
    df = pd.DataFrame.from_dict(data, orient="index").reset_index(names="sample")
    df["mean_coverage"] = df["mean_coverage"].astype(float)
    return df


def exclude_on_coverage(df, threshold):
    df_copy = df.copy()
    return df_copy[df_copy["mean_coverage"] < threshold]


def exclude_on_pattern(df, pattern):
    df_copy = df.copy()
    return df_copy[~df_copy["sample"].str.contains(pattern)]


def read_previous_exclude_list(file):
    with open(file) as f:
        lines = f.readlines()
    if len(lines) == 0:
        return pd.DataFrame(columns=["sample", "reason", "date"])
    else:
        df = pd.read_csv(file, sep="\t")
        return df


def main(args):
    df = read_input_data(args.input)
    df_coverage_excluded = exclude_on_coverage(df, args.coverage_threshold)
    df_coverage_excluded["reason"] = "low_coverage"
    df_pattern_excluded = exclude_on_pattern(df, args.inclusion_pattern)
    df_pattern_excluded["reason"] = "not_NLA"
    df_excluded = pd.concat(
        [
            df_coverage_excluded[["sample", "reason"]],
            df_pattern_excluded[["sample", "reason"]],
        ]
    )
    df_excluded["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_previous_excluded = read_previous_exclude_list(args.previous_exclude_list)
    df_final = pd.concat([df_previous_excluded, df_excluded])
    df_final.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", type=Path, required=True, nargs="+")
    parser.add_argument("--previous-exclude-list", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--inclusion-pattern", type=str, required=True)
    parser.add_argument("--coverage-threshold", type=float, required=True)

    args = parser.parse_args()

    main(args)
