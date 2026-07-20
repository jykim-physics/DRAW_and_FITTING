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
#for script in KsKp_offset_etapip_gg_Ds.py KsKp_offset_etapip_pipipi_Ds.py Kspip_offset_etapip_gg.py Kspip_offset_etapip_pipipi.py; do
#for script in KsKp_offset_etapip_gg_Ds.py; do
for script in KsKp_offset_etapip_pipipi_Ds.py Kspip_offset_etapip_pipipi.py; do
    echo "$script a " >> job_list.txt
    echo "$script b " >> job_list.txt
    echo "$script c " >> job_list.txt
    echo "$script d " >> job_list.txt
    echo "$script e " >> job_list.txt
    echo "$script f " >> job_list.txt
done

echo "queue job_script, sign from job_list.txt" >> job.sub
