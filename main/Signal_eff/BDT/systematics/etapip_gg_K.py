import uproot
import pandas as pd
import numpy as np
import glob
import seaborn as sns

import matplotlib.pyplot as plt
plt.style.use('default')
plt.style.use('belle2')

import os
import glob
import joblib
overall_version = "v7_xgboost_angle_cut"
base_path_sig = "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC"
#sig_MC_name = "250122_loose_v7"
sig_MC_name = "250216_loose_v7"

model_file = f'MC15rd_best_xgb_model_etapip_gg_K_loose_{overall_version}.pkl'
best_xgb_model = joblib.load(model_file)


branches_gg = ['Pip_p','etapip_Eta_isSignal','Pip_mcPDG','skimhad','Dp_dz','Pip_pionID','Pip_genMotherID','etapip_Eta_genMotherID','Pip_genMotherPDG','etapip_Eta_genMotherPDG','Dp_cosHelicityAngleMomentum','Pip_dr',"Dp_isSignal","Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane", "Dp_CMS_p","etapip_Eta_Easym","Dp_M","etapip_Eta_daughterDiffOfPhi_0_1","etapip_Eta_daughterAngle_0_1"]  # Replace with actual branch names


elements_sig = ["DptoetaKp_gg", "DptoetaKp_gg_cc"]
project_name = sig_MC_name

file_list_sig = []
for element in elements_sig:
    pattern = f"{base_path_sig}/{element}/{project_name}/{sig_MC_name}*.root"
    file_list_sig += glob.glob(pattern)

dataframes_signal = []

for file_name in file_list_sig:
    file = uproot.open(file_name)
    tree = file["etapip_gg_K"]

    df_temp = tree.arrays(branches_gg, library="pd")
    dataframes_signal.append(df_temp)

df_signal = pd.concat(dataframes_signal, ignore_index=True)
df_signal = df_signal.query('Dp_isSignal==1')

elements_sig =  ["Dptoetapip_gg", "Dptoetapip_gg_cc"]
project_name = sig_MC_name

file_list_sig = []
for element in elements_sig:
    pattern = f"{base_path_sig}/{element}/{project_name}/{sig_MC_name}*.root"
    file_list_sig += glob.glob(pattern)

dataframes_signal = []

for file_name in file_list_sig:
    file = uproot.open(file_name)
    tree = file["etapip_gg"]

    df_temp = tree.arrays(branches_gg, library="pd")
    dataframes_signal.append(df_temp)

df_ref = pd.concat(dataframes_signal, ignore_index=True)
df_ref = df_ref.query('Dp_isSignal==1')


elements_sig = ["DsptoetaKp_gg", "DsptoetaKp_gg_cc"]
project_name = sig_MC_name

file_list_sig = []
for element in elements_sig:
    pattern = f"{base_path_sig}/{element}/{project_name}/{sig_MC_name}*.root"
    file_list_sig += glob.glob(pattern)

dataframes_signal = []

for file_name in file_list_sig:
    file = uproot.open(file_name)
    tree = file["etapip_gg_K"]

    df_temp = tree.arrays(branches_gg, library="pd")
    dataframes_signal.append(df_temp)


df_signal_Dsp = pd.concat(dataframes_signal, ignore_index=True)
df_signal_Dsp = df_signal_Dsp.query('(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & ((Pip_genMotherPDG == 431 and Pip_mcPDG == 321) | (Pip_genMotherPDG == -431 and Pip_mcPDG == -321) )')

elements_sig = ["Dsptoetapip_gg", "Dsptoetapip_gg_cc"]
project_name = sig_MC_name

file_list_sig = []
for element in elements_sig:
    pattern = f"{base_path_sig}/{element}/{project_name}/{sig_MC_name}*.root"
    file_list_sig += glob.glob(pattern)

dataframes_signal = []

for file_name in file_list_sig:
    file = uproot.open(file_name)
    tree = file["etapip_gg"]

    df_temp = tree.arrays(branches_gg, library="pd")
    dataframes_signal.append(df_temp)


df_ref_Dsp = pd.concat(dataframes_signal, ignore_index=True)
df_ref_Dsp = df_ref_Dsp.query('(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & ((Pip_genMotherPDG == 431 and Pip_mcPDG == 211) | (Pip_genMotherPDG == -431 and Pip_mcPDG == -211) )')

unique_values = df_signal_Dsp['etapip_Eta_genMotherPDG'].unique()
print(unique_values)

df_signal = df_signal.query('Pip_p>0.4 ')
df_signal = df_signal.query('Pip_pionID<0.01')
df_signal = df_signal.query('abs(etapip_Eta_daughterDiffOfPhi_0_1)<1.8')
df_signal = df_signal.query('etapip_Eta_daughterAngle_0_1<1.6')
df_signal = df_signal.query('skimhad==1')

df_ref = df_ref.query('Pip_p>0.4 ')
df_ref = df_ref.query('abs(etapip_Eta_daughterDiffOfPhi_0_1)<1.8')
df_ref = df_ref.query('etapip_Eta_daughterAngle_0_1<1.6')
df_ref = df_ref.query('skimhad==1')

df_signal_Dsp = df_signal_Dsp.query('Pip_p>0.4 ')
df_signal_Dsp = df_signal_Dsp.query('Pip_pionID<0.01')
df_signal_Dsp = df_signal_Dsp.query('abs(etapip_Eta_daughterDiffOfPhi_0_1)<1.8')
df_signal_Dsp = df_signal_Dsp.query('etapip_Eta_daughterAngle_0_1<1.6')
df_signal_Dsp = df_signal_Dsp.query('skimhad==1')

