import uproot
import seaborn as sns
import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
plt.style.use('default')
plt.style.use('belle2')
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score
from sklearn.metrics import roc_curve, auc
from xgboost import XGBClassifier
import joblib

title_dict=dict()
title_dict['etapip_gg']=r'$D^+_{(s)} \to \eta_{\gamma\gamma} \pi^+$'
title_dict['etapip_gg_K']=r'$D^+_{(s)} \to \eta_{\gamma\gamma} K^+$'

mass_dict=dict()
mass_dict['etapip_gg']=r'$M(\eta_{\gamma\gamma}\pi^+)$'
mass_dict['etapip_gg_K']=r'$M(\eta_{\gamma\gamma}K^+)$'

gen_MC_name = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto"
base_path_sig = "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC"
sig_MC_name = "260107_loose_v7_less_vars_ntuple"
tree_name="etapip_gg_K"

overall_version = "v7_correct_cosHel"

base_path = gen_MC_name
cm_elements = ["15rd_jae_e7_18_4S_v3", "15rd_jae_e20_b26_v1", "15rd_jae_e20_e26_4S_v2", "15rd_jae_e21_5S_scan_v1", "15rd_jae_mori_off_v1"]
#cm_elements = ["15rd_jae_e20_b26_v1"]
branches = ['etapip_Eta_isSignal','Pip_mcPDG','skimhad','Dp_dz','Pip_binaryP','Pip_pionIDNN','Pip_pionID','Dp_Psum','dM_pi0_mask_nonan','dM_pi0_mask_2_nonan','Pip_genMotherID','etapip_Eta_genMotherID','Pip_genMotherPDG','etapip_Eta_genMotherPDG','Dp_cosHelicityAngleMomentum','Pip_dr',"Dp_isSignal","Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane",
            "Pip_p","Dp_CMS_p","etapip_Eta_Easym","etapip_Eta_p","Dp_M","etapip_Eta_daughterDiffOfPhi_0_1","etapip_Eta_daughterAngle_0_1"]
training_features = [
    "Pip_dr",
    "Dp_dz",
    "Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane",
    "etapip_Eta_Easym",
    "Dp_cosHelicityAngleMomentum",
    "Dp_CMS_p",
]
print('Training features:' + str(training_features))
columns_to_drop = list(set(branches) - set(training_features))

file_list = []
for element in cm_elements:
    pattern = f"{base_path}/{element}/*.root"
    file_list += glob.glob(pattern)

dataframes = []
for file_name in file_list:
    file = uproot.open(file_name)
    tree = file[f"{tree_name}"]
    df_temp = tree.arrays(branches, library="pd")
    dataframes.append(df_temp)

df_bkg = pd.concat(dataframes, ignore_index=True)
df_bkg = df_bkg.query('Dp_isSignal!=1')
df_bkg = df_bkg.query('((etapip_Eta_isSignal != 1) or (Pip_genMotherID != etapip_Eta_genMotherID) or ((Pip_genMotherPDG != 431 or Pip_mcPDG != 321) and (Pip_genMotherPDG != -431 or Pip_mcPDG != -321) ) )')
df_bkg = df_bkg.query('Pip_pionID<0.01')
df_bkg = df_bkg.query('Pip_p>0.4')
df_bkg = df_bkg.query('Dp_M> 1.7 & Dp_M<2.1')
df_bkg = df_bkg.query('abs(etapip_Eta_daughterDiffOfPhi_0_1)<1.8')
df_bkg = df_bkg.query('etapip_Eta_daughterAngle_0_1<1.6')
df_bkg = df_bkg.query('skimhad==1')
df_bkg = df_bkg.query('dM_pi0_mask_nonan>0.011 and dM_pi0_mask_2_nonan>0.011')

print("Generic samples are imported!")
nan_columns = df_bkg.isnull().any()
print(nan_columns)

df_bkg.describe()

elements_sig = ["DptoetaKp_gg", "DptoetaKp_gg_cc"]
project_name = sig_MC_name

