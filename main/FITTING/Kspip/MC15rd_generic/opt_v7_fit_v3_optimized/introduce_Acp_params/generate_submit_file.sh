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
arguments            = \$(job_script) \$(sign) \$(float_var)
" > job.sub

rm -f job_list.txt

#for script in Kspip_offset_etapip_gg.py Kspip_offset_etapip_pipipi.py; do
for script in KsKp_offset_etapip_gg_Ds.py KsKp_offset_etapip_pipipi_Ds.py Kspip_offset_etapip_gg.py Kspip_offset_etapip_pipipi.py; do
    for sign in plus minus; do
        for param in mean sigma gamma delta sigma_gauss x_bkg1_tau; do
            echo "$script $sign $param" >> job_list.txt
        done
    done
done

echo "queue job_script, sign, float_var from job_list.txt" >> job.sub

