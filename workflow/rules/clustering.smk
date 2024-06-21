rule clustering:
    input:
        distances=OUT + "/distances.tsv",
        previous_clustering=PREVIOUS_CLUSTERING + "/clusters.tsv",
    output:
        OUT + "/clusters.tsv",
    log:
        OUT + "/log/clustering.log",
    message:
        "Clustering {input.distances} with threshold {params.threshold}"
    resources:
        mem_gb=config["mem_gb"]["compression"],
    conda:
        "../envs/clustering.yaml"
    container:
        ""
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
--merged-cluster-separator {params.merged_cluster_separator}
--output {output}
        """
