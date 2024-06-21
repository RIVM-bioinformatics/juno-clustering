# TO DO
## Add per sample output for juno-cgmlst which can be listed by juno-library


rule decompress_snp_profiles:
    input:
        INPUT + "/aln.fa.gz",
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
        ""
    params:
        script="workflow/scripts/script.py",
    threads: config["threads"]["compression"]
    shell:
        """
pigz \
--decompress \
--stdout \
--processes {threads} \
{input} > {output}
        """


rule add_snp_profiles:
    input:
        previous_aln=OUT + "/old_aln.fa",
        assemblies=[SAMPLES[sample]["assembly"] for sample in SAMPLES],
    output:
        temp(OUT + "/aln.fa"),
    log:
        OUT + "/log/add_snp_profiles.log",
    message:
        "Adding SNP profiles to {input.previous_aln}."
    resources:
        mem_gb=config["mem_gb"]["add_snp_profiles"],
    conda:
        "../envs/scripts.yaml"
    container:
        ""
    shell:
        """
cat {input.previous_aln} {input.assemblies} > {output}
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
        ""
    threads: config["threads"]["compression"]
    shell:
        """
pigz \
--stdout \
--processes {threads} \
{input} > {output}
        """
