echo "Processing etapip_gg..."
python3  run_noscale.py Ks 0.80 etapip_gg 2>&1 | tee etapip_gg.out
echo "Processing etapip_pipipi..."
python3  run_noscale.py Ks 0.72 etapip_pipipi 2>&1 | tee etapip_pipipi.out
echo "Processing etapip_gg_K..."
python3  run_noscale.py Ks_K 0.86 etapip_gg_K 2>&1 | tee etapip_gg_K.out
echo "Processing etapip_pipipi_K..."
python3  run_noscale.py Ks_K 0.77 etapip_pipipi_K 2>&1 | tee etapip_pipipi_K.out
