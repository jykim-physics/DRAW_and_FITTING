#!/bin/bash

DATA_A_FNAME="/share/storage/jykim/sweight/proc13/KsKp/gg/proc13_Kspip_gg_K_fit_opt_loose_v7_fitv3_Dpregion_no_bdt.root"
MC_A_FNAME="/share/storage/jykim/sweight/MC15rd/KsKp/gg/MC15rd_Kspip_gg_K_fit_opt_loose_v7_fitv3_Dpregion_no_bdt.root"
DATA_B_FNAME="/share/storage/jykim/sweight/proc13/Kspip/gg/proc13_Kspip_gg_fit_opt_loose_v7_fitv3_Dp_no_bdt_etapip_gg_K_BDT.root"
MC_B_FNAME="/share/storage/jykim/sweight/MC15rd/Kspip/gg/MC15rd_Kspip_gg_fit_opt_loose_v7_fitv3_Dp_no_bdt_etapip_gg_K_BDT.root"
IMG_PREFIX="./plots/BDT_eff_compare/Dp_etaKp_gg_Dp_KsKp"

#DATA_A_FNAME="/share/storage/jykim/sweight/proc13/KsKp/pipipi/proc13_Kspip_pipipi_K_fit_opt_loose_v7_fitv3_Dpregion_no_bdt.root"
#MC_A_FNAME="/share/storage/jykim/sweight/MC15rd/KsKp/pipipi/MC15rd_Kspip_pipipi_K_fit_opt_loose_v7_fitv3_Dpregion_no_bdt.root"
#DATA_B_FNAME="/share/storage/jykim/sweight/proc13/Kspip/pipipi/proc13_Kspip_pipipi_fit_opt_loose_v7_fitv3_Dp_no_bdt_etapip_pipipi_K_BDT.root"
#MC_B_FNAME="/share/storage/jykim/sweight/MC15rd/Kspip/pipipi/MC15rd_Kspip_pipipi_fit_opt_loose_v7_fitv3_Dp_no_bdt_etapip_pipipi_K_BDT.root"
#IMG_PREFIX="./plots/BDT_eff_compare/Dp_etaKp_pipipi_Dp_KsKp"

# Define variables using '|' as a delimiter
VARIABLES=(
  #"BDT|0|1.0|BDT|left|False"
  #"Dp_cosHelicityAngleMomentum|-1|1|cosHel(D^{+}_{(s)})|right|False"
	#"etapip_Eta_Easym|0|1|abs((E_{#gamma_{1}} - E_{#gamma_{2}}) /(E_{#gamma_{1}} + E_{#gamma_{2}}))|right|False"
  #"Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane|-1|1|cos#theta_{XY}|right|True"
  #"Dp_dz|-0.2|0.4|dz(D^{+}_{(s)})|right|False"
  "Pip_dr|0|0.1|dr(h^{+})|right|False"
  #"Dp_CMS_p|2.5|5.2|p^{*}(D^{+}_{(s)})|right|False"
)

for VAR_INFO in "${VARIABLES[@]}"; do
  IFS="|" read -r VAR_NAME MIN_BIN MAX_BIN DISPLAY_VAR_NAME LEGEND_LOC IS_LOGSCALE <<< "$VAR_INFO"

  for NORMALIZED in True False; do
    python3 compare_sweighted_signal_data_mc_4.py "$DATA_A_FNAME" "$DATA_B_FNAME" "$MC_A_FNAME" "$MC_B_FNAME" "${IMG_PREFIX}_data_mc_${VAR_NAME}_ratio_norm${NORMALIZED}.png" "$VAR_NAME" "$MIN_BIN" "$MAX_BIN" "$DISPLAY_VAR_NAME" "$NORMALIZED" "$LEGEND_LOC" "$IS_LOGSCALE"
  done
done

