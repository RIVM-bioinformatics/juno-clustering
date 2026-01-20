import yaml
import os
import csv
import json
import re

sample_sheet = config["sample_sheet"]
with open(sample_sheet) as f:
    SAMPLES = yaml.safe_load(f)

for param in ["threads", "mem_gb"]:
    for k in config[param]:
        config[param][k] = int(config[param][k])

OUT = config["output_dir"]
INPUT = config["input_dir"]

# find collection using collfinder
# iget collection and save to a path passed to cli
PREVIOUS_CLUSTERING = config["previous_clustering"]

if PREVIOUS_CLUSTERING == "None":
    Path(OUT).mkdir(parents=True, exist_ok=True)
    Path(OUT + "/previous_list_excluded_samples.txt").touch()

DATE_APPEND_TSV = config["tsv"]
INPUT_COLLECTION_NAME = config["input_collection_name"]

SAMPLE_DATE_MAP = {}
if INPUT_COLLECTION_NAME is not None and str(INPUT_COLLECTION_NAME).lower() != 'none':
    input_basename = INPUT_COLLECTION_NAME.strip('/').split('/')[-1]
    default_date = input_basename[:6]
else:
    input_basename = os.path.basename(INPUT.rstrip('/'))
    default_date = input_basename[:6]
SAMPLES_LIST = list(SAMPLES.keys()) if isinstance(SAMPLES, dict) else SAMPLES

if DATE_APPEND_TSV is not None and str(DATE_APPEND_TSV).lower() != 'none':
    # TSV is provided, read sample and date columns
    with open(DATE_APPEND_TSV) as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            sample = row.get('sample')
            date = row.get('date')
            if sample and date:
                SAMPLE_DATE_MAP[sample] = date
    # Check for samples in SAMPLES not in TSV and assign default date
    for sample in SAMPLES_LIST:
        if sample not in SAMPLE_DATE_MAP:
            SAMPLE_DATE_MAP[sample] = default_date
else:
    for sample in SAMPLES_LIST:
        SAMPLE_DATE_MAP[sample] = default_date
print("Sample to Date Mapping:", SAMPLE_DATE_MAP)

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
    copy_assemblies_to_temp,
    copy_or_touch_list_excluded_samples,
    touch_list_excluded_samples,


include: "workflow/rules/combine_snp_profiles.smk"
include: "workflow/rules/distance_calculation.smk"
include: "workflow/rules/clustering.smk"


rule all:
    input:
        expected_outputs,