df_ref_Dsp = df_ref_Dsp.query('Pip_p>0.4 ')
df_ref_Dsp = df_ref_Dsp.query('abs(etapip_Eta_daughterDiffOfPhi_0_1)<1.8')
df_ref_Dsp = df_ref_Dsp.query('etapip_Eta_daughterAngle_0_1<1.6')
df_ref_Dsp = df_ref_Dsp.query('skimhad==1')

nan_columns = df_signal.isnull().any()
print(nan_columns)
nan_columns = df_signal_Dsp.isnull().any()
print(nan_columns)

# Drop the specified columns
columns_to_drop = ['etapip_Eta_isSignal','Pip_mcPDG','skimhad','Pip_pionID','Pip_genMotherID','etapip_Eta_genMotherID','Pip_genMotherPDG','etapip_Eta_genMotherPDG',"Dp_isSignal", "Dp_M"]

df_signal_dropped = df_signal.drop(columns=columns_to_drop)
df_signal_Dsp_dropped = df_signal_Dsp.drop(columns=columns_to_drop)

df_ref_dropped = df_ref.drop(columns=columns_to_drop)
df_ref_Dsp_dropped = df_ref_Dsp.drop(columns=columns_to_drop)

# Reorder the columns of df_isSignal_true_dropped and df_isSignal_false_dropped to match the training data's feature order
df_signal_dropped = df_signal_dropped[best_xgb_model.get_booster().feature_names]
df_signal_Dsp_dropped = df_signal_Dsp_dropped[best_xgb_model.get_booster().feature_names]

df_ref_dropped = df_ref_dropped[best_xgb_model.get_booster().feature_names]
df_ref_Dsp_dropped = df_ref_Dsp_dropped[best_xgb_model.get_booster().feature_names]

# Now try to predict probabilities
df_signal_probabilities = best_xgb_model.predict_proba(df_signal_dropped)
df_signal_dropped['prob_signal'] = df_signal_probabilities[:, 1]

df_signal_Dsp_probabilities = best_xgb_model.predict_proba(df_signal_Dsp_dropped)
df_signal_Dsp_dropped['prob_signal'] = df_signal_Dsp_probabilities[:, 1]

df_ref_probabilities = best_xgb_model.predict_proba(df_ref_dropped)
df_ref_dropped['prob_signal'] = df_ref_probabilities[:, 1]

df_ref_Dsp_probabilities = best_xgb_model.predict_proba(df_ref_Dsp_dropped)
df_ref_Dsp_dropped['prob_signal'] = df_ref_Dsp_probabilities[:, 1]

# Optionally, you can combine the datasets back with 'Dp_M' if needed
df_signal_combined = pd.merge(df_signal, df_signal_dropped[['prob_signal']], left_index=True, right_index=True)
df_signal_Dsp_combined = pd.merge(df_signal_Dsp, df_signal_Dsp_dropped[['prob_signal']], left_index=True, right_index=True)

df_ref_combined = pd.merge(df_ref, df_ref_dropped[['prob_signal']], left_index=True, right_index=True)
df_ref_Dsp_combined = pd.merge(df_ref_Dsp, df_ref_Dsp_dropped[['prob_signal']], left_index=True, right_index=True)

df_signal_SR = df_signal_combined.query('Dp_M>1.78 & Dp_M<1.94')
df_signal_Dsp_SR = df_signal_Dsp_combined.query('Dp_M>1.88 & Dp_M<2.04')

df_ref_SR = df_ref_combined.query('Dp_M>1.78 & Dp_M<1.94')
df_ref_Dsp_SR = df_ref_Dsp_combined.query('Dp_M>1.88 & Dp_M<2.04')

plt.figure(figsize=(12, 6))
plt.hist(df_signal_SR['prob_signal'], bins=np.linspace(0, 1, 71), histtype='step', color='red', label=r'$D^+$', density=True)
plt.hist(df_signal_Dsp_SR['prob_signal'], bins=np.linspace(0, 1, 71), histtype='step', color='blue', label=r'$D^+_s$', density=True)
plt.hist(df_ref_SR['prob_signal'], bins=np.linspace(0, 1, 71), histtype='step', color='orange', label=r'$D^+$ reference', density=True)
plt.hist(df_ref_Dsp_SR['prob_signal'], bins=np.linspace(0, 1, 71), histtype='step', color='cyan', label=r'$D^+_s$ reference',density=True)

plt.xlabel('Dp_M')
plt.ylabel('Candidates')
plt.legend()

# plt.grid(True)
plt.xlim(0,1)
#plt.xlabel(r'$M(D^+) \; [\mathrm{GeV/c^2}]$')
plt.xlabel(r'BDT')

plt.tight_layout()
plt.savefig(f"test.png")

plt.show()

print(f"D+ eff: {len(df_signal_SR.query('prob_signal>0.91'))/len(df_signal_SR)*100}%")
print(f"D+ ref eff: {len(df_ref_SR.query('prob_signal>0.91'))/len(df_ref_SR)*100}%")
print(f"Ds+ eff: {len(df_signal_Dsp_SR.query('prob_signal>0.91'))/len(df_signal_Dsp_SR)*100}%")
print(f"Ds+ ref eff: {len(df_ref_Dsp_SR.query('prob_signal>0.91'))/len(df_ref_Dsp_SR)*100}%")



# Dictionary for feature names
feature_labels = {
    'Pip_dr': r'$dr(K^+)$',
    'Dp_dz': r'$dz(D^+_{(s)})$',
    'Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane': r'$\cos \theta_{XY}$',
    'etapip_Eta_Easym': r'$|\frac{E_{\gamma_1} - E_{\gamma_2} }{E_{\gamma_1} + E_{\gamma_2}}|$',
    'Dp_cosHelicityAngleMomentum': r'cosHel$(D^+_{(s)})$',
    'Dp_CMS_p': r'$p^*(D^+_{(s)})$'
}
