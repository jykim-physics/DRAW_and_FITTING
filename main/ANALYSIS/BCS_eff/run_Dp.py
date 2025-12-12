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

#tree_name = sys.argv[1]
#BDT_cut = sys.argv[2]

base_path = "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC"
tree_name = "etapip_gg"
elements = ["Dptoetapip_gg", "Dptoetapip_gg_cc"]
BDT_cut = 0.91
#BDT_cut = 0.83
#tree_name = "etapip_pipipi"
#elements = ["Dptoetapip_pipipi", "Dptoetapip_pipipi_cc"]
#BDT_cut = 0.74
#BDT_cut = 0.92
#tree_name = "etapip_gg_K"
#elements = ["DptoetaKp_gg", "DptoetaKp_gg_cc"]
#BDT_cut = 0.91
#tree_name = "etapip_pipipi_K"
#elements = ["DptoetaKp_pipipi", "DptoetaKp_pipipi_cc"]
#BDT_cut = 0.92

Dp_M_range = "Dp_M > 0"
#Dp_M_range = "Dp_M > 1.78 and Dp_M < 1.94"

#tree_name = "etapip_gg_K"
#tree_name = "etapip_pipipi"
#BDT_cut = 0.74

file_list = []
if tree_name == "etapip_gg_K" or tree_name == "etapip_pipipi_K":
    for element in elements:
        pattern = f"{base_path}/{element}/250216_loose_v7/{tree_name}/no_BCS/{BDT_cut}/*.no_BCS.root"
        file_list += glob.glob(pattern)
elif tree_name == "etapip_gg" or tree_name == "etapip_pipipi":
    for element in elements:
        pattern = f"{base_path}/{element}/250216_loose_v7/{tree_name}/ref/no_BCS/{BDT_cut}/*.no_BCS.root"
        file_list += glob.glob(pattern)
# Initialize an empty list to hold DataFrames
dataframes = []
branches_all = ["__experiment__", "__run__", "__event__", "__production__",\
             'multiplicity','Dp_isSignal','rank', 'Dp_M', 'Dp_chiProb']
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

df_all = df_all.query(Dp_M_range)

# Rename columns for convenience
df_all = df_all.rename(columns={"Dp_isSignal": "isSignal"})

# Define event ID columns
event_cols = ['__experiment__', '__run__', '__event__', '__production__']

# Total signal events
total_signal = df_all[df_all['isSignal'] == 1][event_cols].drop_duplicates().shape[0]

# 1. Multi-Candidate Event Fraction
multi_cand_events = df_all[df_all['multiplicity'] > 1][event_cols].drop_duplicates()
multi_cand_fraction = 100 * multi_cand_events.shape[0] / df_all[event_cols].drop_duplicates().shape[0]

# 2. Signal Contained in Multi-Candidate Events
#multi_cand_signals = df_all[(df_all['multiplicity'] > 1) & (df_all['isSignal'] == 1)][event_cols].drop_duplicates()
multi_cand_signals = len(
    df_all[df_all["multiplicity"] > 1]
    .groupby(event_cols)
    .filter(lambda x: (x["isSignal"] == 1).any())
    .drop_duplicates(subset=event_cols)
)
#signal_in_multi_fraction = 100 * multi_cand_signals.shape[0] / total_signal
signal_in_multi_fraction = 100 * multi_cand_signals / multi_cand_events.shape[0]

# 3. Signal Chosen Among Multi-Cands (rank==1 in multi-cand + signal)
chosen_signals = df_all[(df_all['multiplicity'] > 1) & (df_all['isSignal'] == 1) & (df_all['rank'] == 1)]
chosen_signal_fraction = 100 * chosen_signals[event_cols].drop_duplicates().shape[0] / multi_cand_signals

# 4. Overall BCS Efficiency (rank==1 in any signal)
overall_bcs_eff = 100 * df_all[(df_all['isSignal'] == 1) & (df_all['rank'] == 1)][event_cols].drop_duplicates().shape[0] / total_signal

# Print nicely
print("=== BCS Performance Metrics ===")
print(f"1. Multi-Candidate Event Fraction (%)       : {multi_cand_fraction:.2f}")
print(f"2. Signal Contained in Multi-Cands (%)      : {signal_in_multi_fraction:.2f}")
print(f"3. Signal Chosen Among Multi-Cands (%)      : {chosen_signal_fraction:.2f}")
print(f"4. Overall BCS Efficiency (%)               : {overall_bcs_eff:.2f}")

