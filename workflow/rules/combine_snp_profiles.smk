# TODO: Add per sample output for juno-cgmlst which can be listed by juno-library


# Copy assemblies to a temporary directory in the output directory
# This is needed because pyfastx makes index files in the input directory which is not permitted by default on iRODS
rule copy_assemblies_to_temp:
    input:
        [SAMPLES[sample]["assembly"] for sample in SAMPLES],
    output:
        temp(directory(OUT + "/assemblies")),
    message:
        "Copying assemblies to temp."
    shell:
        """
mkdir -p {output}
cp {input} {output}
        """


# PREVIOUS_CLUSTERING is read into config as a str
if PREVIOUS_CLUSTERING == "None":

    rule combine_snp_profiles_from_scratch:
        input:
            OUT + "/assemblies",
        output:
            aln=temp(OUT + "/aln.fa"),
            index=temp(OUT + "/aln.fa.fxi"),
        log:
            OUT + "/log/combine_snp_profiles.log",
        message:
            "Combining SNP profiles from scratch."
        resources:
            mem_gb=config["mem_gb"]["compression"],
        conda:
            "../envs/scripts.yaml"
        container:
            "docker://ghcr.io/boasvdp/juno_clustering_scripts:0.2"
        params:
            N_content_threshold=config["N_content_threshold"],
        threads: config["threads"]["compression"]
        shell:
            """
python workflow/scripts/add_to_alignment.py \
--output {output.aln} \
--N-content-threshold {params.N_content_threshold} \
--new-input {input}/* 2>&1> {log}
            """

else:

    rule decompress_snp_profiles:
        input:
            PREVIOUS_CLUSTERING + "/aln.fa.gz",
        output:
            temp(OUT + "/old_aln.fa"),
        log:
            OUT + "/log/decompress_snp_profiles.log",
        message:
            "Uncompressing {input}."
        resources:
            mem_gb=config["mem_gb"]["compression"],
        conda:
            "../envs/scripts.yaml"
        container:
            "docker://ghcr.io/boasvdp/juno_clustering_scripts:0.2"
        params:
            script="workflow/scripts/script.py",
        threads: config["threads"]["compression"]
        shell:
            """
pigz \
--decompress \
--stdout \
--processes {threads} \
{input} 1> {output} 2> {log}
            """

    rule add_snp_profiles:
        input:
            previous_aln=OUT + "/old_aln.fa",
            assembly_dir=OUT + "/assemblies",
        output:
            aln=temp(OUT + "/aln.fa"),
            index=temp(OUT + "/aln.fa.fxi"),
        log:
            OUT + "/log/add_snp_profiles.log",
        message:
            "Adding SNP profiles to {input.previous_aln}."
        resources:
            mem_gb=config["mem_gb"]["compression"],
        conda:
            "../envs/scripts.yaml"
        container:
            "docker://ghcr.io/boasvdp/juno_clustering_scripts:0.2"
        params:
            N_content_threshold=config["N_content_threshold"],
        threads: config["threads"]["compression"]
        shell:
            """
python workflow/scripts/add_to_alignment.py \
--previous-aln {input.previous_aln} \
--output {output.aln} \
--N-content-threshold {params.N_content_threshold} \
--new-input {input.assembly_dir}/* 2>&1> {log}
            """


rule compress_snp_profiles:
    input:
        OUT + "/aln.fa",
    output:
        OUT + "/aln.fa.gz",
    log:
        OUT + "/log/compress_snp_profiles.log",
    message:
        "Compressing {input}."
    resources:
        mem_gb=config["mem_gb"]["compression"],
    conda:
        "../envs/scripts.yaml"
    container:
        "docker://ghcr.io/boasvdp/juno_clustering_scripts:0.2"
    threads: config["threads"]["compression"]
    shell:
        """
pigz \
--stdout \
--processes {threads} \
{input} > {output}
        """
