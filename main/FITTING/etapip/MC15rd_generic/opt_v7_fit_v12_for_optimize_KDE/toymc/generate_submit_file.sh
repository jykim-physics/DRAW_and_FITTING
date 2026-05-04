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

#for script in etapip_gg_offset_CB.py etapip_pipipi_offset_CB.py; do
#    for sign in plus minus; do
#        echo "$script $sign" >> job_list.txt
#    done
#done

#for script in etapip_gg_K_offset_CB.py; do
for script in etapip_pipipi_K_offset_CB.py; do
    for sign in plus minus all; do
        echo "$script $sign" >> job_list.txt
    done
done

echo "queue job_script, sign from job_list.txt" >> job.sub

