# PREVIOUS_CLUSTERING is read into config as a str
if PREVIOUS_CLUSTERING == "None":

    rule clustering_from_scratch:
        input:
            distances=OUT + "/distances.tsv",
        output:
            OUT + "/clusters.csv",
        log:
            OUT + "/log/clustering.log",
        message:
            "Clustering {input.distances} with threshold {params.threshold}"
        resources:
            mem_gb=config["mem_gb"]["clustering"],
        conda:
            "../envs/clustering.yaml"
        container:
            "docker://ghcr.io/boasvdp/network_analysis:0.2"
        params:
            threshold=config["cluster_threshold"],
            merged_cluster_separator=config["merged_cluster_separator"],
        threads: config["threads"]["clustering"]
        shell:
            """
python workflow/scripts/cluster.py \
--threshold {params.threshold} \
--distances {input.distances} \
--output {output} \
--log {log} \
--verbose \
--merged-cluster-separator {params.merged_cluster_separator:q} \
--output {output}
            """

else:

    rule clustering_from_previous:
        input:
            distances=OUT + "/distances.tsv",
            previous_clustering=PREVIOUS_CLUSTERING + "/clusters.csv",
        output:
            OUT + "/clusters.csv",
        log:
            OUT + "/log/clustering.log",
        message:
            "Clustering {input.distances} with threshold {params.threshold}"
        resources:
            mem_gb=config["mem_gb"]["clustering"],
        conda:
            "../envs/clustering.yaml"
        container:
            "docker://ghcr.io/boasvdp/network_analysis:0.2"
        params:
            threshold=config["cluster_threshold"],
            merged_cluster_separator=config["merged_cluster_separator"],
        threads: config["threads"]["clustering"]
        shell:
            """
python workflow/scripts/cluster.py \
--threshold {params.threshold} \
--distances {input.distances} \
--previous-clustering {input.previous_clustering} \
--output {output} \
--log {log} \
--verbose \
--merged-cluster-separator {params.merged_cluster_separator:q} \
--output {output}
            """
