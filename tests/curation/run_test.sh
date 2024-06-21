#!/bin/bash

set -euxo pipefail

MAIN_DIR=$( pwd )

SCRIPT_DIR=$( dirname -- "${BASH_SOURCE[0]}" )
cd $SCRIPT_DIR

snp-dists -m aln_3.fa > dists_3.tsv

python "$MAIN_DIR"/workflow/scripts/cluster.py \
    --previous-clustering clusters_2.csv \
    --distances dists_3.tsv \
    --output clusters_3.csv \
    --threshold 2 \
    --log cluster_3.log \
    -vv

python edit_curated_cluster.py \
    --input clusters_3.csv \
    --sample strain_03 \
    --cluster A002 \
    --output clusters_3_edited.csv


snp-dists -m aln_5.fa > dists_5.tsv

python "$MAIN_DIR"/workflow/scripts/cluster.py \
    --previous-clustering clusters_3_edited.csv \
    --distances dists_5.tsv \
    --output clusters_5.csv \
    --threshold 2 \
    --log cluster_5.log \
    -vv

cmp clusters_5.csv clusters_5_correct.csv