# Define your modes
modes=("etapip_gg" "etapip_pipipi" "etapip_gg_K" "etapip_pipipi_K")

for mode in "${modes[@]}"; do
    echo "Processing $mode..."
    #python3 run_Dp_BDT.py "$mode" 2>&1 | tee "${mode}_BDT.out"
    #python3 run_Dp_chiProb.py "$mode" 2>&1 | tee "${mode}_chiProb.out"
    #python3 run_Dsp_chiProb.py "$mode" 2>&1 | tee "${mode}_chiProb_Dsp.out"
    python3 run_Dsp_BDT.py "$mode" 2>&1 | tee "${mode}_BDT_Dsp.out"
done
