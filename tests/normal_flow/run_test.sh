#!/bin/bash

set -euxo pipefail

MAIN_DIR=$( pwd )

SCRIPT_DIR=$( dirname -- "${BASH_SOURCE[0]}" )
cd $SCRIPT_DIR

snp-dists -m aln_4.fa > dists_4.tsv

python "$MAIN_DIR"/cluster.py \
    --previous-clustering clusters_2.csv \
    --distances dists_4.tsv \
    --output clusters_4.csv \
    --threshold 2 \
    --log cluster_4.log \
    -vv

snp-dists -m aln_7.fa > dists_7.tsv

python "$MAIN_DIR"/cluster.py \
    --previous-clustering clusters_4.csv \
    --distances dists_7.tsv \
    --output clusters_7.csv \
    --threshold 2 \
    --log cluster_7.log \
    -vv

cmp clusters_7.csv clusters_7_correct.csv