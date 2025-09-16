import uproot
import pandas as pd
import numpy as np
import glob
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import joblib
plt.style.use('default')
plt.style.use('belle2')

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

# ============================
# 효율비 스캔 & 플롯 (BDT cut 변화)
# ============================


# 1) 스캔할 임계값(threshold) 목록 정의
#thresholds = [0.86, 0.87, 0.88, 0.89, 0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96]
center = 0.91
step = 0.001
num_steps_each_side = 20

thresholds = np.round(
    np.linspace(center - num_steps_each_side*step,
                center + num_steps_each_side*step,
                num_steps_each_side*2 + 1),
    3
).tolist()

print(thresholds)
def eff_above_threshold(df, thr):
    """df 내 prob_signal > thr 비율을 반환 (df 길이가 0이면 np.nan)"""
    n = len(df)
    if n == 0:
        return np.nan
    return (df['prob_signal'] > thr).sum() / n

# 2) 각 threshold에서 D+, D_s^+의 (signal/ref) 효율 계산
eff_Dp_sig  = []
eff_Dp_ref  = []
eff_Dsp_sig = []
eff_Dsp_ref = []

for thr in thresholds:
    eff_Dp_sig.append(eff_above_threshold(df_signal_SR,    thr))
    eff_Dp_ref.append(eff_above_threshold(df_ref_SR,       thr))
    eff_Dsp_sig.append(eff_above_threshold(df_signal_Dsp_SR,thr))
    eff_Dsp_ref.append(eff_above_threshold(df_ref_Dsp_SR,  thr))

eff_Dp_sig  = np.array(eff_Dp_sig)
eff_Dp_ref  = np.array(eff_Dp_ref)
eff_Dsp_sig = np.array(eff_Dsp_sig)
eff_Dsp_ref = np.array(eff_Dsp_ref)

# 3) 효율비 (ref/sig)
ratio_Dp   = eff_Dp_ref  / eff_Dp_sig
ratio_Dsp  = eff_Dsp_ref / eff_Dsp_sig

# 4) 기준점(예: 0.91)에서의 값 출력
cut0 = 0.91
def get_at_cut(xlist, ylist, cut):
    # thresholds 리스트에 정확히 있는 cut을 찾는 간단한 방법
    if cut in xlist:
        i = xlist.index(cut)
        return ylist[i]
    # float 오차 대비 근접값 선택
    i = int(np.argmin(np.abs(np.array(xlist) - cut)))
    return ylist[i]

Dp_eff_at_091      = get_at_cut(thresholds, eff_Dp_sig,  cut0)
Dp_ref_eff_at_091  = get_at_cut(thresholds, eff_Dp_ref,  cut0)
Dsp_eff_at_091     = get_at_cut(thresholds, eff_Dsp_sig, cut0)
Dsp_ref_eff_at_091 = get_at_cut(thresholds, eff_Dsp_ref, cut0)

Dp_ratio_at_091    = get_at_cut(thresholds, ratio_Dp,   cut0)
Dsp_ratio_at_091   = get_at_cut(thresholds, ratio_Dsp,  cut0)

print(f"[BDT > {cut0:.2f}]")
print(f"  D+     eff(sig) = {Dp_eff_at_091*100:.3f}%")
print(f"  D+     eff(ref) = {Dp_ref_eff_at_091*100:.3f}%")
print(f"  D+   ref/sig    = {Dp_ratio_at_091:.6f}")
print(f"  Ds+    eff(sig) = {Dsp_eff_at_091*100:.3f}%")
print(f"  Ds+    eff(ref) = {Dsp_ref_eff_at_091*100:.3f}%")
print(f"  Ds+  ref/sig    = {Dsp_ratio_at_091:.6f}")

