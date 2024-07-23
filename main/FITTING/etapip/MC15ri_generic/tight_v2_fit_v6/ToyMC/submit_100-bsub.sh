#!/bin/bash

# Define a dictionary mapping job names to Python scripts and directories
declare -A job_configs=(
    #["MC15ri_etapip_gg_fitv6_toyMC_100"]="etapip_gg_fit_v6_toymc_100.py:/share/storage/jykim/plots/MC15ri/etapip/gg/generic/"
    ["MC15ri_etapip_gg_fitv6_toyMC_100"]="etapip_gg_fit_v6_toymc_100.py:/home/belle2/jaeyoung/storage_ghi/Ntuples_ghi_2/MC15ri_generic/MC15ri_etaetapip_tight_v2_240419_Kp_BCS_etapi0const/bsub_log/"

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
    for ((i=0; i<=499; i++))
    do
        echo "Number: $i"
        # bsub -h "/cvmfs/belle.cern.ch/el9/externals/v02-00-02/Linux_x86_64/common/bin/python3 $python_script ${i}" -e "${dir}/${job_name}_${i}.err" -o "${dir}/${job_name}_${i}.out" -L "${dir}/${job_name}_${i}.log"
        echo "basf2 ${python_script} ${i}"
        bsub -q s -o "./bsub_log/${i}.out" -e "./bsub_log/${i}.err"  bash -c "basf2 ${python_script} ${i} > ${dir}/${job_name}_${i}.log" # -e "${dir}/${job_name}_${i}.err" -o "${dir}/${job_name}_${i}.out"
        sleep 0.001

    done
done