file_list_sig = []
for element in elements_sig:
    pattern = f"{base_path_sig}/{element}/{project_name}/*.root"
    file_list_sig += glob.glob(pattern)
dataframes_signal = []
for file_name in file_list_sig:
    file = uproot.open(file_name)
    tree = file[f"{tree_name}"]
    df_temp = tree.arrays(branches, library="pd")
    dataframes_signal.append(df_temp)
df_signal = pd.concat(dataframes_signal, ignore_index=True)
df_signal = df_signal.query('Dp_isSignal==1')

elements_sig = ["DsptoetaKp_gg", "DsptoetaKp_gg_cc"]
project_name = sig_MC_name
file_list_sig = []
for element in elements_sig:
    pattern = f"{base_path_sig}/{element}/{project_name}/*.root"
    file_list_sig += glob.glob(pattern)
dataframes_signal = []
for file_name in file_list_sig:
    file = uproot.open(file_name)
    tree = file[f"{tree_name}"]
    df_temp = tree.arrays(branches, library="pd")
    dataframes_signal.append(df_temp)
df_signal_Dsp = pd.concat(dataframes_signal, ignore_index=True)
df_signal_Dsp = df_signal_Dsp.query('(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & ((Pip_genMotherPDG == 431 and Pip_mcPDG == 321) | (Pip_genMotherPDG == -431 and Pip_mcPDG == -321) )')

unique_values = df_signal_Dsp['etapip_Eta_genMotherPDG'].unique()
print(unique_values)
df_signal = pd.concat([df_signal, df_signal_Dsp], ignore_index=True)
df_signal = df_signal.query('Pip_pionID<0.01')
df_signal = df_signal.query('Pip_p>0.4 ')
df_signal = df_signal.query('Dp_M> 1.7 & Dp_M<2.1')
df_signal = df_signal.query('abs(etapip_Eta_daughterDiffOfPhi_0_1)<1.8')
df_signal = df_signal.query('etapip_Eta_daughterAngle_0_1<1.6')
df_signal = df_signal.query('skimhad==1')
df_signal = df_signal.query('dM_pi0_mask_nonan>0.011 and dM_pi0_mask_2_nonan>0.011')
print("Signal samples are imported!")

nan_columns = df_signal.isnull().any()
print(nan_columns)

# Ensure the signal and background datasets are balanced
min_size = min(len(df_signal), len(df_bkg))
# Sample an equal number of rows from both signal and background
df_signal_balanced = df_signal.sample(n=min_size, random_state=42)
df_bkg_balanced = df_bkg.sample(n=min_size, random_state=42)

# Assign labels: signal=1, background=0
df_signal_balanced['label'] = 1
df_bkg_balanced['label'] = 0

# Concatenate the signal and background datasets
df_combined = pd.concat([df_signal_balanced, df_bkg_balanced], ignore_index=True)

# Shuffle the combined dataset
df_combined = df_combined.sample(frac=1, random_state=42).reset_index(drop=True)

# Drop the specified columns

df_combined = df_combined.drop(columns=columns_to_drop)
df_combined.describe()

plt.rcParams['font.family'] = 'DejaVu Sans'


# Separate features and labels
X = df_combined.drop(columns='label')
y = df_combined['label']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X = X_train
y = y_train

# Correlation plot ####################
# Dictionary for feature names
feature_labels = {
    'Pip_dr': r'$dr(h^+)$',
    'Dp_dz': r'$dz(D^+_{(s)})$',
    'Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane': r'$\cos \theta_{XY}$',
    'etapip_Eta_Easym': r'$|\frac{E_{\gamma_1} - E_{\gamma_2} }{E_{\gamma_1} + E_{\gamma_2}}|$',
    'Dp_cosHelicityAngleMomentum': r'cosHel$(D^+_{(s)})$',
    'Dp_CMS_p': r'$p^*(D^+_{(s)})$'
}

### **1. Correlation Plot (Using X_train)**
correlation_matrix = X_train.corr()

plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1,
            xticklabels=[feature_labels.get(col, col) for col in correlation_matrix.columns],
            yticklabels=[feature_labels.get(col, col) for col in correlation_matrix.columns])