# 5) 플롯: 효율비(ref/sig) vs BDT cut
plt.figure(figsize=(6.4, 4.8))
plt.plot(thresholds, ratio_Dp,  marker='o', label=r'D$^+$: ref/sig')
plt.plot(thresholds, ratio_Dsp, marker='s', label=r'D$_s^+$: ref/sig')
plt.axvline(cut0, linestyle='--', linewidth=1, label=f'cut = {cut0:.2f}')
plt.xlabel('BDT cut')
plt.ylabel('Efficiency ratio (ref / sig)')
#plt.title('Efficiency ratios vs BDT cut')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('eff_ratio_scan.png', dpi=200)
# plt.show()  # 주피터면 활성화

# (선택) 개별 효율도 같이 참고하고 싶으면 아래 보조 플롯 추가
plt.figure(figsize=(6.8, 5.0))
plt.plot(thresholds, eff_Dp_sig,  marker='o', linestyle='-',  label=r'D$^+$ sig')
plt.plot(thresholds, eff_Dp_ref,  marker='o', linestyle='--', label=r'D$^+$ ref')
plt.plot(thresholds, eff_Dsp_sig, marker='s', linestyle='-',  label=r'D$_s^+$ sig')
plt.plot(thresholds, eff_Dsp_ref, marker='s', linestyle='--', label=r'D$_s^+$ ref')
plt.axvline(cut0, linestyle='--', linewidth=1, label=f'cut = {cut0:.2f}')
plt.xlabel('BDT cut')
plt.ylabel('Efficiency')
#plt.title('Efficiencies vs BDT cut')
plt.grid(True, alpha=0.3)
plt.legend(ncol=2)
plt.tight_layout()
plt.savefig('eff_scan_individual.png', dpi=200)
# plt.show()



def eff_binom(df, thr):
    """무가중 효율 및 이항오차"""
    n = len(df)
    if n == 0:
        return np.nan, np.nan
    k = (df['prob_signal'] > thr).sum()
    eff = k / n
    # binomial std (normal approx). 필요시 Clopper-Pearson로 교체 가능.
    se  = np.sqrt(eff * (1 - eff) / n) if 0 < eff < 1 else (0. if eff in (0,1) else np.nan)
    return eff, se

mc_eff_sig, mc_eff_sig_err = [], []
mc_eff_ref, mc_eff_ref_err = [], []
mc_ratio, mc_ratio_err = [], []

for thr in thresholds:
    e_sig, de_sig = eff_binom(df_signal_SR, thr)
    e_ref, de_ref = eff_binom(df_ref_SR,    thr)

    mc_eff_sig.append(e_sig);  mc_eff_sig_err.append(de_sig)
    mc_eff_ref.append(e_ref);  mc_eff_ref_err.append(de_ref)

    # ratio = ref/sig, 단순 오차 전파
    if (e_sig is not np.nan) and (e_sig not in (0,)) and (e_ref is not np.nan):
        r = e_ref / e_sig
        dr = r * np.sqrt( (de_ref/e_ref)**2 + (de_sig/e_sig)**2 ) if (e_ref>0 and e_sig>0) else np.nan
    else:
        r, dr = np.nan, np.nan

    mc_ratio.append(r); mc_ratio_err.append(dr)

print("\n[MC scan of ratio (ref/sig) vs BDT cut]")
for t, r, dr in zip(thresholds, mc_ratio, mc_ratio_err):
    print(f"  cut={t:.6f}: ratio_MC = {r:.7f} ± {dr:.7f}")

# 모드 입력분포 차이 민감도: 동작점(예: 0.91) 근방에서의 변동폭을 시스템atics 후보로
cut0 = 0.91
idx0 = int(np.argmin(np.abs(np.array(thresholds)-cut0)))
# 주변 두세 포인트와 비교(원하는 창 크기 선택)
window_idx = [i for i in range(len(thresholds)) if abs(i-idx0)<=5]
local_vals = [mc_ratio[i] for i in window_idx if not np.isnan(mc_ratio[i])]
if local_vals:
    spread_local = (np.nanmax(local_vals) - np.nanmin(local_vals))
    print(f"\n[입력분포 차이에 의한 민감도 추정] cut≈{cut0:.2f} 주변 ratio_MC 변동폭 = {spread_local:.5f}")
else:
    spread_local = np.nan
