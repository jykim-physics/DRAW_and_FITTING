#!/bin/bash

# Define a dictionary mapping job names to Python scripts and directories
declare -A job_configs=(
    ["MC15ri_etapip_gg"]="MC15ri_etapip_gg.py:/share/storage/jykim/plots/MC15ri/etapip/gg/"
    ["MC15ri_etapip_pipipi"]="MC15ri_etapip_pipipi.py:/share/storage/jykim/plots/MC15ri/etapip/pipipi/"
    ["MC15ri_etaeta_gg"]="MC15ri_etaeta_gg.py:/share/storage/jykim/plots/MC15ri/etaeta/gg/"
    ["MC15ri_etaeta_gpi"]="MC15ri_etaeta_gpi.py:/share/storage/jykim/plots/MC15ri/etaeta/gpi/"
    ["MC15ri_etaeta_pipi"]="MC15ri_etaeta_pipi.py:/share/storage/jykim/plots/MC15ri/etaeta/pipi/"
)

# Iterate over the keys of the dictionary and submit jobs
for job_name in "${!job_configs[@]}"; do
    config="${job_configs[$job_name]}"
    python_script=$(echo "$config" | cut -d ':' -f1)
    dir=$(echo "$config" | cut -d ':' -f2)
    if [ ! -d "$dir" ]; then
        # If it doesn't exist, create the directory
        mkdir -p "$dir"
        echo "Directory created successfully."
    else
        echo "Directory already exists."
    fi
    yhep_bsub -f /cvmfs/belle.cern.ch/el9/externals/v02-00-02/Linux_x86_64/common/bin/python3 -a "$python_script" -e "${dir}/${job_name}.err" -o "${dir}/${job_name}.out" -l "${dir}/${job_name}.log"
done

