#!/bin/bash

set -euo pipefail

#----------------------------------------------#
# User parameters
if [ ! -z "${1}" ] || [ ! -z "${2}" ] || [ ! -z "${irods_input_projectID}" ]
then
    input_dir="${1}"
    output_dir="${2}"
    PROJECT_NAME="${irods_input_projectID}"
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

# check if there is an exclusion file, if so change the parameter
if [ ! -z "${irods_input_sequencing__run_id}" ] && [ -f "/data/BioGrid/NGSlab/sample_sheets/${irods_input_sequencing__run_id}.exclude" ]
then
  EXCLUSION_FILE_COMMAND="-ex /data/BioGrid/NGSlab/sample_sheets/${irods_input_sequencing__run_id}.exclude"
else
  EXCLUSION_FILE_COMMAND=""
fi


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
## Run collfinder to get previous clustering run

mamba env create -f envs/collfinder.yaml --name collfinder_env
conda activate collfinder_env

# Run collfinder.py in subshell
PREVIOUS_RUN = $( python collfinder.py
    -i "$input_dir"
    -m projectID
    -x "sys::pipeline::gitrepo=https://github.com/RIVM-bioinformatics/Juno_clustering"
    -x "sys::data::state=valid"
    -r import_timestamp )

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

python juno_clustering.py \
    --queue "${QUEUE}" \
    -i "${input_dir}" \
    -o "${output_dir}" \
    --clustering-preset "${TYPE}" \
    --previous-clustering "${PREVIOUS_RUN}" \
    "${EXCLUSION_FILE_COMMAND}"

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
        echo "${attrname}: '${!key}'" >> ${OUTPUTDIR}/metadata.yml
    fi
done

set -euo pipefail

exit ${result}
