import uproot
import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt
plt.style.use('default')
plt.style.use('belle2')

import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
import joblib

gen_MC_name = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto"
base_path_sig = "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC"
sig_MC_name = "260107_loose_v7_less_vars_ntuple"
tree_name="etapip_pipipi"

overall_version = "v7_correct_cosHel"

base_path = gen_MC_name
cm_elements = ["15rd_jae_e7_18_4S_v3", "15rd_jae_e20_b26_v1", "15rd_jae_e20_e26_4S_v2", "15rd_jae_e21_5S_scan_v1", "15rd_jae_mori_off_v1"]
#cm_elements = ["15rd_jae_e20_b26_v1"]
branches = ['etapip_Eta_isSignal','Pip_mcPDG','skimhad','Dp_dz','Pip_binaryP','Pip_pionIDNN','Pip_pionID','Dp_Psum','Pip_genMotherID','etapip_Eta_genMotherID','Pip_genMotherPDG','etapip_Eta_genMotherPDG','Dp_cosHelicityAngleMomentum','Pip_dr',"Dp_isSignal","Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane",
            "Pip_p","Dp_CMS_p","etapip_Eta_p","Dp_M"]
training_features = [
    "Pip_dr",
    "Dp_dz",
    "Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane",
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
df_bkg = df_bkg.query('((etapip_Eta_isSignal != 1) or (Pip_genMotherID != etapip_Eta_genMotherID) or ((Pip_genMotherPDG != 431 or Pip_mcPDG != 211) and (Pip_genMotherPDG != -431 or Pip_mcPDG != -211) ) )')
df_bkg = df_bkg.query('Pip_p>0.4')
df_bkg = df_bkg.query('Dp_M> 1.6 & Dp_M<2.1')
df_bkg = df_bkg.query('skimhad==1')

print("Generic samples are imported")
nan_columns = df_bkg.isnull().any()
print("NaN included columns")
print(nan_columns)

df_bkg.describe()

elements_sig = ["Dptoetapip_pipipi", "Dptoetapip_pipipi_cc"]
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

elements_sig = ["Dsptoetapip_pipipi", "Dsptoetapip_pipipi_cc"]
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
df_signal_Dsp = df_signal_Dsp.query('(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & ((Pip_genMotherPDG == 431 and Pip_mcPDG == 211) | (Pip_genMotherPDG == -431 and Pip_mcPDG == -211) )')

unique_values = df_signal_Dsp['etapip_Eta_genMotherPDG'].unique()
print(unique_values)
df_signal = pd.concat([df_signal, df_signal_Dsp], ignore_index=True)
df_signal = df_signal.query('Pip_p>0.4 ')
df_signal = df_signal.query('Dp_M> 1.6 & Dp_M<2.1')
df_signal = df_signal.query('skimhad==1')

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

xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')

# # Define the parameter grid for XGBoost
# param_grid = {
#     'n_estimators': [50, 100, 150],
#     'max_depth': [3, 5, 7],
#     'learning_rate': [0.01, 0.1, 0.2],
#     'subsample': [0.8, 1.0],
#     'colsample_bytree': [0.8, 1.0]
# }
param_grid = {
    'n_estimators': [500, 700, 900],
    'max_depth': [5, 7, 9, 11],
    'learning_rate': [0.005, 0.01, 0.1],
    #'subsample': [0.8,0.9, 1.0],
    #'colsample_bytree': [0.8,0.9, 1.0]
}
# Initialize GridSearchCV with cross-validation
grid_search = GridSearchCV(
     estimator=xgb_model,
     param_grid=param_grid,
     scoring='accuracy',
     cv=5,  # 5-fold cross-validation
     verbose=1,
     n_jobs=27
)

# Perform the grid search
grid_search.fit(X, y)

# # Get the best model and its parameters
best_xgb_model = grid_search.best_estimator_
print("Best Parameters:", grid_search.best_params_)
print("Best Cross-Validation Accuracy:", grid_search.best_score_)
joblib.dump(best_xgb_model, f'MC15rd_best_xgb_model_{tree_name}_loose_{overall_version}.pkl')

#xgb_model.fit(X,y)
#best_xgb_model = xgb_model
#joblib.dump(best_xgb_model, f'MC15rd_best_xgb_model_{tree_name}_loose_{overall_version}.pkl')

print('Training is done!')

# Extract all mean cross-validation scores and parameter combinations
results_df = pd.DataFrame(grid_search.cv_results_)

# Sort results by mean test score in descending order
results_df = results_df.sort_values(by='mean_test_score', ascending=False)

# Highlight the best score
best_score = grid_search.best_score_

# Plotting the scores using Matplotlib
plt.figure(figsize=(10, 6))

# Create a scatter plot
plt.scatter(
    range(len(results_df)),
    results_df['mean_test_score'],
    c='blue',  # Color for the points
    s=10,
    marker='o',
    label='Mean CV Score'
)

# Highlighting the best score
best_index = results_df['mean_test_score'].idxmax()
plt.scatter(best_index, best_score, color='red', s=20, label=f'Best Score: {best_score:.4f}', edgecolor='black')

# Adding labels and legend
plt.title("Grid Search CV Scores for Hyperparameter Tuning")
plt.xlabel("Hyperparameter Combination Index")
plt.ylabel("Mean CV Accuracy Score")
plt.legend()
plt.xlim(0,)
plt.tight_layout()
plt.savefig(f"MC15rd_{tree_name}_gridsearch_loose_{overall_version}.png")

# Show the plot
plt.show()

