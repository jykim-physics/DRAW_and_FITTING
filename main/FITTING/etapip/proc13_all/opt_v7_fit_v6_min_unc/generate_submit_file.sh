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

for script in etapip_gg_offset_novo_CB.py etapip_pipipi_offset_novo_CB.py; do
#for script in etapip_gg_offset_novo_CB.py; do
#for script in etapip_pipipi_offset_novo_CB.py; do
    for value in $(seq 0.61 0.01 0.90); do
    #for value in $(seq 0.79 0.01 0.90); do
        echo "$script all $value" >> job_list.txt
    done
done

#for script in etapip_gg_K_offset_CB.py etapip_pipipi_K_offset_CB.py; do
#for script in etapip_gg_K_offset_CB.py; do
#    for value in $(seq 0.70 0.01 0.99); do
#        echo "$script all $value" >> job_list.txt
#    done
#done

echo "queue job_script, sign, bdt from job_list.txt" >> job.sub
