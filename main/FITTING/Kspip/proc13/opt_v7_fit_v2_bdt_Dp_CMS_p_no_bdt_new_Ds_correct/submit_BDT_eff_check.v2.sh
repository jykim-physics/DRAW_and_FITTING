#!/bin/bash

# ==========================================
# 1. Define the Function
# ==========================================
run_bdt_check() {
    local DATA_FNAME="$1"
    local MC_FNAME="$2"
    local IMG_PREFIX="$3"
    local BDT_START="$4"
    local BDT_STEP="$5"
    local BDT_END="$6"

    # Define variables using '|' as a delimiter (Global to the function)
    local VARIABLES=(
      "BDT|0|1.0|BDT|left"
    )
    local NORMALIZED=True

    echo "------------------------------------------------------"
    echo "Processing: $IMG_PREFIX"
    echo "Range: $BDT_START to $BDT_END (Step: $BDT_STEP)"
    echo "------------------------------------------------------"

    for VAR_INFO in "${VARIABLES[@]}"; do
        IFS="|" read -r VAR_NAME MIN_BIN MAX_BIN DISPLAY_VAR_NAME LEGEND_LOC <<< "$VAR_INFO"

        # Loop through the sequence of BDT cuts
        for BDT_cut in $(seq "$BDT_START" "$BDT_STEP" "$BDT_END"); do
            echo "  > Running BDT_cut = ${BDT_cut}"

            # Ensure the directory exists for logs/images
            mkdir -p "$(dirname "${IMG_PREFIX}")"

            # Execute Python Script
            # Note: Removed trailing spaces after backslashes needed for line continuation
            python3 BDT_eff_check.v2.py "$DATA_FNAME" "$MC_FNAME" \
            "${IMG_PREFIX}_data_mc_${VAR_NAME}_norm${NORMALIZED}_eff_check.png" \
            "$VAR_NAME" "$MIN_BIN" "$MAX_BIN" "$DISPLAY_VAR_NAME" \
            "$NORMALIZED" "$LEGEND_LOC" \
            "${BDT_cut}" \
            | tee "${IMG_PREFIX}_data_mc_${VAR_NAME}_norm${NORMALIZED}_eff_check_${BDT_cut}.log"
        done
    done
}

# ==========================================
# 2. Execute Function for each Configuration
# ==========================================

# --- Config 1: KsKp gg (Standard) ---
run_bdt_check \
    "/share/storage/jykim/sweight/proc13/KsKp/gg/proc13_Kspip_gg_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct.root" \
    "/share/storage/jykim/sweight/MC15rd/KsKp/gg/MC15rd_Kspip_gg_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct.root" \
    "./BDT_eff_check/etaKp_gg" \
    0.88 0.01 0.96

# --- Config 2: KsKp gg (Weighted / wDpCMSp) ---
run_bdt_check \
    "/share/storage/jykim/sweight/proc13/KsKp/gg/proc13_Kspip_gg_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct.root" \
    "/share/storage/jykim/sweight/MC15rd/KsKp/gg/MC15rd_Kspip_gg_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct_wDpCMSp.root" \
    "./BDT_eff_check/weighted_etaKp_gg" \
    0.88 0.01 0.96

# --- Config 3: KsKp pipipi (Standard) ---
run_bdt_check \
    "/share/storage/jykim/sweight/proc13/KsKp/pipipi/proc13_Kspip_pipipi_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct.root" \
    "/share/storage/jykim/sweight/MC15rd/KsKp/pipipi/MC15rd_Kspip_pipipi_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct.root" \
    "./BDT_eff_check/etaKp_pipipi" \
    0.88 0.01 0.96

# --- Config 4: KsKp pipipi (Weighted) ---
run_bdt_check \
    "/share/storage/jykim/sweight/proc13/KsKp/pipipi/proc13_Kspip_pipipi_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct.root" \
    "/share/storage/jykim/sweight/MC15rd/KsKp/pipipi/MC15rd_Kspip_pipipi_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct_wDpCMSp.root" \
    "./BDT_eff_check/weighted_etaKp_pipipi" \
    0.88 0.01 0.96

# --- Config 5: Kspip gg ---
# Note: Different BDT Range (0.72 - 0.76)
run_bdt_check \
    "/share/storage/jykim/sweight/proc13/Kspip/gg/proc13_Kspip_gg_fit_opt_loose_v7_fitv2_Dp_no_bdt_new_Ds_correct.root" \
    "/share/storage/jykim/sweight/MC15rd/Kspip/gg/MC15rd_Kspip_gg_fit_opt_loose_v7_fitv2_Dp_no_bdt_new_Ds_correct.root" \
    "./BDT_eff_check/etapip_gg" \
    0.81 0.01 0.85

# --- Config 6: Kspip pipipi ---
# Note: Different BDT Range (0.81 - 0.85)
run_bdt_check \
    "/share/storage/jykim/sweight/proc13/Kspip/pipipi/proc13_Kspip_pipipi_fit_opt_loose_v7_fitv2_Dp_no_bdt_new_Ds_correct.root" \
    "/share/storage/jykim/sweight/MC15rd/Kspip/pipipi/MC15rd_Kspip_pipipi_fit_opt_loose_v7_fitv2_Dp_no_bdt_new_Ds_correct.root" \
    "./BDT_eff_check/etapip_pipipi" \
    0.72 0.01 0.76
