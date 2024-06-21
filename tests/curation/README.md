# Curation

This test mimics a situation where a cluster is curated and the curation should be propagated.

**NOTE: the test now represents the current behaviour of the script, which is that if a cluster name is removed by curation, it becomes available for the assignment of novel clusters!**

## previous clustering
strain_01 and strain_02 are separated by 5 SNPs and form distinct clusters.

## First iteration
strain_03 is separated by 3 SNPs from strain_02 and forms a distinct cluster.

## Curation
The assignment of strain_03 is curated and added to the cluster of strain_02.

## Second iteration
strain_04 is closest to strain_03 and is added to the cluster of strain_02 and strain_03 while strain_05 forms a new cluster.