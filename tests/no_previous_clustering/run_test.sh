#!/bin/bash

set -euxo pipefail

MAIN_DIR=$( pwd )

SCRIPT_DIR=$( dirname -- "${BASH_SOURCE[0]}" )
cd $SCRIPT_DIR

snp-dists -m aln_4.fa > dists_4.tsv

python "$MAIN_DIR"/cluster.py \
    --distances dists_4.tsv \
    --output clusters_4.csv \
    --threshold 2 \
    --log cluster_4.log \
    -vv

cmp clusters_4.csv clusters_4_correct.csv