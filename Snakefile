import yaml


sample_sheet = config["sample_sheet"]
with open(sample_sheet) as f:
    SAMPLES = yaml.safe_load(f)

for param in ["threads", "mem_gb"]:
    for k in config[param]:
        config[param][k] = int(config[param][k])

OUT = config["output_dir"]

# Configure pipeline outputs
expected_outputs = []

expected_outputs.append(OUT + "/clusters.tsv")
expected_outputs.append(OUT + "/distances.tsv")

if config["clustering_type"] == "juno-variant-typing":
    expected_outputs.append(OUT + "/aln.fa.gz")
elif config["clustering_type"] == "juno-cgmlst":
    expected_outputs.append(OUT + "/cgmlst_alleles.tsv.gz")


localrules:
    all,


include: "workflow/rules/combine_snp_profiles.smk"
include: "workflow/rules/distance_calculation.smk"
include: "workflow/rules/clustering.smk"


rule all:
    input:
        expected_outputs,
