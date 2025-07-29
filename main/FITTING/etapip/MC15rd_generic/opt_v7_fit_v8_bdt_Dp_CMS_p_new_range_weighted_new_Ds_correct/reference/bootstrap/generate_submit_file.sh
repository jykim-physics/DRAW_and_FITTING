echo "
universe             = vanilla
getenv               = true
output               = log/job_summary_\$(Cluster)_\$(Process).out
error                = log/job_summary_\$(Cluster)_\$(Process).error
log                  = log/job_summary_\$(Cluster)_\$(Process).log
request_cpus         = 14
request_memory       = 28000
executable           = python3.sh
transfer_input_files = \$(job_script)
arguments            = \$(job_script) \$(sign)
" > job.sub

rm -f job_list.txt

#for script in etapip_gg_K_ref.py etapip_pipipi_K_ref.py; do
for script in etapip_pipipi_K_ref.py; do
    for sign in all; do
        echo "$script $sign" >> job_list.txt
    done
done

echo "queue job_script, sign from job_list.txt" >> job.sub

