#!/bin/bash

set -euo pipefail

#----------------------------------------------#
# User parameters
if [ ! -z "${1}" ] || [ ! -z "${2}" ] || [ ! -z "${irods_runsheet_projectID}" ]
then
    input_dir="${1}"
    output_dir="${2}"
    PROJECT_NAME="${irods_runsheet_projectID}"
else
    echo "This shell script is only used to run the pipeline in the RIVM iRODS environment."
    echo "One of the parameters is missing, make sure there is an input directory, output directory and project name(param 1, 2 or irods_input_projectID)."
    exit 1
fi

if [ ! -d "${input_dir}" ] || [ ! -d "${output_dir}" ]
then
    echo "The input directory $input_dir or the output directory $output_dir does not exist"
    exit 1
fi

# set +u
# # check if there is an exclusion file, if so change the parameter
# if [ ! -z "${irods_input_sequencing__run_id}" ] && [ -f "/data/BioGrid/NGSlab/sample_sheets/${irods_input_sequencing__run_id}.exclude" ]
# then
#   EXCLUSION_FILE="/data/BioGrid/NGSlab/sample_sheets/${irods_input_sequencing__run_id}.exclude"
# else
#   EXCLUSION_FILE=""
# fi
# set -u


#----------------------------------------------#
## make sure conda works

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/mnt/miniconda/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/mnt/miniconda/etc/profile.d/conda.sh" ]; then
        . "/mnt/miniconda/etc/profile.d/conda.sh"
    else
        export PATH="/mnt/miniconda/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<export -f conda
export -f __conda_activate
export -f __conda_reactivate
export -f __conda_hashr

#----------------------------------------------#
# Run collfinder to get previous clustering run

mamba env create -f envs/collfinder.yaml --name collfinder_env
conda activate collfinder_env

# Run collfinder.py in subshell
# exclude collections with input_collection = irods_runsheet_sys__runsheet__input_collection
# to be able to rerun (after adding curated clusters.csv)

set -x
PREVIOUS_RUN=$( python workflow/scripts/collfinder.py \
    -i ${irods_runsheet_sys__runsheet__input_collection} \
    -x "sys::pipeline::gitrepo=https://github.com/RIVM-bioinformatics/juno-clustering.git" \
    -m projectID \
    -x "sys::data::state=valid" \
    -r "sys::run::finish_time" \
    -X "user::data::state=invalid" \
    -X "user::pipeline::input_collection=${irods_runsheet_sys__runsheet__input_collection}" \
    -X "sys::runsheet::input_collection=${irods_runsheet_sys__runsheet__input_collection}" \
    -l "../output/log/collfinder.log"
    )

# Run find_downstream_clusterfile.py in subshell
set -x
CURATED_CLUSTERING_COLL=$( python workflow/scripts/find_downstream_clusterfile.py \
    -p ${PREVIOUS_RUN} \
    -x "sys::data::state=valid" \
    -X "user::data::state=invalid" \
    -l "../output/log/find_downstream_clusterfile.log"
    )

# Download the previous run collection and downstream collection containing curated cluster file
if [ ! -z "${PREVIOUS_RUN}" ] ; then
    iget -r -v ${PREVIOUS_RUN}
    l_previous_run="$(pwd)/$(basename ${PREVIOUS_RUN})"
    
    # copy previous clustering file to the output collection
    cp ${l_previous_run}/clusters.csv ../output/clusters_previous.csv
    
    # set provenance information for previous clustering:
    echo user::pipeline::input_collection: "${PREVIOUS_RUN}" >> ${output_dir}/metadata.yml
fi

if [ ! -z "${CURATED_CLUSTERING_COLL}" ] ; then
    iget -r -v ${CURATED_CLUSTERING_COLL}
    l_curated_clustering_coll="$(pwd)/$(basename ${CURATED_CLUSTERING_COLL})"
    
    # copy the curated clusters.csv files to the output collection
    cp ${l_curated_clustering_coll}/clusters.csv ../output/clusters_previous_curated.csv
    
    # copy the clusters.csv from the downstream to the previous_run folder
    mv ${l_previous_run}/clusters.csv ${l_previous_run}/clusters.csv.old
    cp ${l_curated_clustering_coll}/clusters.csv ${l_previous_run}/clusters.csv
    
    # set provenance information for previous clustering:
    echo user::pipeline::input_collection_curated_cluster: "${CURATED_CLUSTERING_COLL}" >> ${output_dir}/metadata.yml
fi

conda deactivate
    
#----------------------------------------------#
# Install pipeline conda env
mamba env create -f envs/juno_clustering.yaml --name pipeline_env
conda activate pipeline_env

#----------------------------------------------#
# Run the pipeline

echo -e "\nRun pipeline..."

if [ ! -z ${irods_runsheet_sys__runsheet__lsf_queue} ]; then
    QUEUE="${irods_runsheet_sys__runsheet__lsf_queue}"
else
    QUEUE="bio"
fi

case $PROJECT_NAME in
  myco)
    TYPE="mycobacterium_tuberculosis"
    ;;
  salm)
    TYPE="salmonella"
    ;;
  *)
    TYPE="unknown"
    ;;
esac

set -euo pipefail

# make a copy of the input dir (to get rename permissions)
input_dir_copy = "${input_dir}" + "_copy"
mkdir ${input_dir_copy}

USER=$(id -un)
GROUP=$(id -gn)

bindfs \
  --force-user="${USER}" \
  --force-group="${GROUP}" \
  --perms=u=rwx:g=rx:o=rx \
  ${input_dir} ${input_dir_copy}

python workflow/scripts/rename_files.py \
    --input-dir "${input_dir_copy}" \
    --input-coll "${irods_runsheet_sys__runsheet__input_collection}" \
    -l "../output/log/rename_files.log"


if [ ! -z "${PREVIOUS_RUN}" ] ; then
    echo "Using previous clustering run: ${PREVIOUS_RUN}"
    python juno_clustering.py \
        --queue "${QUEUE}" \
        -i "${input_dir_copy}" \
        -o "${output_dir}" \
        --clustering-preset "${TYPE}" \
        --previous-clustering "${l_previous_run}" \
        --input-collection-name "${irods_runsheet_sys__runsheet__input_collection}"
else  
python juno_clustering.py \
    --queue "${QUEUE}" \
    -i "${input_dir_copy}" \
    -o "${output_dir}" \
    --clustering-preset "${TYPE}"
fi

result=$?

# Propagate metadata

set +euo pipefail

SEQ_KEYS=
SEQ_ENV=`env | grep irods_input_sequencing`
for SEQ_AVU in ${SEQ_ENV}
do
    SEQ_KEYS="${SEQ_KEYS} ${SEQ_AVU%%=*}"
done

for key in $SEQ_KEYS irods_input_illumina__Flowcell irods_input_illumina__Instrument \
    irods_input_illumina__Date irods_input_illumina__Run_number irods_input_illumina__Run_Id
do
    if [ ! -z ${!key} ] ; then
        attrname=${key:12}
        attrname=${attrname/__/::}
        echo "${attrname}: '${!key}'" >> ${output_dir}/metadata.yml
    fi
done


set -euo pipefail

exit ${result}
