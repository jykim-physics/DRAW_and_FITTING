rm -f job.sub
rm -f job_list.txt
echo "
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
" > job.sub

for script in etapip_gg_offset_novo_CB_Dp_Dm.py; do
    echo "$script plus 0.83" >> job_list.txt
    echo "$script minus 0.83" >> job_list.txt
done

for script in etapip_pipipi_offset_novo_CB_Dp_Dm.py; do
    echo "$script plus 0.75" >> job_list.txt
    echo "$script minus 0.75" >> job_list.txt
done

echo "queue job_script, sign, bdt from job_list.txt" >> job.sub
