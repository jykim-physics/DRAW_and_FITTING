import uproot
import pandas as pd
import numpy as np
import glob
import joblib
import matplotlib.pyplot as plt
plt.style.use('default')
plt.style.use('belle2')

# ========== 설정 ==========
overall_version = "v7_xgboost_angle_cut"
base_path_sig = "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC"
sig_MC_name = "250216_loose_v7"

model_file = f"MC15rd_best_xgb_model_etapip_gg_K_loose_{overall_version}.pkl"
best_xgb_model = joblib.load(model_file)
feat_order = best_xgb_model.get_booster().feature_names

branches_gg = [
    'Pip_p','etapip_Eta_isSignal','Pip_mcPDG','skimhad','Dp_dz','Pip_pionID',
    'Pip_genMotherID','etapip_Eta_genMotherID','Pip_genMotherPDG','etapip_Eta_genMotherPDG',
    'Dp_cosHelicityAngleMomentum','Pip_dr','Dp_isSignal',
    'Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane','Dp_CMS_p','etapip_Eta_Easym','Dp_M',
    'etapip_Eta_daughterDiffOfPhi_0_1','etapip_Eta_daughterAngle_0_1'
]

# 공통 드롭 컬럼
drop_cols = [
    'etapip_Eta_isSignal','Pip_mcPDG','skimhad','Pip_pionID',
    'Pip_genMotherID','etapip_Eta_genMotherID','Pip_genMotherPDG','etapip_Eta_genMotherPDG',
    'Dp_isSignal','Dp_M'
]

# 데이터셋 정의(요소 폴더, 트리이름, 기본 시그널 정의, 추가 모드별 질의, SR 창)
DATASETS = {
    # D+ → ηK+ (signal)
    "Dp_sig": {
        "elements": ["DptoetaKp_gg", "DptoetaKp_gg_cc"],
        "tree": "etapip_gg_K",
        "signal_query": "Dp_isSignal==1",
        "extra_query": [
            "Pip_p>0.4", "Pip_pionID<0.01",
            "abs(etapip_Eta_daughterDiffOfPhi_0_1)<1.8",
            "etapip_Eta_daughterAngle_0_1<1.6",
            "skimhad==1"
        ],
        "sr": (1.78, 1.94)
    },
    # D+ → ηπ+ (reference)
    "Dp_ref": {
        "elements": ["Dptoetapip_gg", "Dptoetapip_gg_cc"],
        "tree": "etapip_gg",
        "signal_query": "Dp_isSignal==1",
        "extra_query": [
            "Pip_p>0.4",
            "abs(etapip_Eta_daughterDiffOfPhi_0_1)<1.8",
            "etapip_Eta_daughterAngle_0_1<1.6",
            "skimhad==1"
        ],
        "sr": (1.78, 1.94)
    },
    # D_s^+ → ηK+ (signal_Dsp)
    "Ds_sig": {
        "elements": ["DsptoetaKp_gg", "DsptoetaKp_gg_cc"],
        "tree": "etapip_gg_K",
        # gen-mother 일치 & PDG 일치 조건
        "signal_query": "(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & " \
                        "((Pip_genMotherPDG == 431 and Pip_mcPDG == 321) | (Pip_genMotherPDG == -431 and Pip_mcPDG == -321))",
        "extra_query": [
            "Pip_p>0.4", "Pip_pionID<0.01",
            "abs(etapip_Eta_daughterDiffOfPhi_0_1)<1.8",
            "etapip_Eta_daughterAngle_0_1<1.6",
            "skimhad==1"
        ],
        "sr": (1.88, 2.04)
    },
    # D_s^+ → ηπ+ (reference_Dsp)
    "Ds_ref": {
        "elements": ["Dsptoetapip_gg", "Dsptoetapip_gg_cc"],
        "tree": "etapip_gg",
        "signal_query": "(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & " \
                        "((Pip_genMotherPDG == 431 and Pip_mcPDG == 211) | (Pip_genMotherPDG == -431 and Pip_mcPDG == -211))",
        "extra_query": [
            "Pip_p>0.4",
            "abs(etapip_Eta_daughterDiffOfPhi_0_1)<1.8",
            "etapip_Eta_daughterAngle_0_1<1.6",
            "skimhad==1"
        ],
        "sr": (1.88, 2.04)
    },
}

