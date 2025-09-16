import uproot
import pandas as pd
import numpy as np
import glob
import joblib
import matplotlib.pyplot as plt
plt.style.use('default')
plt.style.use('belle2')

# ========== 설정 ==========
overall_version = "v7_xgboost"
base_path_sig = "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC"
sig_MC_name = "250216_loose_v7"

# Ds 가중치 파일이 있는 디렉토리(요청 경로)
#DS_WEIGHTED_DIR = f"{base_path_sig}/{sig_MC_name}/weighted"
DS_WEIGHTED_DIR = f"{base_path_sig}"

model_file = f"MC15rd_best_xgb_model_etapip_pipipi_K_loose_{overall_version}.pkl"
best_xgb_model = joblib.load(model_file)
feat_order = best_xgb_model.get_booster().feature_names

branches_pipipi = [
    'Pip_p','etapip_Eta_isSignal','Pip_mcPDG','skimhad','Dp_dz','Pip_pionID',
    'Pip_genMotherID','etapip_Eta_genMotherID','Pip_genMotherPDG','etapip_Eta_genMotherPDG',
    'Dp_cosHelicityAngleMomentum','Pip_dr','Dp_isSignal',
    'Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane','Dp_CMS_p','Dp_M',
]

# 공통 드롭 컬럼
drop_cols = [
    'etapip_Eta_isSignal','Pip_mcPDG','skimhad','Pip_pionID',
    'Pip_genMotherID','etapip_Eta_genMotherID','Pip_genMotherPDG','etapip_Eta_genMotherPDG',
    'Dp_isSignal','Dp_M'
]

# 데이터셋 정의(요소 폴더, 트리이름, 기본 시그널 정의, 추가 모드별 질의, SR 창, Ds 전용 옵션)
DATASETS = {
    # D+ → ηK+ (signal)
    "Dp_sig": {
        "elements": ["DptoetaKp_pipipi", "DptoetaKp_pipipi_cc"],
        "tree": "etapip_pipipi_K",
        "signal_query": "Dp_isSignal==1",
        "extra_query": [
            "Pip_p>0.4", "Pip_pionID<0.01",
            "skimhad==1"
        ],
        "sr": (1.82, 1.91),
        "weighted": False,
        "weight_branch": None,
        "custom_dir": None,   # 기본 경로 패턴 사용
    },
    # D+ → ηπ+ (reference)
    "Dp_ref": {
        "elements": ["Dptoetapip_pipipipi", "Dptoetapip_pipipi_cc"],
        "tree": "etapip_pipipi",
        "signal_query": "Dp_isSignal==1",
        "extra_query": [
            "Pip_p>0.4",
            "skimhad==1"
        ],
        "sr": (1.82, 1.91),
        "weighted": False,
        "weight_branch": None,
        "custom_dir": None,
    },
    # D_s^+ → ηK+ (signal_Dsp)  **가중치 사용 + 디렉토리 override**
    "Ds_sig": {
        "elements": ["DsptoetaKp_pipipi", "DsptoetaKp_pipipi_cc"],  # 사용 안 해도 무방(override)
        "tree": "etapip_pipipi_K",
        "signal_query": "(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & "
                        "((Pip_genMotherPDG == 431 and Pip_mcPDG == 321) | (Pip_genMotherPDG == -431 and Pip_mcPDG == -321))",
        "extra_query": [
            "Pip_p>0.4", "Pip_pionID<0.01",
            "skimhad==1"
        ],
        "sr": (1.92, 2.01),
        "weighted": True,
        "weight_branch": "ds_weight",
        "custom_dir": DS_WEIGHTED_DIR,  # 여기를 사용해서 파일 수집
    },
    # D_s^+ → ηπ+ (reference_Dsp) **가중치 사용 + 디렉토리 override**
    "Ds_ref": {
        "elements": ["Dsptoetapip_pipipi", "Dsptoetapip_pipipi_cc"],
        "tree": "etapip_pipipi",
        "signal_query": "(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & "
                        "((Pip_genMotherPDG == 431 and Pip_mcPDG == 211) | (Pip_genMotherPDG == -431 and Pip_mcPDG == -211))",
        "extra_query": [
            "Pip_p>0.4",
            "skimhad==1"
        ],
        "sr": (1.92, 2.01),
        "weighted": True,
        "weight_branch": "ds_weight",
        "custom_dir": DS_WEIGHTED_DIR,
    },
}

