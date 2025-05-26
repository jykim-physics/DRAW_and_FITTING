#!/bin/bash

DATA_FNAME="/share/storage/jykim/sweight/proc13/KsKp/gg/proc13_Kspip_gg_K_fit_opt_loose_v7_fitv1_Ds_no_bdt_new_Ds.root"
#MC_FNAME="/share/storage/jykim/sweight/MC15rd/KsKp/gg/MC15rd_Kspip_gg_K_fit_opt_loose_v7_fitv1_Ds_no_bdt_new_Ds.root"
MC_FNAME="/share/storage/jykim/sweight/MC15rd/KsKp/gg/MC15rd_Kspip_gg_K_fit_opt_loose_v7_fitv1_Ds_no_bdt_new_Ds_wDpCMSp.root"
#IMG_PREFIX="./plots/etaKp_gg"
IMG_PREFIX="./weighted_plots/etaKp_gg"

#DATA_FNAME="/share/storage/jykim/sweight/proc13/KsKp/gg/proc13_Kspip_gg_K_fit_opt_loose_v7_fitv1_Dp_no_bdt.root"
#MC_FNAME="/share/storage/jykim/sweight/MC15rd/KsKp/gg/MC15rd_Kspip_gg_K_fit_opt_loose_v7_fitv1_Dp_no_bdt.root"
#IMG_PREFIX="./plots/Dp_etaKp_gg"

#DATA_FNAME="/share/storage/jykim/sweight/proc13/KsKp/pipipi/proc13_Kspip_pipipi_K_fit_opt_loose_v7_fitv1_Ds_no_bdt_new_Ds.root"
#MC_FNAME="/share/storage/jykim/sweight/MC15rd/KsKp/pipipi/MC15rd_Kspip_pipipi_K_fit_opt_loose_v7_fitv1_Ds_no_bdt_new_Ds.root"
#MC_FNAME="/share/storage/jykim/sweight/MC15rd/KsKp/pipipi/MC15rd_Kspip_pipipi_K_fit_opt_loose_v7_fitv1_Ds_no_bdt_new_Ds_wDpCMSp.root"
#IMG_PREFIX="./plots/etaKp_pipipi"
#IMG_PREFIX="./weighted_plots/etaKp_pipipi"

#DATA_FNAME="/share/storage/jykim/sweight/proc13/KsKp/pipipi/proc13_Kspip_pipipi_K_fit_opt_loose_v7_fitv1_Dp_no_bdt.root"
#MC_FNAME="/share/storage/jykim/sweight/MC15rd/KsKp/pipipi/MC15rd_Kspip_pipipi_K_fit_opt_loose_v7_fitv1_Dp_no_bdt.root"
#IMG_PREFIX="./plots/Dp_etaKp_pipipi"

#DATA_FNAME="/share/storage/jykim/sweight/proc13/Kspip/gg/proc13_Kspip_gg_fit_opt_loose_v7_fitv1_Dp_no_bdt_new_Ds.root"
#MC_FNAME="/share/storage/jykim/sweight/MC15rd/Kspip/gg/MC15rd_Kspip_gg_fit_opt_loose_v7_fitv1_Dp_no_bdt_new_Ds.root"
#IMG_PREFIX="./plots/etapip_gg"

#DATA_FNAME="/share/storage/jykim/sweight/proc13/Kspip/pipipi/proc13_Kspip_pipipi_fit_opt_loose_v7_fitv1_Dp_no_bdt_new_Ds.root"
#MC_FNAME="/share/storage/jykim/sweight/MC15rd/Kspip/pipipi/MC15rd_Kspip_pipipi_fit_opt_loose_v7_fitv1_Dp_no_bdt_new_Ds.root"
#IMG_PREFIX="./plots/etapip_pipipi"

# Define variables using '|' as a delimiter
VARIABLES=(
  "BDT|0|1.0|BDT|left"
  "Dp_cosHelicityAngleMomentum|-1|1|cosHel(D^{+}_{(s)})|right"
	"etapip_Eta_Easym|0|1|abs((E_{#gamma_{1}} - E_{#gamma_{2}}) /(E_{#gamma_{1}} + E_{#gamma_{2}}))|right"
  "Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane|-1|1|cos#theta_{XY}|right"
  "Dp_dz|-0.2|0.4|dz(D^{+}_{(s)})|right"
  "Pip_dr|0|0.1|dr(#pi^{+})|right"
  "Dp_CMS_p|2.5|5.2|p^{*}(D^{+}_{(s)})|right"
)

for VAR_INFO in "${VARIABLES[@]}"; do
  IFS="|" read -r VAR_NAME MIN_BIN MAX_BIN DISPLAY_VAR_NAME LEGEND_LOC <<< "$VAR_INFO"

  for NORMALIZED in True False; do
    python3 compare_sweighted_signal_data_mc.py "$DATA_FNAME" "$MC_FNAME" "${IMG_PREFIX}_data_mc_${VAR_NAME}_norm${NORMALIZED}.png" "$VAR_NAME" "$MIN_BIN" "$MAX_BIN" "$DISPLAY_VAR_NAME" "$NORMALIZED" "$LEGEND_LOC"
    python3 compare_sweighted_signal_data_mc_ratio.py "$DATA_FNAME" "$MC_FNAME" "${IMG_PREFIX}_data_mc_${VAR_NAME}_ratio_norm${NORMALIZED}.png" "$VAR_NAME" "$MIN_BIN" "$MAX_BIN" "$DISPLAY_VAR_NAME" "$NORMALIZED" "$LEGEND_LOC"
  done
done

