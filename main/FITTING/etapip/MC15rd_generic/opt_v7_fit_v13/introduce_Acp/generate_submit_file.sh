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

: "
for script in etapip_gg_K_offset_CB.py; do
    for sign in plus minus; do
        for param in mean scale_factor Ds_mean x_bkg1_c1 x_bkg1_c2; do
            echo "$script $sign $param" >> job_list.txt
        done
    done
done
"
for script in etapip_pipipi_K_offset_CB.py; do
    for sign in plus minus; do
        #for param in mean scale_factor Ds_mean x_bkg1_c1 x_bkg1_c2; do
        for param in x_bkg1_c1 x_bkg1_c2; do
            echo "$script $sign $param" >> job_list.txt
        done
    done
done


echo "queue job_script, sign, float_var from job_list.txt" >> job.sub