# ========== 유틸 함수 ==========
def collect_files(elements, project, base_dir, custom_dir=None):
    """custom_dir이 주어지면 그 디렉토리에서만 수집; 아니면 elements 폴더 패턴 사용"""
    files = []
    if custom_dir:
        #files = glob.glob(f"{custom_dir}/{project}*.root")
        for elem in elements:
            files.extend(glob.glob(f"{custom_dir}/{elem}/{project}/weighted/{project}*.root"))
        return sorted(files)
    for elem in elements:
        files.extend(glob.glob(f"{base_dir}/{elem}/{project}/{project}*.root"))
    return sorted(files)

def load_df(files, tree, branches, weight_branch=None):
    """필요 시 weight_branch를 추가로 읽음(브랜치가 없으면 skip하지 말고 에러 방지)"""
    # 데이터셋마다 브랜치 목록 구성
    brs = list(branches)
    if weight_branch and (weight_branch not in brs):
        brs.append(weight_branch)

    dfs = []
    for f in files:
        with uproot.open(f) as rf:
            if tree not in rf:
                continue
            # 존재하지 않는 브랜치는 자동으로 제외되도록 try
            try:
                dfs.append(rf[tree].arrays(brs, library="pd"))
            except KeyError:
                # weight_branch가 없는 파일이 있을 경우를 대비
                # 존재하는 브랜치만 다시 시도
                avail = [b for b in brs if b in rf[tree].keys()]
                dfs.append(rf[tree].arrays(avail, library="pd"))
    if not dfs:
        return pd.DataFrame(columns=brs)
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

# ---------- 효율 계산(무가중/가중) ----------
def eff_unweighted(df, thr):
    n = len(df)
    if n == 0:
        return np.nan
    return (df["prob_signal"] > thr).sum() / n

def efferr_unweighted(df, thr):
    n = len(df)
    if n == 0:
        return (np.nan, np.nan)
    k = (df["prob_signal"] > thr).sum()
    p = k / n
    se = np.sqrt(p*(1-p)/n) if 0 < p < 1 else 0.0
    return (p, se)

def eff_weighted(df, thr, wcol):
    if len(df) == 0 or wcol not in df.columns:
        return np.nan
    w = df[wcol].values
    mask = (df["prob_signal"] > thr).values
    s1 = np.sum(w[mask])
    s0 = np.sum(w)
    if s0 <= 0:
        return np.nan
    return s1 / s0

def efferr_weighted(df, thr, wcol):
    """가중 비율의 표준오차 근사: p(1-p)/n_eff,  n_eff=(sum w)^2 / sum w^2"""
    if len(df) == 0 or wcol not in df.columns:
        return (np.nan, np.nan)
    w = df[wcol].values
    if np.sum(w) <= 0:
        return (np.nan, np.nan)
    mask = (df["prob_signal"] > thr).values
    p = np.sum(w[mask]) / np.sum(w)
    sumw = np.sum(w)
    sumw2 = np.sum(w**2)
    if sumw2 == 0:
        return (p, np.nan)
    n_eff = (sumw**2) / sumw2
    se = np.sqrt(p*(1-p)/n_eff) if 0 < p < 1 else 0.0
    return (p, se)

# ========== 메인 파이프라인 ==========
outputs = {}
for key, cfg in DATASETS.items():
    files = collect_files(cfg["elements"], sig_MC_name, base_path_sig, custom_dir=cfg.get("custom_dir"))
    df = load_df(files, cfg["tree"], branches_pipipi, weight_branch=cfg.get("weight_branch"))
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

    outputs[key] = {
        "full": df_with_bdt,
        "sr": df_sr,
        "weighted": cfg["weighted"],
        "weight_branch": cfg["weight_branch"],
    }

