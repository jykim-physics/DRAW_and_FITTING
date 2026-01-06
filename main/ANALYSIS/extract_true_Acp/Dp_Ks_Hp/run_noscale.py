import uproot
import pandas as pd
import numpy as np
import glob

import matplotlib.pyplot as plt
plt.style.use('default')
plt.style.use('belle2')

import os
import glob
import sys

tree_name = sys.argv[1] #Ks
BDT_cut = sys.argv[2] #0.83
ref_tree = sys.argv[3]#etapip_gg

if tree_name == "Ks_K":
    Dsp_cut = "(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & ((Pip_genMotherPDG == 431 and Pip_mcPDG == 321) | (Pip_genMotherPDG == -431 and Pip_mcPDG == -321) )"
elif tree_name == "Ks":
    Dsp_cut = "(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & ((Pip_genMotherPDG == 431 and Pip_mcPDG == 211) | (Pip_genMotherPDG == -431 and Pip_mcPDG == -211) )"

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/Kspip/MC15rd_Kspip_loose_v7_1_250228_Dp_CMS_p_v3"
cm_elements = ["MCrd_Ks_e7_18_4S_v3", "MCrd_Ks_e20_b26_v1", "MCrd_Ks_e20_e26_4S_v2", "MCrd_Ks_e21_5S_scan_v1", "MCrd_Ks_mori_off_v1"]

#ref_tree = "etapip_gg"
file_list = []
#tree_name = "Ks"
for element in cm_elements:
    #pattern = f"{base_path}/{element}/{ref_tree}/{tree_name}/*.BCS.root"
    if tree_name == "Ks_K":
        pattern = f"{base_path}/{element}/{ref_tree}/{tree_name}/{BDT_cut}/weighted/*.BCS.root"
    elif tree_name == "Ks":
        pattern = f"{base_path}/{element}/{ref_tree}/{tree_name}/{BDT_cut}/*.BCS.root"
    file_list += glob.glob(pattern)

# Initialize an empty list to hold DataFrames
dataframes = []
branches_all = ["__experiment__", "__run__", "__event__",\
             'Dp_M','Dp_isSignal','Dp_CMS_cosTheta',\
             'etapip_Eta_M','etapip_Eta_isSignal',\
             'etapip_Eta_genMotherPDG','etapip_Eta_genMotherID',\
             'Pip_mcPDG',\
             'Pip_genMotherPDG','Pip_genMotherID', "Pip_charge"]
if tree_name == "Ks_K":
	branches_all += ["ds_weight"]
# Process each file
for file_name in file_list:
    # Load the ROOT file and tree
    file = uproot.open(file_name)
    tree = file[tree_name]

    # Convert the selected branches to a Pandas DataFrame
    df_temp = tree.arrays(branches_all, library="pd")

    # Append the DataFrame to the list
    dataframes.append(df_temp)

df_all = pd.concat(dataframes, ignore_index=True)

df_all = df_all.query("Dp_M > 1.80 and Dp_M < 2.03")

df_Dp_signal = df_all.query("Dp_isSignal==1").copy()
#df_Dsp_signal = df_all.query("(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & ((Pip_genMotherPDG == 431 and Pip_mcPDG == 321) | (Pip_genMotherPDG == -431 and Pip_mcPDG == -321) )").copy()
#df_Dsp_signal = df_all.query("(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & ((Pip_genMotherPDG == 431 and Pip_mcPDG == 211) | (Pip_genMotherPDG == -431 and Pip_mcPDG == -211) )").copy()
df_Dsp_signal = df_all.query(Dsp_cut).copy()

#nan_columns = df_all.isnull().any()
#print(nan_columns)

def calc_acp_with_weights(df, weight_column=None, global_scale=1):
    if weight_column:
        df["__weight__"] = df[weight_column] * global_scale
    else:
        df["__weight__"] = global_scale

    df_plus = df.query("Pip_charge == 1")
    df_minus = df.query("Pip_charge == -1")

    n_plus = df_plus["__weight__"].sum()
    n_minus = df_minus["__weight__"].sum()

    # Errors: sqrt(sum w^2)
    err_plus = np.sqrt((df_plus["__weight__"] ** 2).sum())
    err_minus = np.sqrt((df_minus["__weight__"] ** 2).sum())

    total = n_plus + n_minus
    acp = (n_plus - n_minus) / total if total > 0 else 0.

    # Error propagation
    dAcp_dplus = 2 * n_minus / total**2
    dAcp_dminus = 2 * n_plus / total**2
    err_acp = np.sqrt((dAcp_dplus * err_plus)**2 + (dAcp_dminus * err_minus)**2)

    return acp * 100, err_acp * 100, n_plus, n_minus, err_plus, err_minus  # in percent

