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
arguments            = \$(job_script) \$(sign) \$(syst)
" > job.sub

rm -f job_list.txt

for script in etapip_gg_K.py etapip_pipipi_K.py; do
    for sign in plus minus all; do
        for param in plus minus; do
            echo "$script $sign $param" >> job_list.txt
        done
    done
done


echo "queue job_script, sign, syst from job_list.txt" >> job.sub