# 편의상 바로 변수로 꺼내기(기존 네이밍 유지)
df_signal_combined     = outputs["Dp_sig"]["full"]
df_ref_combined        = outputs["Dp_ref"]["full"]
df_signal_Dsp_combined = outputs["Ds_sig"]["full"]
df_ref_Dsp_combined    = outputs["Ds_ref"]["full"]

df_signal_SR     = outputs["Dp_sig"]["sr"]
df_ref_SR        = outputs["Dp_ref"]["sr"]
df_signal_Dsp_SR = outputs["Ds_sig"]["sr"]
df_ref_Dsp_SR    = outputs["Ds_ref"]["sr"]

print("Dp_sig / Dp_ref / Ds_sig / Ds_ref (full) lengths:",
      len(df_signal_combined), len(df_ref_combined), len(df_signal_Dsp_combined), len(df_ref_Dsp_combined))
print("SR lengths:",
      len(df_signal_SR), len(df_ref_SR), len(df_signal_Dsp_SR), len(df_ref_Dsp_SR))

# ============================
# 분포 플롯 (Ds는 가중치 사용)
# ============================
plt.figure(figsize=(12, 6))
# D+
plt.hist(df_signal_SR['prob_signal'], bins=np.linspace(0, 1, 71),
         histtype='step', label=r'$D^+$', density=True)
plt.hist(df_ref_SR['prob_signal'], bins=np.linspace(0, 1, 71),
         histtype='step', label=r'$D^+$ reference', density=True)
# Ds (가중치)
w_sig = df_signal_Dsp_SR["ds_weight"] if "ds_weight" in df_signal_Dsp_SR.columns else None
w_ref = df_ref_Dsp_SR["ds_weight"]    if "ds_weight" in df_ref_Dsp_SR.columns    else None
plt.hist(df_signal_Dsp_SR['prob_signal'], bins=np.linspace(0, 1, 71),
         histtype='step', label=r'$D_s^+$', density=True, weights=w_sig)
plt.hist(df_ref_Dsp_SR['prob_signal'], bins=np.linspace(0, 1, 71),
         histtype='step', label=r'$D_s^+$ reference', density=True, weights=w_ref)
plt.xlim(0, 1)
plt.xlabel(r'BDT')
plt.ylabel('Candidates (density)')
plt.legend(ncol=2)
plt.tight_layout()
plt.savefig("BDT_output_pipipi.png", dpi=200)
# plt.show()

# ========== 효율/효율비 스캔 ==========
center = 0.92
step = 0.001
num_steps_each_side = 20
thresholds = np.round(
    np.linspace(center - num_steps_each_side*step,
                center + num_steps_each_side*step,
                num_steps_each_side*2 + 1),
    3
).tolist()

def get_at_cut(xlist, ylist, cut):
    if cut in xlist:
        i = xlist.index(cut)
        return ylist[i]
    i = int(np.argmin(np.abs(np.array(xlist) - cut)))
    return ylist[i]

# D+ (무가중)
eff_Dp_sig  = np.array([eff_unweighted(df_signal_SR, thr) for thr in thresholds])
eff_Dp_ref  = np.array([eff_unweighted(df_ref_SR,    thr) for thr in thresholds])
ratio_Dp    = eff_Dp_ref / eff_Dp_sig

# Ds (가중)
eff_Dsp_sig = np.array([eff_weighted(df_signal_Dsp_SR, thr, "ds_weight") for thr in thresholds])
eff_Dsp_ref = np.array([eff_weighted(df_ref_Dsp_SR,    thr, "ds_weight") for thr in thresholds])
ratio_Dsp   = eff_Dsp_ref / eff_Dsp_sig

# 기준점 출력
cut0 = 0.92
Dp_eff_at_091      = get_at_cut(thresholds, eff_Dp_sig,  cut0)
Dp_ref_eff_at_091  = get_at_cut(thresholds, eff_Dp_ref,  cut0)
Dsp_eff_at_091     = get_at_cut(thresholds, eff_Dsp_sig, cut0)
Dsp_ref_eff_at_091 = get_at_cut(thresholds, eff_Dsp_ref, cut0)
Dp_ratio_at_091    = get_at_cut(thresholds, ratio_Dp,    cut0)
Dsp_ratio_at_091   = get_at_cut(thresholds, ratio_Dsp,   cut0)

