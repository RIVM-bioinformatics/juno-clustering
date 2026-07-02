#!/bin/bash

set -euxo pipefail

MAIN_DIR=$( pwd )

SCRIPT_DIR=$( dirname -- "${BASH_SOURCE[0]}" )
cd $SCRIPT_DIR

snp-dists -m aln_4.fa > dists_4.tsv

python "$MAIN_DIR"/workflow/scripts/cluster.py \
    --previous-clustering clusters_2.csv \
    --distances dists_4.tsv \
    --output clusters_4.csv \
    --threshold 2 \
    --log cluster_4.log \
    -vv

snp-dists -m aln_5.fa > dists_5.tsv

python "$MAIN_DIR"/workflow/scripts/cluster.py \
    --previous-clustering clusters_4.csv \
    --distances dists_5.tsv \
    --output clusters_5.csv \
    --threshold 2 \
    --log cluster_5.log \
    -vv

cmp clusters_5.csv clusters_5_correct.csv