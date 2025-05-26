#!/bin/bash

rm -f job.sub job_list.txt

cat <<EOF > job.sub
universe             = vanilla
getenv               = true
output               = log/job_summary_\$(Cluster)_\$(Process).out
error                = log/job_summary_\$(Cluster)_\$(Process).error
log                  = log/job_summary_\$(Cluster)_\$(Process).log
request_cpus         = 2
request_memory       = 4000
executable           = python3.sh
transfer_input_files = \$(job_script)
arguments            = \$(job_script) \$(sign) \$(bdt)
queue job_script, sign, bdt from job_list.txt
EOF

cat <<EOF > job_list.txt
etapip_gg_offset_novo_CB_Dp_Dm.py plus 0.83
etapip_gg_offset_novo_CB_Dp_Dm.py minus 0.83
etapip_pipipi_offset_novo_CB_Dp_Dm.py plus 0.75
etapip_pipipi_offset_novo_CB_Dp_Dm.py minus 0.75
etapip_gg_K_offset_CB_Dp_Dm.py plus 0.92
etapip_gg_K_offset_CB_Dp_Dm.py minus 0.92
etapip_pipipi_K_offset_CB_Dp_Dm.py plus 0.88
etapip_pipipi_K_offset_CB_Dp_Dm.py minus 0.88
EOF

