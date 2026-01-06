#!/bin/bash

DATA_FNAME="/share/storage/jykim/sweight/proc13/KsKp/gg/proc13_Kspip_gg_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct.root"
MC_FNAME="/share/storage/jykim/sweight/MC15rd/KsKp/gg/MC15rd_Kspip_gg_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct.root"
IMG_PREFIX="./BDT_eff_check/etaKp_gg"
BDT_cut_range=`seq 0.88 0.01 0.96`

DATA_FNAME="/share/storage/jykim/sweight/proc13/KsKp/gg/proc13_Kspip_gg_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct.root"
MC_FNAME="/share/storage/jykim/sweight/MC15rd/KsKp/gg/MC15rd_Kspip_gg_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct_wDpCMSp.root"
IMG_PREFIX="./BDT_eff_check/weighted_etaKp_gg"
BDT_cut_range=`seq 0.88 0.01 0.96`


DATA_FNAME="/share/storage/jykim/sweight/proc13/KsKp/pipipi/proc13_Kspip_pipipi_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct.root"
MC_FNAME="/share/storage/jykim/sweight/MC15rd/KsKp/pipipi/MC15rd_Kspip_pipipi_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct_wDpCMSp.root"
IMG_PREFIX="./BDT_eff_check/etaKp_pipipi"
BDT_cut_range=`seq 0.88 0.01 0.96`

DATA_FNAME="/share/storage/jykim/sweight/proc13/KsKp/pipipi/proc13_Kspip_pipipi_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct.root"
MC_FNAME="/share/storage/jykim/sweight/MC15rd/KsKp/pipipi/MC15rd_Kspip_pipipi_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct.root"
IMG_PREFIX="./BDT_eff_check/weighted_etaKp_pipipi"
BDT_cut_range=`seq 0.88 0.01 0.96`

DATA_FNAME="/share/storage/jykim/sweight/proc13/Kspip/gg/proc13_Kspip_gg_fit_opt_loose_v7_fitv2_Dp_no_bdt_new_Ds_correct.root"
MC_FNAME="/share/storage/jykim/sweight/MC15rd/Kspip/gg/MC15rd_Kspip_gg_fit_opt_loose_v7_fitv2_Dp_no_bdt_new_Ds_correct.root"
IMG_PREFIX="./BDT_eff_check/etapip_gg"
BDT_cut_range=`seq 0.72 0.01 0.76`

DATA_FNAME="/share/storage/jykim/sweight/proc13/Kspip/pipipi/proc13_Kspip_pipipi_fit_opt_loose_v7_fitv2_Dp_no_bdt_new_Ds_correct.root"
MC_FNAME="/share/storage/jykim/sweight/MC15rd/Kspip/pipipi/MC15rd_Kspip_pipipi_fit_opt_loose_v7_fitv2_Dp_no_bdt_new_Ds_correct.root"
IMG_PREFIX="./BDT_eff_check/etapip_pipipi"
BDT_cut_range=`seq 0.81 0.01 0.85`

# Define variables using '|' as a delimiter
VARIABLES=(
  "BDT|0|1.0|BDT|left"
)

NORMALIZED=True
for VAR_INFO in "${VARIABLES[@]}"; do
  IFS="|" read -r VAR_NAME MIN_BIN MAX_BIN DISPLAY_VAR_NAME LEGEND_LOC <<< "$VAR_INFO"

  for BDT_cut in $(seq 0.88 0.01 0.96); do
		echo "=================="
		echo "BDT_cut = ${BDT_cut}"
		python3 BDT_eff_check.v2.py "$DATA_FNAME" "$MC_FNAME" \
    "${IMG_PREFIX}_data_mc_${VAR_NAME}_norm${NORMALIZED}_eff_check.png" \
    "$VAR_NAME" "$MIN_BIN" "$MAX_BIN" "$DISPLAY_VAR_NAME" \
    "$NORMALIZED" "$LEGEND_LOC" \
		"${BDT_cut}" \
    | tee "${IMG_PREFIX}_data_mc_${VAR_NAME}_norm${NORMALIZED}_eff_check_${BDT_cut}.log"
  done
done

