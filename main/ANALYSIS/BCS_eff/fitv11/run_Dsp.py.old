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
elements = ["Dsptoetapip_gg", "Dsptoetapip_gg_cc"]
BDT_cut = 0.83

Dp_M_range = "Dp_M > 0"
signal_cut = "(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & ((Pip_genMotherPDG == 431 and Pip_mcPDG == 211) | (Pip_genMotherPDG == -431 and Pip_mcPDG == -211) )"


file_list = []
for element in elements:
    pattern = f"{base_path}/{element}/250216_loose_v7/{tree_name}/no_BCS/{BDT_cut}/weighted/*.no_BCS.root"
    file_list += glob.glob(pattern)
# Initialize an empty list to hold DataFrames
dataframes = []
branches_all = ["__experiment__", "__run__", "__event__", "__production__",\
             'multiplicity','Dp_isSignal','rank', 'Dp_M', 'etapip_Eta_genMotherPDG','etapip_Eta_genMotherID', 'Pip_mcPDG', 'Pip_genMotherPDG','Pip_genMotherID', 'etapip_Eta_isSignal', "ds_weight"]
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

# Define event columns
event_cols = ['__experiment__', '__run__', '__event__', '__production__']

# Apply signal definition
df_all['isTrueSignal'] = df_all.eval(signal_cut)

# Drop duplicate events for global event count
all_events = df_all.drop_duplicates(subset=event_cols)
multi_cand_events = df_all[df_all['multiplicity'] > 1].drop_duplicates(subset=event_cols)

signal_events = df_all[df_all['isTrueSignal']].drop_duplicates(subset=event_cols)
multi_cand_signal_events = df_all[(df_all['isTrueSignal']) & (df_all['multiplicity'] > 1)].drop_duplicates(subset=event_cols)

chosen_signals = df_all[(df_all['isTrueSignal']) & (df_all['multiplicity'] > 1) & (df_all['rank'] == 1)].drop_duplicates(subset=event_cols)
chosen_signal_events = df_all[(df_all['isTrueSignal']) & (df_all['rank'] == 1)].drop_duplicates(subset=event_cols)

# 1. Multi-Candidate Event Fraction (weighted)
multi_cand_fraction = 100 * multi_cand_events['ds_weight'].sum() / all_events['ds_weight'].sum()

# 2. Signal Contained in Multi-Candidate Events (weighted)
signal_in_multi_fraction = 100 * multi_cand_signal_events['ds_weight'].sum() / multi_cand_events['ds_weight'].sum()

# 3. Signal Chosen Among Multi-Cands (rank == 1, weighted)
chosen_signal_fraction = 100 * chosen_signals['ds_weight'].sum() / multi_cand_signal_events['ds_weight'].sum()

# 4. Overall BCS Efficiency (rank == 1 in any signal, weighted)
overall_bcs_eff = 100 * chosen_signal_events['ds_weight'].sum() / signal_events['ds_weight'].sum()

# Print results
print("=== Weighted BCS Performance Metrics ===")
print(f"1. Multi-Candidate Event Fraction (%)       : {multi_cand_fraction:.2f}")
print(f"2. Signal Contained in Multi-Cands (%)      : {signal_in_multi_fraction:.2f}")
print(f"3. Signal Chosen Among Multi-Cands (%)      : {chosen_signal_fraction:.2f}")
print(f"4. Overall BCS Efficiency (%)               : {overall_bcs_eff:.2f}")

"""


# Apply signal definition
df_all['isTrueSignal'] = df_all.eval(signal_cut)

# Group by unique events
event_cols = ['__experiment__', '__run__', '__event__', '__production__']
df_all['event_id'] = df_all[event_cols].astype(str).agg('_'.join, axis=1)

# 1. Multi-Candidate Event Fraction (weighted)
all_events = df_all.drop_duplicates('event_id')
multi_cand_events = df_all[df_all['multiplicity'] > 1].drop_duplicates('event_id')
multi_cand_fraction = 100 * multi_cand_events['ds_weight'].sum() / all_events['ds_weight'].sum()

# 2. Signal Contained in Multi-Candidate Events (weighted)
signal_events = df_all[df_all['isTrueSignal']]
multi_cand_signal_events = signal_events[signal_events['multiplicity'] > 1].drop_duplicates('event_id')
signal_in_multi_fraction = 100 * multi_cand_signal_events['ds_weight'].sum() / multi_cand_events['ds_weight'].sum()

# 3. Signal Chosen Among Multi-Cands (rank == 1, weighted)
chosen_signals = multi_cand_signal_events[multi_cand_signal_events['rank'] == 1]
chosen_signal_fraction = 100 * chosen_signals['ds_weight'].sum() / multi_cand_signal_events['ds_weight'].sum()

# 4. Overall BCS Efficiency (rank == 1 in any signal, weighted)
unique_signal_events = signal_events.drop_duplicates('event_id')
chosen_signal_events = signal_events[signal_events['rank'] == 1].drop_duplicates('event_id')
overall_bcs_eff = 100 * chosen_signal_events['ds_weight'].sum() / unique_signal_events['ds_weight'].sum()

# Print results
print("=== Weighted BCS Performance Metrics ===")
print(f"1. Multi-Candidate Event Fraction (%)       : {multi_cand_fraction:.2f}")
print(f"2. Signal Contained in Multi-Cands (%)      : {signal_in_multi_fraction:.2f}")
print(f"3. Signal Chosen Among Multi-Cands (%)      : {chosen_signal_fraction:.2f}")
print(f"4. Overall BCS Efficiency (%)               : {overall_bcs_eff:.2f}")
"""

'''

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
multi_cand_signals = df_all[(df_all['multiplicity'] > 1) & (df_all['isSignal'] == 1)][event_cols].drop_duplicates()
signal_in_multi_fraction = 100 * multi_cand_signals.shape[0] / multi_cand_events.shape[0]

# 3. Signal Chosen Among Multi-Cands (rank==1 in multi-cand + signal)
chosen_signals = df_all[(df_all['multiplicity'] > 1) & (df_all['isSignal'] == 1) & (df_all['rank'] == 1)]
chosen_signal_fraction = 100 * chosen_signals[event_cols].drop_duplicates().shape[0] / multi_cand_signals.shape[0]

# 4. Overall BCS Efficiency (rank==1 in any signal)
overall_bcs_eff = 100 * df_all[(df_all['isSignal'] == 1) & (df_all['rank'] == 1)][event_cols].drop_duplicates().shape[0] / total_signal

# Print nicely
print("=== BCS Performance Metrics ===")
print(f"1. Multi-Candidate Event Fraction (%)       : {multi_cand_fraction:.2f}")
print(f"2. Signal Contained in Multi-Cands (%)      : {signal_in_multi_fraction:.2f}")
print(f"3. Signal Chosen Among Multi-Cands (%)      : {chosen_signal_fraction:.2f}")
print(f"4. Overall BCS Efficiency (%)               : {overall_bcs_eff:.2f}")

tree_name = "etapip_pipipi"
elements = ["Dsptoetapip_pipipi", "Dsptoetapip_pipipi_cc"]
BDT_cut = 0.74
tree_name = "etapip_gg_K"
elements = ["DsptoetaKp_gg", "DsptoetaKp_gg_cc"]
BDT_cut = 0.91
tree_name = "etapip_pipipi_K"
elements = ["DsptoetaKp_pipipi", "DsptoetaKp_pipipi_cc"]
BDT_cut = 0.92
'''
