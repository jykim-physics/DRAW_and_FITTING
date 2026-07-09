#!/bin/bash
set -euo pipefail

PYTHON_SCRIPT="./compare_two_sigmc_combined_batch.py"

#SAMPLE1_PLUS_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_gg/260107_loose_v7_less_vars_ntuple/etapip_gg/ref/no_bdt/*BDT.root"
#SAMPLE1_PLUS_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_gg/260602_loose_v7_eta_theta_var/etapip_gg/ref/min_unc_search/0.86/*BDT.root"
#SAMPLE1_PLUS_TREE="etapip_gg"
#SAMPLE1_CC_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_gg_cc/260107_loose_v7_less_vars_ntuple/etapip_gg/ref/no_bdt/*BDT.root"
#SAMPLE1_CC_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_gg_cc/260602_loose_v7_eta_theta_var/etapip_gg/ref/min_unc_search/0.86/*BDT.root"
#SAMPLE1_CC_TREE="etapip_gg"
#SAMPLE1_LABEL="D^{+} #rightarrow #eta_{#gamma#gamma} #pi^{+}"

#SAMPLE2_PLUS_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DptoetaKp_gg/260107_loose_v7_less_vars_ntuple/etapip_gg_K/no_bdt/*BDT.root"
#SAMPLE2_PLUS_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DptoetaKp_gg/260602_loose_v7_eta_theta_var/etapip_gg_K/min_unc_search/0.86/*BDT.root"
#SAMPLE2_PLUS_TREE="etapip_gg_K"
#SAMPLE2_CC_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DptoetaKp_gg_cc/260107_loose_v7_less_vars_ntuple/etapip_gg_K/no_bdt/*BDT.root"
#SAMPLE2_CC_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DptoetaKp_gg_cc/260602_loose_v7_eta_theta_var/etapip_gg_K/min_unc_search/0.86/*BDT.root"
#SAMPLE2_CC_TREE="etapip_gg_K"
#SAMPLE2_LABEL="D^{+} #rightarrow #eta_{#gamma#gamma} K^{+}"

#IMG_PREFIX="./plots/etaKp_gg_versus_etaPip_gg/Dp_Eta_gg"
#IMG_PREFIX="./plots/full_selected_etaKp_gg_versus_etaPip_gg/Dp_Eta_gg"


#SAMPLE1_PLUS_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_pipipi/260107_loose_v7_less_vars_ntuple/etapip_pipipi/ref/no_bdt/*BDT.root"
#SAMPLE1_CC_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_pipipi_cc/260107_loose_v7_less_vars_ntuple/etapip_pipipi/ref/no_bdt/*BDT.root"

SAMPLE1_PLUS_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_pipipi/260602_loose_v7_eta_theta_var/etapip_pipipi/ref/min_unc_search/0.77/*BDT.root"
SAMPLE1_PLUS_TREE="etapip_pipipi"

SAMPLE1_CC_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_pipipi_cc/260602_loose_v7_eta_theta_var/etapip_pipipi/ref/min_unc_search/0.77/*BDT.root"
SAMPLE1_CC_TREE="etapip_pipipi"

SAMPLE1_LABEL="D^{+} #rightarrow #eta_{3#pi} #pi^{+}"

#SAMPLE2_PLUS_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DptoetaKp_pipipi/260107_loose_v7_less_vars_ntuple/etapip_pipipi_K/no_bdt/*BDT.root"
#SAMPLE2_CC_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DptoetaKp_pipipi_cc/260107_loose_v7_less_vars_ntuple/etapip_pipipi_K/no_bdt/*BDT.root"

SAMPLE2_PLUS_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DptoetaKp_pipipi/260602_loose_v7_eta_theta_var/etapip_pipipi_K/min_unc_search/0.77/*BDT.root"
SAMPLE2_PLUS_TREE="etapip_pipipi_K"

SAMPLE2_CC_PATTERN="/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DptoetaKp_pipipi_cc/260602_loose_v7_eta_theta_var/etapip_pipipi_K/min_unc_search/0.77/*BDT.root"
SAMPLE2_CC_TREE="etapip_pipipi_K"

SAMPLE2_LABEL="D^{+} #rightarrow #eta_{3#pi} K^{+}"

#IMG_PREFIX="./plots/etaKp_pipipi_versus_etaPip_pipipi/Dp_Eta_pipipi"
IMG_PREFIX="./plots/full_selected_etaKp_pipipi_versus_etaPip_pipipi/Dp_Eta_pipipi"

mkdir -p "$(dirname "$IMG_PREFIX")"

python3 "$PYTHON_SCRIPT" \
  --sample1-plus-pattern "$SAMPLE1_PLUS_PATTERN" \
  --sample1-plus-tree "$SAMPLE1_PLUS_TREE" \
  --sample1-cc-pattern "$SAMPLE1_CC_PATTERN" \
  --sample1-cc-tree "$SAMPLE1_CC_TREE" \
  --sample1-label "$SAMPLE1_LABEL" \
  --sample2-plus-pattern "$SAMPLE2_PLUS_PATTERN" \
  --sample2-plus-tree "$SAMPLE2_PLUS_TREE" \
  --sample2-cc-pattern "$SAMPLE2_CC_PATTERN" \
  --sample2-cc-tree "$SAMPLE2_CC_TREE" \
  --sample2-label "$SAMPLE2_LABEL" \
  --img-prefix "$IMG_PREFIX" \
  --normalized True