# Calculate
#acp_Dp, err_Dp, nplus_Dp, nminus_Dp, errplus_Dp, errminus_Dp = calc_acp_with_weights(df_Dp_signal)
#acp_Dsp, err_Dsp, nplus_Dsp, nminus_Dsp, errplus_Dsp, errminus_Dsp = calc_acp_with_weights(df_Dsp_signal, weight_column="ds_weight")

# Print results
#print("=== A_CP Summary (weights applied, error from sqrt(N)) ===")
#print(f"D+  : A_CP = {acp_Dp:.4f} ± {err_Dp:.4f} %, N+ = {nplus_Dp:.4f} ± {errplus_Dp:.4f}, N- = {nminus_Dp:.4f} ± {errminus_Dp:.4f}")
#print(f"D_s+: A_CP = {acp_Dsp:.4f} ± {err_Dsp:.4f} %, N+ = {nplus_Dsp:.4f} ± {errplus_Dsp:.4f}, N- = {nminus_Dsp:.4f} ± {errminus_Dsp:.4f}")


def calc_acp_cosTheta_symmetric(df, cosTheta_var="Dp_CMS_cosTheta", weight_column=None, global_scale=1):
    # Subset for positive and negative cosTheta
    df_pos = df.query(f"{cosTheta_var} > 0").copy()
    df_neg = df.query(f"{cosTheta_var} < 0").copy()

    # Compute A_CP for each region
    acp_pos, err_pos, nplus_pos, nminus_pos, errplus_pos, errminus_pos = calc_acp_with_weights(df_pos, weight_column, global_scale)
    acp_neg, err_neg, nplus_neg, nminus_neg, errplus_neg, errminus_neg = calc_acp_with_weights(df_neg, weight_column, global_scale)

    # Symmetrized combination
    acp_sym = (acp_pos + acp_neg) / 2
    err_sym = np.sqrt(err_pos**2 + err_neg**2) / 2  # assuming uncorrelated

    return {
        "acp_sym": acp_sym,
        "err_sym": err_sym,
        "acp_pos": acp_pos,
        "err_pos": err_pos,
        "acp_neg": acp_neg,
        "err_neg": err_neg,
        "nplus_pos": nplus_pos,
        "nminus_pos": nminus_pos,
        "nplus_neg": nplus_neg,
        "nminus_neg": nminus_neg
    }

if tree_name == "Ks":
    res_Dp = calc_acp_cosTheta_symmetric(df_Dp_signal)
    print("=== Symmetrized A_CP using cosθ separation ===")
    print(f"D+ : A'_CP = {res_Dp['acp_sym']:.4f} ± {res_Dp['err_sym']:.4f} %")
    print(f"  cosθ>0  : A_CP = {res_Dp['acp_pos']:.4f} ± {res_Dp['err_pos']:.4f} %, N+ = {res_Dp['nplus_pos']:.4f}, N- = {res_Dp['nminus_pos']:.4f}")
    print(f"  cosθ<0  : A_CP = {res_Dp['acp_neg']:.4f} ± {res_Dp['err_neg']:.4f} %, N+ = {res_Dp['nplus_neg']:.4f}, N- = {res_Dp['nminus_neg']:.4f}")
elif tree_name == "Ks_K":
  res_Dsp = calc_acp_cosTheta_symmetric(df_Dsp_signal, weight_column="ds_weight")
  print(f"D_s+: A'_CP = {res_Dsp['acp_sym']:.4f} ± {res_Dsp['err_sym']:.4f} %")
  print(f"    cosθ>0  : A_CP = {res_Dsp['acp_pos']:.4f} ± {res_Dsp['err_pos']:.4f} %, N+ = {res_Dsp['nplus_pos']:.4f}, N- = {res_Dsp['nminus_pos']:.4f}")
  print(f"    cosθ<0  : A_CP = {res_Dsp['acp_neg']:.4f} ± {res_Dsp['err_neg']:.4f} %, N+ = {res_Dsp['nplus_neg']:.4f}, N- = {res_Dsp['nminus_neg']:.4f}")