print(f"[BDT > {cut0:.2f}]")
print(f"  D+     eff(sig) = {Dp_eff_at_091*100:.3f}%")
print(f"  D+     eff(ref) = {Dp_ref_eff_at_091*100:.3f}%")
print(f"  D+   ref/sig    = {Dp_ratio_at_091:.6f}")
print(f"  Ds+    eff(sig) = {Dsp_eff_at_091*100:.3f}%")
print(f"  Ds+    eff(ref) = {Dsp_ref_eff_at_091*100:.3f}%")
print(f"  Ds+  ref/sig    = {Dsp_ratio_at_091:.6f}")

# (보조) 개별 효율 곡선
plt.figure(figsize=(6.8, 5.0))
plt.plot(thresholds, eff_Dp_sig,  marker='o', linestyle='-',  label=r'D$^+$ sig')
plt.plot(thresholds, eff_Dp_ref,  marker='o', linestyle='--', label=r'D$^+$ ref')
plt.plot(thresholds, eff_Dsp_sig, marker='s', linestyle='-',  label=r'D$_s^+$ sig (w)')
plt.plot(thresholds, eff_Dsp_ref, marker='s', linestyle='--', label=r'D$_s^+$ ref (w)')
plt.axvline(cut0, linestyle='--', linewidth=1, label=f'cut = {cut0:.2f}')
plt.xlabel('BDT cut')
plt.ylabel('Efficiency')
plt.grid(True, alpha=0.3)
plt.legend(ncol=2, fontsize='small')
plt.tight_layout()
plt.savefig('eff_scan_individual_pipipi.png', dpi=200)

# --- Errorbar 포함 효율 곡선 ---
# D+ (무가중)
Dp_sig_vals,  Dp_sig_errs  = zip(*[efferr_unweighted(df_signal_SR, thr)     for thr in thresholds])
Dp_ref_vals,  Dp_ref_errs  = zip(*[efferr_unweighted(df_ref_SR,    thr)     for thr in thresholds])

# Ds+ (가중)
Dsp_sig_vals, Dsp_sig_errs = zip(*[efferr_weighted(df_signal_Dsp_SR, thr, "ds_weight") for thr in thresholds])
Dsp_ref_vals, Dsp_ref_errs = zip(*[efferr_weighted(df_ref_Dsp_SR,    thr, "ds_weight") for thr in thresholds])

plt.figure(figsize=(6.8, 5.0))
plt.errorbar(thresholds, Dp_sig_vals,  yerr=Dp_sig_errs,  fmt='o-', capsize=3, label=r'D$^+$ sig')
plt.errorbar(thresholds, Dp_ref_vals,  yerr=Dp_ref_errs,  fmt='o--', capsize=3, label=r'D$^+$ ref')
plt.errorbar(thresholds, Dsp_sig_vals, yerr=Dsp_sig_errs, fmt='s-', capsize=3, label=r'D$_s^+$ sig (w)')
plt.errorbar(thresholds, Dsp_ref_vals, yerr=Dsp_ref_errs, fmt='s--', capsize=3, label=r'D$_s^+$ ref (w)')
plt.axvline(cut0, linestyle='--', linewidth=1, label=f'cut = {cut0:.2f}')
plt.xlabel('BDT cut')
plt.ylabel('Efficiency')
plt.grid(True, alpha=0.3)
plt.legend(ncol=2, fontsize='small')
plt.tight_layout()
plt.savefig('eff_scan_individual_with_err_pipipi.png', dpi=200)
# plt.show()

print("\n[MC scan of ref and sig vs BDT cut]")
for t, r, dr in zip(thresholds, Dp_sig_vals, Dp_sig_errs):
    print(f"  D+ sig  cut={t:.3f}: ratio_MC = {r:.7f} ± {dr:.7f}")
for t, r, dr in zip(thresholds, Dp_ref_vals, Dp_ref_errs):
    print(f"  D+ ref  cut={t:.3f}: ratio_MC = {r:.7f} ± {dr:.7f}")
