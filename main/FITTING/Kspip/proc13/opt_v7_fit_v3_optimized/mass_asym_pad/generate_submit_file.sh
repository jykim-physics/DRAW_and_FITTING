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

for script in  KsKp_offset_etapip_gg_Ds.py KsKp_offset_etapip_pipipi_Ds.py Kspip_offset_etapip_gg.py Kspip_offset_etapip_pipipi.py; do
#for script in   Kspip_offset_etapip_gg.py Kspip_offset_etapip_pipipi.py; do
	echo "$script plus" >> job_list.txt
	echo "$script minus" >> job_list.txt
done


echo "queue job_script, sign, bdt from job_list.txt" >> job.sub
