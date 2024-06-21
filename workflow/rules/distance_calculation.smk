# Naive all vs all distance calculation
# Improvement: check which distances have been calculated and only calculate the missing ones
rule distance_calculation_snp:
    input:
        OUT + "/aln.fa",
    output:
        OUT + "/distances.tsv",
    conda:
        ""
    container:
        "docker://ghcr.io/boasvdp/distle:0.1.0"
    params:
        max_distance=config["max_distance"],
        output_mode="full",
    log:
        OUT + "/log/distance_calculation_snp.log",
    shell:
        """
distle \
--verbose \
--input-format fasta \
--output-mode {params.output_mode} \
--maxdist {params.max_distance} \
{input} {output} 2&>1 > {log}
        """


rule distance_calculation_cgmlst:
    input:
        OUT + "/cgmlst_profiles.tsv",
    output:
        OUT + "/distances.tsv",
    conda:
        ""
    container:
        "docker://ghcr.io/boasvdp/distle:0.1.0"
    params:
        max_distance=config["max_distance"],
        output_mode="full",
    log:
        OUT + "/log/distance_calculation_cgmlst.log",
    shell:
        """
distle \
--verbose \
--input-format cgmlst \
--output-mode {params.output_mode} \
--maxdist {params.max_distance} \
{input} {output} 2&>1 > {log}
        """
