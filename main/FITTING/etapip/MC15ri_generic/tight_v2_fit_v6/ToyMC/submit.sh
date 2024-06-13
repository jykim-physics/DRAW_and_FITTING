#!/bin/bash

# Define a dictionary mapping job names to Python scripts and directories
declare -A job_configs=(
    ["MC15ri_etapip_gg_fitv6_toyMC_numcpu4_10000"]="etapip_fit_v6_toymc.py:/share/storage/jykim/plots/MC15ri/etapip/gg/generic/"
    #["MC15ri_etapip_pipipi_fitv6"]="etapip_pipipi_1ab_tight_v2.py:/share/storage/jykim/plots/MC15ri/etapip/pipipi/generic/"
    #["MC15ri_etapip_gg_cc_fitv6"]="etapip_gg_cc_1ab_tight_v2.py:/share/storage/jykim/plots/MC15ri/etapip/gg/generic/"
    #["MC15ri_etapip_pipipi_cc_fitv6"]="etapip_pipipi_cc_1ab_tight_v2.py:/share/storage/jykim/plots/MC15ri/etapip/pipipi/generic/"
    #["MC15ri_etaKp_gg_fitv2"]="etaKp_gg_1ab_tight_v2.py:/share/storage/jykim/plots/MC15ri/etaKp/gg/generic/"
    #["MC15ri_etaKp_gg_cc_fitv2"]="etaKp_gg_cc_1ab_tight_v2.py:/share/storage/jykim/plots/MC15ri/etaKp/gg/generic/"
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