for t, r, dr in zip(thresholds, Dsp_sig_vals, Dsp_sig_errs):
    print(f"  Ds+ sig  cut={t:.3f}: ratio_MC = {r:.7f} ± {dr:.7f}")
for t, r, dr in zip(thresholds, Dsp_ref_vals, Dsp_ref_errs):
    print(f"  Ds+ ref  cut={t:.3f}: ratio_MC = {r:.7f} ± {dr:.7f}")


# ---- 오차 포함 (D+, Ds 각각) ----
def calc_ratio_with_err(df_sig, df_ref, weighted=False, wcol=None):
    ratios, ratio_errs = [], []
    for thr in thresholds:
        if weighted:
            e_sig, de_sig = efferr_weighted(df_sig, thr, wcol)
            e_ref, de_ref = efferr_weighted(df_ref, thr, wcol)
        else:
            e_sig, de_sig = efferr_unweighted(df_sig, thr)
            e_ref, de_ref = efferr_unweighted(df_ref, thr)
        if (e_sig is not np.nan) and (e_ref is not np.nan) and (e_sig > 0) and (e_ref > 0):
            r  = e_ref / e_sig
            dr = r * np.sqrt( (de_ref/e_ref)**2 + (de_sig/e_sig)**2 )
        else:
            r, dr = np.nan, np.nan
        ratios.append(r); ratio_errs.append(dr)
    return ratios, ratio_errs

ratio_Dp,  ratio_Dp_err  = calc_ratio_with_err(df_signal_SR,    df_ref_SR,    weighted=False)
ratio_Dsp, ratio_Dsp_err = calc_ratio_with_err(df_signal_Dsp_SR, df_ref_Dsp_SR, weighted=True, wcol="ds_weight")

# 표로도 찍기
print("\n[MC scan of ratio (ref/sig) vs BDT cut]")
for t, r, dr in zip(thresholds, ratio_Dp, ratio_Dp_err):
    print(f"  D+  cut={t:.3f}: ratio_MC = {r:.7f} ± {dr:.7f}")
for t, r, dr in zip(thresholds, ratio_Dsp, ratio_Dsp_err):
    print(f"  Ds+ cut={t:.3f}: ratio_MC = {r:.7f} ± {dr:.7f}")

# 효율비 그래프 (오차 포함)
plt.figure(figsize=(6.4, 4.8))
plt.errorbar(thresholds, ratio_Dp,  yerr=ratio_Dp_err,  fmt='o', capsize=3, label=r'D$^+$: ref/sig')
plt.errorbar(thresholds, ratio_Dsp, yerr=ratio_Dsp_err, fmt='s', capsize=3, label=r'D$_s^+$: ref/sig (w)')
plt.axvline(cut0, linestyle='--', linewidth=1, color='gray', label=f'cut = {cut0:.2f}')
plt.xlabel('BDT cut')
plt.ylabel('Efficiency ratio (ref / sig)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('eff_ratio_scan_both_with_err_pipipi.png', dpi=200)

# ---- cut 주변 변동폭(민감도) ----
idx0 = int(np.argmin(np.abs(np.array(thresholds)-cut0)))
window_idx = [i for i in range(len(thresholds)) if abs(i-idx0) <= 5]

local_vals_Dp  = [ratio_Dp[i]  for i in window_idx if not np.isnan(ratio_Dp[i])]
local_vals_Dsp = [ratio_Dsp[i] for i in window_idx if not np.isnan(ratio_Dsp[i])]
spread_local_Dp  = (np.nanmax(local_vals_Dp)  - np.nanmin(local_vals_Dp))  if local_vals_Dp  else np.nan
spread_local_Dsp = (np.nanmax(local_vals_Dsp) - np.nanmin(local_vals_Dsp)) if local_vals_Dsp else np.nan
print(f"\n[민감도 추정] D+  : cut≈{cut0:.2f} 주변 ratio 변동폭 = {spread_local_Dp:.6f}")
print(f"[민감도 추정] Ds+ : cut≈{cut0:.2f} 주변 ratio 변동폭 = {spread_local_Dsp:.6f}")

