import uproot
import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt
plt.style.use('default')
plt.style.use('belle2')

import sys

# =========================
# 설정: Ds 모드(한 셋만 유효)
# =========================
base_path = "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC"

tree_name = sys.argv[1]
if tree_name == "etapip_gg":
  elements = ["Dsptoetapip_gg", "Dsptoetapip_gg_cc"]
  BDT_cut = "0.86"
  histo_title = r"$D^+_s \to \eta_{\gamma\gamma} \pi^+$"
elif tree_name == "etapip_pipipi":
  elements = ["Dsptoetapip_pipipi", "Dsptoetapip_pipipi_cc"]
  BDT_cut = "0.77"
  histo_title = r"$D^+_s \to \eta_{3\pi} \pi^+$"
elif tree_name == "etapip_gg_K":
  elements = ["DsptoetaKp_gg", "DsptoetaKp_gg_cc"]
  BDT_cut = "0.86"
  histo_title = r"$D^+_s \to \eta_{\gamma\gamma} K^+$"
elif tree_name == "etapip_pipipi_K":
  elements = ["DsptoetaKp_pipipi", "DsptoetaKp_pipipi_cc"]
  BDT_cut = "0.77"
  histo_title = r"$D^+_s \to \eta_{3\pi} K^+$"

Dp_M_range = "Dp_M > 0"

# --- Ds 신호 정의(요청하신 cut만 사용; Ds_isSignal 등은 사용하지 않음) ---
if tree_name == "etapip_gg_K" or tree_name == "etapip_pipipi_K":
  signal_cut = (
      "(etapip_Eta_isSignal == 1) & "
      "(Pip_genMotherID == etapip_Eta_genMotherID) & "
      "((Pip_genMotherPDG == 431 and Pip_mcPDG == 321) | "
      "(Pip_genMotherPDG == -431 and Pip_mcPDG == -321))"
  )
elif tree_name == "etapip_gg" or tree_name == "etapip_pipipi":
  signal_cut = (
      "(etapip_Eta_isSignal == 1) & "
      "(Pip_genMotherID == etapip_Eta_genMotherID) & "
      "((Pip_genMotherPDG == 431 and Pip_mcPDG == 211) | "
      "(Pip_genMotherPDG == -431 and Pip_mcPDG == -211))"
  )

# ---  BCS 규칙: 'lowest' 또는 'highest' ---
#BCS_PICK = 'lowest'  # 일반적으론 'highest'가 적합하지만, 요청에 맞춰 기본 'lowest'
BCS_PICK = 'highest'  # 일반적으론 'highest'가 적합하지만, 요청에 맞춰 기본 'lowest'

# =========================
# 데이터 로드 (weighted 전용)
# =========================
file_list = []
if tree_name == "etapip_gg_K" or tree_name == "etapip_pipipi_K":
    for element in elements:
        pattern = f"{base_path}/{element}/260107_loose_v7_less_vars_ntuple/{tree_name}/min_unc_search/{BDT_cut}/weighted/*BDT.root"
        file_list += glob.glob(pattern)
elif tree_name == "etapip_gg" or tree_name == "etapip_pipipi":
    for element in elements:
        pattern = f"{base_path}/{element}/260107_loose_v7_less_vars_ntuple/{tree_name}/ref/min_unc_search/{BDT_cut}/weighted/*BDT.root"
        file_list += glob.glob(pattern)
#for element in elements:
#    pattern = f"{base_path}/{element}/250216_loose_v7/{tree_name}/no_BCS/{BDT_cut}/weighted/*.no_BCS.root"
#    file_list += glob.glob(pattern)

if len(file_list) == 0:
    print("[ERROR] weighted 경로에 파일이 없습니다. 경로나 BDT_cut, tree_name을 확인하세요.")
    sys.exit(1)

branches_all = [
    "__experiment__", "__run__", "__event__", "__production__",
    "Dp_M", "Dp_chiProb", "ds_weight", "BDT",
    # signal_cut에 필요한 브랜치
    "etapip_Eta_isSignal", "Pip_genMotherID", "Pip_genMotherPDG",
    "Pip_mcPDG", "etapip_Eta_genMotherPDG", "etapip_Eta_genMotherID",
]

