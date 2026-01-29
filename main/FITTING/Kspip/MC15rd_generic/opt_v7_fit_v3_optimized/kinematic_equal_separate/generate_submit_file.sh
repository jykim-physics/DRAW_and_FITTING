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
arguments            = \$(job_script) \$(sign)
" > job.sub

rm -f job_list.txt
for script in Dp_etapip_gg.py Dp_etapip_gg_K.py Dp_etapip_pipipi.py Dp_etapip_pipipi_K.py Dsp_etapip_gg.py Dsp_etapip_gg_K.py Dsp_etapip_pipipi.py Dsp_etapip_pipipi_K.py; do
    echo "$script plus " >> job_list.txt
    echo "$script minus " >> job_list.txt
done

echo "queue job_script, sign from job_list.txt" >> job.sub
