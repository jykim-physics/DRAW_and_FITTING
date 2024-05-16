#!/bin/bash

# Define a dictionary mapping job names to Python scripts and directories
declare -A job_configs=(
    ["MC15ri_Kspip"]="Kspip_gg_1ab_tight_v2.py:/share/storage/jykim/plots/MC15ri/Kspip/generic/"
    ["MC15ri_Kspip_cc"]="Kspip_gg_cc_1ab_tight_v2.py:/share/storage/jykim/plots/MC15ri/Kspip/generic/"
    ["MC15ri_KsKp"]="KsKp_gg_1ab_tight_v2.py:/share/storage/jykim/plots/MC15ri/Kspip/generic/"
    ["MC15ri_KsKp_cc"]="KsKp_gg_cc_1ab_tight_v2.py:/share/storage/jykim/plots/MC15ri/Kspip/generic/"
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