# ========== 유틸 함수 ==========
def collect_files(elements, project, base_dir):
    files = []
    for elem in elements:
        files.extend(glob.glob(f"{base_dir}/{elem}/{project}/{project}*.root"))
    return files

def load_df(files, tree, branches):
    dfs = []
    for f in files:
        with uproot.open(f) as rf:
            if tree not in rf:
                continue
            dfs.append(rf[tree].arrays(branches, library="pd"))
    if not dfs:
        return pd.DataFrame(columns=branches)
    return pd.concat(dfs, ignore_index=True)

def apply_queries(df, queries):
    for q in queries:
        df = df.query(q)
    return df

def add_bdt_score(df_raw, model, drop_cols, feat_order):
    # 드롭/정렬
    X = df_raw.drop(columns=drop_cols, errors='ignore')
    X = X.reindex(columns=feat_order)
    # 예측
    proba = model.predict_proba(X)
    out = df_raw.copy()
    out["prob_signal"] = proba[:, 1]
    return out

def select_sr(df, sr_range):
    lo, hi = sr_range
    return df.query(f"Dp_M>{lo} & Dp_M<{hi}")

# ========== 메인 파이프라인 ==========
outputs = {}
for key, cfg in DATASETS.items():
    files = collect_files(cfg["elements"], sig_MC_name, base_path_sig)
    df = load_df(files, cfg["tree"], branches_gg)
    if df.empty:
        print(f"[WARN] {key}: no entries loaded.")
        outputs[key] = {"full": df, "sr": df}
        continue

    # 시그널 정의 + 추가 컷
    df = apply_queries(df, [cfg["signal_query"]])
    df = apply_queries(df, cfg["extra_query"])

    # prob_signal 추가
    df_with_bdt = add_bdt_score(df, best_xgb_model, drop_cols, feat_order)

    # SR 선택
    df_sr = select_sr(df_with_bdt, cfg["sr"])

    outputs[key] = {"full": df_with_bdt, "sr": df_sr}

# 편의상 바로 변수로 꺼내기(기존 네이밍 유지)
df_signal_combined   = outputs["Dp_sig"]["full"]
df_ref_combined      = outputs["Dp_ref"]["full"]
df_signal_Dsp_combined = outputs["Ds_sig"]["full"]
df_ref_Dsp_combined    = outputs["Ds_ref"]["full"]

df_signal_SR     = outputs["Dp_sig"]["sr"]
df_ref_SR        = outputs["Dp_ref"]["sr"]
df_signal_Dsp_SR = outputs["Ds_sig"]["sr"]
df_ref_Dsp_SR    = outputs["Ds_ref"]["sr"]

# (선택) 확인 출력
print("Dp_sig / Dp_ref / Ds_sig / Ds_ref (full) lengths:",
      len(df_signal_combined), len(df_ref_combined), len(df_signal_Dsp_combined), len(df_ref_Dsp_combined))
print("SR lengths:",
      len(df_signal_SR), len(df_ref_SR), len(df_signal_Dsp_SR), len(df_ref_Dsp_SR))



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
plt.xlabel(r'BDT')
plt.tight_layout()
plt.savefig(f"test.png")
plt.show()
print(f"D+ eff: {len(df_signal_SR.query('prob_signal>0.91'))/len(df_signal_SR)*100}%")
print(f"D+ ref eff: {len(df_ref_SR.query('prob_signal>0.91'))/len(df_ref_SR)*100}%")
print(f"Ds+ eff: {len(df_signal_Dsp_SR.query('prob_signal>0.91'))/len(df_signal_Dsp_SR)*100}%")
print(f"Ds+ ref eff: {len(df_ref_Dsp_SR.query('prob_signal>0.91'))/len(df_ref_Dsp_SR)*100}%")

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
