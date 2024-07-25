if config["clustering_preset"] == "mycobacterium_tuberculosis":
    rule copy_or_touch_list_excluded_samples:
        output:
            temp(OUT + "/previous_list_excluded_samples.tsv"),
        params:
            previous_list = PREVIOUS_CLUSTERING + "/list_excluded_samples.tsv"
        shell:
            """
if [ -f {params.previous_list} ]
then
    cp {params.previous_list} {output}
else
    touch {output}
fi
            """
    
    rule list_excluded_samples:
        input:
            seq_exp_json = expand(INPUT + "/mtb_typing/seq_exp_json/{sample}.json", sample=SAMPLES),
            exclude_list = OUT + "/previous_list_excluded_samples.tsv",
        output:
            OUT + "/list_excluded_samples.tsv",
        log:
            OUT + "/log/list_excluded_samples.log",
        message:
            "Listing samples which should be excluded."
        resources:
            mem_gb=config["mem_gb"]["compression"],
        conda:
            "../envs/scripts.yaml"
        container:
            "docker://ghcr.io/boasvdp/juno_clustering_scripts:0.2"
        params:
            coverage_threshold=config["coverage_threshold"],
            inclusion_pattern=config["inclusion_pattern"],
        threads: config["threads"]["compression"]
        shell:
            """
# columns: sample, reason, date
python workflow/scripts/list_excluded_samples.py \
--input {input.seq_exp_json} \
--previous-exclude-list {input.exclude_list} \
--output {output} \
--inclusion-pattern {params.inclusion_pattern} \
--coverage-threshold {params.coverage_threshold} \
2>&1> {log}
            """
else:
    rule touch_list_excluded_samples:
        output:
            temp(OUT + "/list_excluded_samples.tsv"),
        shell:
            """
touch {output}
            """


# PREVIOUS_CLUSTERING is read into config as a str
if PREVIOUS_CLUSTERING == "None":

    rule clustering_from_scratch:
        input:
            distances=OUT + "/distances.tsv",
            exclude_list=OUT + "/list_excluded_samples.tsv",
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
--output {output} \
--exclude {input.exclude_list}
            """

else:

    rule clustering_from_previous:
        input:
            distances=OUT + "/distances.tsv",
            previous_clustering=PREVIOUS_CLUSTERING + "/clusters.csv",
            exclude_list=OUT + "/list_excluded_samples.txt",
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
--exclude {input.exclude_list}
--output {output}
            """
