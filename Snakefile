import yaml


sample_sheet = config["sample_sheet"]
with open(sample_sheet) as f:
    SAMPLES = yaml.safe_load(f)

for param in ["threads", "mem_gb"]:
    for k in config[param]:
        config[param][k] = int(config[param][k])

OUT = config["output_dir"]

# find collection using collfinder
# iget collection and save to a path passed to cli
PREVIOUS_CLUSTERING = config["previous_clustering"]

# Configure pipeline outputs
expected_outputs = []

expected_outputs.append(OUT + "/clusters.csv")
expected_outputs.append(OUT + "/distances.tsv")

if config["clustering_type"] == "alignment":
    expected_outputs.append(OUT + "/aln.fa.gz")
elif config["clustering_type"] == "mlst":
    expected_outputs.append(OUT + "/cgmlst_alleles.tsv.gz")


localrules:
    all,


include: "workflow/rules/combine_snp_profiles.smk"
include: "workflow/rules/distance_calculation.smk"
include: "workflow/rules/clustering.smk"


rule all:
    input:
        expected_outputs,