plt.title("2D Correlation Plot (Training Data)")
plt.tight_layout()
plt.savefig(f'MC15rd_corr_{tree_name}_loose_{overall_version}.png')
plt.show()

# Feature distribution plot ####################
# **Define x-ranges for specific features** (optional)
x_ranges = {
    'Pip_dr': (0, 1),
    'Dp_dz': (-1, 1),
    'Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane': (-1.0, 1.0),
    'etapip_Eta_Easym' : (0,1),
    'Dp_cosHelicityAngleMomentum': (-1.0, 1.0),
    'Dp_CMS_p': (2.5, 6.5)
}
log_scale_features = {'Pip_dr', 'Dp_dz', 'Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane'}


plt.figure(figsize=(18, 12))

for i, feature in enumerate(feature_labels.keys(), 1):
    plt.subplot(2, 3, i)

    # Use predefined x-range if available, otherwise use min/max from X_train
    xmin, xmax = x_ranges.get(feature, (X_train[feature].min(), X_train[feature].max()))
    bins = np.linspace(xmin, xmax, 50)

    # Plot signal (y_train == 1) and background (y_train == 0)
    plt.hist(X_train[feature][y_train == 1], bins=bins, density=True, alpha=0.5, color='r', label='Signal')
    plt.hist(X_train[feature][y_train == 0], bins=bins, density=True, alpha=0.5, color='b', label='Background')

    plt.xlabel(feature_labels[feature])
    plt.ylabel("Normalized Frequency")
    plt.xlim(xmin, xmax)  # Set the x-range
    #if feature in log_scale_features:
    #    plt.yscale("log")

    plt.legend()

plt.tight_layout()
plt.savefig(f'MC15rd_features_{tree_name}_loose_{overall_version}.png')
plt.show()


# Ipomrtance plots ####################
model_file = f'MC15rd_best_xgb_model_{tree_name}_loose_{overall_version}.pkl'
best_xgb_model = joblib.load(model_file)
booster = best_xgb_model.get_booster()

feature_names = {
    'Pip_dr': r'$dr(h^+)$',
    'Dp_dz': r'$dz(D^+_{(s)})$',
    'Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane': r'$\cos \theta_{XY}$',
    'etapip_Eta_Easym': r'$|\frac{E_{\gamma_1} - E_{\gamma_2} }{E_{\gamma_1} + E_{\gamma_2}}|$',
    'Dp_cosHelicityAngleMomentum': r'cosHel$(D^+_{(s)})$',
    'Dp_CMS_p': r'$p^*(D^+_{(s)})$'
}
# 3. Loop through the three importance types
importance_types = ['weight', 'gain', 'cover', 'total_gain', 'total_cover']
#‘weight’: the number of times a feature is used to split the data across all trees.
#‘gain’: the average gain across all splits the feature is used in.
#‘cover’: the average coverage across all splits the feature is used in.

for imp_type in importance_types:
    # Get score for this specific type
    importance_dict = booster.get_score(importance_type=imp_type)

    # Create DataFrame
    importance_df = pd.DataFrame.from_dict(importance_dict, orient='index', columns=['Score'])

    # Rename indices using LaTeX labels
    importance_df.index = [feature_names.get(f, f) for f in importance_df.index]

    # Sort by score
    importance_df = importance_df.sort_values(by='Score', ascending=False)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.barh(importance_df.index, importance_df['Score'], color='teal')

    # Dynamic labels and titles
    plt.xlabel(fr'Feature Importance', fontsize=16)
    plt.title(fr'{title_dict[tree_name]}' + f' ({imp_type.capitalize()})', fontsize=18)

    plt.gca().invert_yaxis()  # Most important on top
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()

    # Save with unique filename
    output_filename = f"MC15rd_{tree_name}_importance_loose_{overall_version}_{imp_type}.png"
    plt.savefig(output_filename)
    plt.close() # Close the figure to free memory

    print(f"Saved: {output_filename}")

# ROC plot ####################
# Get predicted probabilities for the positive class
y_prob_xgb = best_xgb_model.predict_proba(X_test)[:, 1]

