echo "Processing etapip_gg..."
python3  run_noscale.py  etapip_gg 0.80 2>&1 | tee etapip_gg.out
echo "Processing etapip_pipipi..."
python3  run_noscale.py  etapip_pipipi 0.72 2>&1 | tee etapip_pipipi.out
echo "Processing etapip_gg_K..."
python3  run_noscale.py  etapip_gg_K 0.86 2>&1 | tee etapip_gg_K.out
echo "Processing etapip_pipipi_K..."
python3  run_noscale.py  etapip_pipipi_K 0.77 2>&1 | tee etapip_pipipi_K.out