event_cols = ['__experiment__', '__run__', '__event__', '__production__']
dfs = []
for fn in file_list:
    with uproot.open(fn) as f:
        tree = f[tree_name]
        # 1. Load the individual file into a temporary dataframe
        tmp_df = tree.arrays(branches_all, library="pd")

        # 2. Apply the Dp_M_range filter immediately to save memory
        tmp_df = tmp_df.query(Dp_M_range).copy()

        # 3. Calculate multiplicity for THIS file specifically
        # This counts candidates per unique event within this single .root file
        tmp_df['multiplicity'] = tmp_df.groupby(event_cols)['__event__'].transform('count')

        dfs.append(tmp_df)

df_all = pd.concat(dfs, ignore_index=True)
df_all = df_all.query(Dp_M_range).copy()

# 필수 컬럼 체크
need_cols = ["Dp_chiProb", "ds_weight", "multiplicity", "BDT"]
missing = [c for c in need_cols if c not in df_all.columns]
if missing:
    print("[ERROR] 누락 컬럼:", missing)
    sys.exit(1)

# 이벤트 키
event_cols = ["__experiment__", "__run__", "__event__", "__production__"]

# =========================
# 신호 정의 (Ds 전용 signal_cut)
# =========================
must_cols = ["etapip_Eta_isSignal", "Pip_genMotherID", "etapip_Eta_genMotherID", "Pip_genMotherPDG", "Pip_mcPDG"]
missing2 = [c for c in must_cols if c not in df_all.columns]
if missing2:
    print("[ERROR] signal_cut 평가에 필요한 컬럼이 없습니다:", missing2)
    sys.exit(1)

df_all["isTrueSignal"] = df_all.eval(signal_cut)

# =========================
# 기반 BCS 후보 선택
# =========================
if BCS_PICK == 'lowest':
    key_series = df_all['BDT'].fillna(np.inf)
    bcs_index = key_series.groupby(df_all[event_cols].apply(tuple, axis=1)).idxmin()
elif BCS_PICK == 'highest':
    key_series = df_all['BDT'].fillna(-np.inf)
    bcs_index = key_series.groupby(df_all[event_cols].apply(tuple, axis=1)).idxmax()
else:
    raise ValueError("BCS_PICK must be 'lowest' or 'highest'.")

df_all['bcs_by_bdt'] = False
df_all.loc[bcs_index, 'bcs_by_bdt'] = True

# 이벤트 대표 테이블: 이벤트 가중치, multiplicity_event(최대)
per_event = (
    df_all
    .groupby(event_cols, as_index=False)
    .agg(weight=('ds_weight','first'),
         multiplicity_event=('multiplicity','max'))
)

# BCS로 선택된 후보(이벤트당 1행) + 그 후보가 신호인지
chosen_per_event_df = df_all.loc[bcs_index, event_cols + ['isTrueSignal', 'ds_weight']]
chosen_per_event_df = chosen_per_event_df.rename(columns={'ds_weight':'weight'})

# 이벤트 집합들
signal_events = (
    df_all[df_all['isTrueSignal']]
    .groupby(event_cols, as_index=False)
    .agg(any=('isTrueSignal','any'))
)[event_cols]

multi_events = per_event[per_event['multiplicity_event'] > 1][event_cols]

multi_signal_events = (
    df_all[df_all['multiplicity'] > 1]
    .groupby(event_cols)
    .filter(lambda x: (x['isTrueSignal']).any())
)[event_cols].drop_duplicates()

# =========================
# 가중치 기준 메트릭 계산
# =========================
def sum_event_weights(ev_df):
    if ev_df.empty:
        return 0.0
    return per_event.merge(ev_df, on=event_cols, how='inner')['weight'].sum()

den_w_all = per_event['weight'].sum()                  # 전체 이벤트 가중치 합
w_multi   = sum_event_weights(multi_events)            # 다중후보 이벤트 가중치 합
w_sig_all = sum_event_weights(signal_events)           # 신호 이벤트(신호 후보 ≥1 포함) 가중치 합
w_multi_sig = sum_event_weights(multi_signal_events)   # 다중후보+신호 포함 이벤트 가중치 합