# Compute ROC curve and AUC
fpr_xgb, tpr_xgb, thresholds_xgb = roc_curve(y_test, y_prob_xgb)
roc_auc_xgb = auc(fpr_xgb, tpr_xgb)

# Plot ROC curve
plt.figure(figsize=(8, 6))
plt.plot(fpr_xgb, tpr_xgb, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc_xgb:.3f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic for Best Model')
plt.legend(loc='lower right')
plt.grid(True)
plt.tight_layout()
plt.savefig(f"MC15rd_{tree_name}_roc_loose_{overall_version}.png")

plt.show()

# Train,test BDT output plot ####################
# Function to plot histograms for train (as points) and test (as bars)
def plot_probability_histograms(y_train_true, y_train_probs, y_test_true, y_test_probs):
    plt.figure(figsize=(12, 6))

    # Define a common set of bins for both train and test
    bins = np.linspace(0, 1, 61)  # 60 bins from 0 to 1 for predicted probabilities

    # Test set: Plot histograms as bars
    plt.hist(y_test_probs[y_test_true == 1], bins=bins, alpha=0.5, label='Test Signal Class', color='green', edgecolor='black', density=True)
    plt.hist(y_test_probs[y_test_true == 0], bins=bins, alpha=0.5, label='Test Bkg Class', color='red', edgecolor='black', density=True)

    # Train set: Calculate histogram values for points
    hist_train_pos, _ = np.histogram(y_train_probs[y_train_true == 1], bins=bins, density=True)
    hist_train_neg, _ = np.histogram(y_train_probs[y_train_true == 0], bins=bins, density=True)

    # Calculate the bin centers (to place the points in the middle of each bin)
    bin_centers = 0.5 * (bins[1:] + bins[:-1])

    # Plot the train set histograms as points
    plt.plot(bin_centers, hist_train_pos, 'o', label='Train Signal Class', color='darkgreen')
    plt.plot(bin_centers, hist_train_neg, 'o', label='Train Bkg Class', color='darkred')

    # Labels, title, and legend
    plt.xlabel('Predicted Probabilities')
    plt.ylabel('Density')
    plt.legend(loc='best')
    plt.grid(True)
    plt.xlim(0,1)


# Calculate predicted probabilities for the training and test sets
y_train_probs = best_xgb_model.predict_proba(X_train)[:, 1]
y_test_probs = best_xgb_model.predict_proba(X_test)[:, 1]

# Plot histograms with train set as points and test set as bars
plot_probability_histograms(
    y_train, y_train_probs,
    y_test, y_test_probs
)

plt.tight_layout()
plt.savefig(f"MC15rd_train_test_{tree_name}_loose_{overall_version}.png")
plt.show()

# FOM, whole BDT, BDT per D+,Ds+,bkg plots ####################
baes_path = gen_MC_name

file_list = []
for element in cm_elements:
    pattern = f"{base_path}/{element}/*.root"
    file_list += glob.glob(pattern)

# Initialize an empty list to hold DataFrames
dataframes = []

# Process each file
for file_name in file_list:
    # Load the ROOT file and tree
    file = uproot.open(file_name)
    tree = file[f"{tree_name}"]
    # Convert the selected branches to a Pandas DataFrame
    df_temp = tree.arrays(branches, library="pd")
    # Append the DataFrame to the list
    dataframes.append(df_temp)

# Concatenate all DataFrames into a single DataFrame
df_bkg_apply = pd.concat(dataframes, ignore_index=True)
df_bkg_apply = df_bkg_apply.query('Pip_pionID<0.01')
df_bkg_apply = df_bkg_apply.query('Pip_p>0.4')
df_bkg_apply = df_bkg_apply.query('Dp_M> 1.7 & Dp_M<2.1')
df_bkg_apply = df_bkg_apply.query('abs(etapip_Eta_daughterDiffOfPhi_0_1)<1.8')
df_bkg_apply = df_bkg_apply.query('etapip_Eta_daughterAngle_0_1<1.6')
df_bkg_apply = df_bkg_apply.query('skimhad==1')
df_bkg_apply = df_bkg_apply.query('dM_pi0_mask_nonan>0.011 and dM_pi0_mask_2_nonan>0.011')

# Separate signal and background data
df_isSignal_true = df_bkg_apply.query('Dp_isSignal==1')
df_isSignal_false = df_bkg_apply.query('Dp_isSignal!=1')

df_isSignal_true_dropped = df_isSignal_true.drop(columns=columns_to_drop)
df_isSignal_false_dropped = df_isSignal_false.drop(columns=columns_to_drop)


# Reorder the columns of df_isSignal_true_dropped and df_isSignal_false_dropped to match the training data's feature order
df_isSignal_true_dropped = df_isSignal_true_dropped[best_xgb_model.get_booster().feature_names]
df_isSignal_false_dropped = df_isSignal_false_dropped[best_xgb_model.get_booster().feature_names]
#df_isSignal_true_dropped = df_isSignal_true_dropped[best_xgb_model.feature_name_]
#df_isSignal_false_dropped = df_isSignal_false_dropped[best_xgb_model.feature_name_]

# Now try to predict probabilities
isSignal_true_probabilities = best_xgb_model.predict_proba(df_isSignal_true_dropped)
df_isSignal_true_dropped['prob_signal'] = isSignal_true_probabilities[:, 1]

isSignal_false_probabilities = best_xgb_model.predict_proba(df_isSignal_false_dropped)
df_isSignal_false_dropped['prob_signal'] = isSignal_false_probabilities[:, 1]

# Optionally, you can combine the datasets back with 'Dp_M' if needed
df_isSignal_true_combined = pd.merge(df_isSignal_true, df_isSignal_true_dropped[['prob_signal']], left_index=True, right_index=True)
df_isSignal_false_combined = pd.merge(df_isSignal_false, df_isSignal_false_dropped[['prob_signal']], left_index=True, right_index=True)


df_combined_all_range = pd.concat([df_isSignal_true_combined, df_isSignal_false_combined], ignore_index=True)

df_combined_all_range['Dp_isSignal'] = df_combined_all_range['Dp_isSignal'].fillna(0)

df_combined_all_range.columns.tolist()

df_combined = df_combined_all_range.query('Dp_M>1.78 & Dp_M<1.94')
#df_combined = df_combined_all_range.query('Dp_M>1.83 & Dp_M<1.89')

scale = 1/4
# Define the figure of merit function using query
def figure_of_merit(df, cut_value):
    df_cut = df.query('prob_signal > @cut_value')
    Nsig = (df_cut['Dp_isSignal'] == 1).sum()
    Nbkg = (df_cut['Dp_isSignal'] != 1).sum()
    if Nsig + Nbkg == 0:
        return 0
    return Nsig*scale / np.sqrt(Nsig*scale + Nbkg*scale)

# Define range of cut values to test
cut_values = np.linspace(0, 1, 101)  # You can adjust the range and granularity

# Calculate figure of merit for each cut value
figures_of_merit = [figure_of_merit(df_combined, cut) for cut in cut_values]

# Find the best cut value
best_cut = cut_values[np.argmax(figures_of_merit)]
best_fom = max(figures_of_merit)

# Print the best cut value and corresponding figure of merit
print(f'Best cut value: {best_cut}')
print(f'Best figure of merit: {best_fom}')

# Plot figure of merit vs. cut value
plt.figure(figsize=(10, 6))
plt.plot(cut_values, figures_of_merit, color='blue', label='Figure of Merit', linewidth=2)
plt.axvline(x=best_cut, color='red', linestyle='--', label=f'Optimal Cut ({best_cut:.2f})')
plt.xlabel('Cut Value')
plt.ylabel('Figure of Merit')
plt.title('Figure of Merit vs. Cut Value')
plt.xlim(0,1)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(f"MC15rd_{tree_name}_FOM_loose_{overall_version}.png")

# Define the optimal cut (replace with the actual value from your previous code)
optimal_cut = best_cut

# Separate the dataframe based on the optimal cut
df_signal = df_combined_all_range.query('prob_signal > @optimal_cut')
# Create histograms
plt.figure(figsize=(12, 6))

# Histogram for signal
plt.hist(df_signal['Dp_M'], bins=np.linspace(1.7, 2.05, 71), histtype='step', color='red', label='All')

# Histogram for background
# plt.hist(df_background['Dp_M'], bins=np.linspace(1.6, 2.1, 71), histtype='step', color='red', label='Background')

plt.xlabel('Dp_M')
plt.ylabel('Candidates')
# plt.title('Histogram of Dp_M for Signal and Background')
plt.legend()

# plt.grid(True)
plt.xlim(1.7,2.05)
plt.xlabel(fr'{mass_dict[tree_name]} $\; [\mathrm{{GeV/c^2}}]$')


plt.tight_layout()
plt.savefig(f"MC15rd_{tree_name}_Dp_M_all_loose_{overall_version}.png")

plt.show()


scale = 1/4
df_signal_matched_true = df_signal.query('Dp_isSignal==1')
print(f'nsig={len(df_signal_matched_true)}')
print(f'nsig={len(df_signal_matched_true)*scale}')

# Define the optimal cut (replace with the actual value from your previous code)
optimal_cut = best_cut

# Separate the dataframe based on the optimal cut
df_signal = df_combined_all_range.query('prob_signal > 0')
df_background = df_combined_all_range.query('prob_signal > @optimal_cut')

# Create histograms
plt.figure(figsize=(12, 6))

# Histogram for signal
plt.hist(df_signal['Dp_M'], bins=np.linspace(1.7, 2.05, 71), histtype='step', color='blue', label='Before')

# Histogram for background
plt.hist(df_background['Dp_M'], bins=np.linspace(1.7, 2.05, 71), histtype='step', color='red', label='After')

plt.xlabel('Dp_M')
plt.ylabel('Candidates')
# plt.title('Histogram of Dp_M for Signal and Background')
plt.legend()

# plt.grid(True)

plt.xlabel(fr'{mass_dict[tree_name]} $\; [\mathrm{{GeV/c^2}}]$')
plt.xlim(1.7,2.05)
plt.tight_layout()
plt.savefig(f"MC15rd_{tree_name}_Dp_M_before_after_loose_{overall_version}.png")

plt.show()


print(f'n_before={len(df_signal)}')
print(f'n_after={len(df_background)}')
print(f'cut eff={len(df_background)/len(df_signal)}')

# Separate the dataframe based on the optimal cut
df_signal = df_combined_all_range.query('Dp_isSignal==1')
df_background_Ds = df_combined_all_range.query('(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & ((Pip_genMotherPDG == 431 and Pip_mcPDG == 321) | (Pip_genMotherPDG == -431 and Pip_mcPDG == -321) )')
df_background = df_combined_all_range.query('(Dp_isSignal != 1) and ((etapip_Eta_isSignal != 1) or (Pip_genMotherID != etapip_Eta_genMotherID) or ((Pip_genMotherPDG != 431 or Pip_mcPDG != 321) and (Pip_genMotherPDG != -431 or Pip_mcPDG != -321) ) )')

# Create histograms
plt.figure(figsize=(12, 6))

# Histogram for signal
plt.hist(df_signal['prob_signal'], bins=np.linspace(0,1, 71), histtype='step', color='red', label=r'$D^+$ Signal',density=True)
plt.hist(df_background_Ds['prob_signal'], bins=np.linspace(0,1, 71), histtype='step', color='green', label=r'$D_s^+$ Signal',density=True)

# Histogram for background
plt.hist(df_background['prob_signal'], bins=np.linspace(0,1, 71), histtype='step', color='blue', label='Background',density=True)

plt.xlabel('BDT')
plt.ylabel('Density')

plt.title(fr'{title_dict[tree_name]}')
plt.legend()


# plt.grid(True)
plt.xlim(0,1)
plt.tight_layout()
plt.savefig(f"MC15rd_{tree_name}_BDT_output_Dp_Ds_bkg_loose_{overall_version}.png")

plt.show()


print(f'nsig={len(df_signal)}')