# 다중후보에서 BCS가 '신호'를 택한 이벤트의 가중치 합
chosen_sig_multi_w = (
    chosen_per_event_df[chosen_per_event_df['isTrueSignal']]
    .merge(multi_signal_events, on=event_cols, how='inner')
)['weight'].sum()

# 전체에서 BCS가 '신호'를 택한 이벤트의 가중치 합
correct_signal_w = (
    chosen_per_event_df[chosen_per_event_df['isTrueSignal']]
    .merge(signal_events, on=event_cols, how='inner')
)['weight'].sum()

multi_cand_fraction = 100.0 * w_multi / den_w_all if den_w_all > 0 else np.nan
signal_in_multi_fraction = 100.0 * w_multi_sig / w_multi if w_multi > 0 else np.nan
chosen_signal_fraction = 100.0 * chosen_sig_multi_w / w_multi_sig if w_multi_sig > 0 else np.nan
overall_bcs_eff = 100.0 * correct_signal_w / w_sig_all if w_sig_all > 0 else np.nan

print("=== Weighted BCS Performance Metrics (Ds, bdt-based, pick: {}) ===".format(BCS_PICK))
print(f"1. Multi-Candidate Event Fraction (%)       : {multi_cand_fraction:.2f}")
print(f"2. Signal Contained in Multi-Cands (%)      : {signal_in_multi_fraction:.2f}")
print(f"3. Signal Chosen Among Multi-Cands (%)      : {chosen_signal_fraction:.2f}")
print(f"4. Overall BCS Efficiency (%)               : {overall_bcs_eff:.2f}")

# =========================
# multiplicity 히스토그램 (1,2,3,4,5+)
#  - 이벤트 단위(max 규칙)
#  - unweighted / weighted 둘 다 저장
# =========================
labels = ['1','2','3','4','5+']
m_clip = per_event['multiplicity_event'].clip(upper=5)

# Unweighted
counts_unw = [(m_clip == k).sum() for k in [1,2,3,4,5]]
total_events_hist = sum(counts_unw)
multi_events_hist = sum(counts_unw[1:])
frac_hist_unw = 100.0 * multi_events_hist / total_events_hist if total_events_hist > 0 else np.nan

# Weighted
w_by_bin = []
for k in [1,2,3,4,5]:
    mask = (m_clip == k)
    w_sum_k = per_event.loc[mask, 'weight'].sum()
    w_by_bin.append(w_sum_k)
w_total = sum(w_by_bin)
w_multi_hist = sum(w_by_bin[1:])
frac_hist_w = 100.0 * w_multi_hist / w_total if w_total > 0 else np.nan

print("\n[CHECK] multi_cand_fraction vs histogram (weighted)")
print(f"metric={multi_cand_fraction:.6f}  hist={frac_hist_w:.6f}  diff={abs(multi_cand_fraction - frac_hist_w):.6f}")

# 그림 저장
plt.figure(figsize=(6.8, 4.6))
plt.bar(labels, counts_unw)
plt.title(f'{histo_title}')
plt.xlabel('Multiplicity')
plt.ylabel('Number of events')
for i, c in enumerate(counts_unw):
    plt.text(i, c, str(c), ha='center', va='bottom', fontsize=10)
plt.tight_layout()
plt.savefig(f'multiplicity_hist_unweighted_BDT_{tree_name}.png', dpi=160)
plt.close()

plt.figure(figsize=(6.8, 4.6))
plt.bar(labels, w_by_bin)
plt.title(f'{histo_title}')
plt.xlabel('Multiplicity')
plt.ylabel('Number of events')
for i, c in enumerate(w_by_bin):
    plt.text(i, c, f"{c:.2f}", ha='center', va='bottom', fontsize=10)
plt.tight_layout()
plt.savefig(f'multiplicity_hist_weighted_BDT_{tree_name}.png', dpi=160)
plt.close()

print(f"[INFO] Saved histograms: multiplicity_hist_unweighted.png, multiplicity_hist_weighted_BDT_{tree_name}.png")

