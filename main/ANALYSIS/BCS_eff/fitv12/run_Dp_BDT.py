import uproot
import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt
plt.style.use('default')
plt.style.use('belle2')

import os
import sys

# -----------------------------
# 사용자 설정 (채널/BDT 컷 등)
# -----------------------------
base_path = "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC"

# 하나만 켜서 사용하세요 (현재는 마지막 셋이 유효)

tree_name = sys.argv[1]
if tree_name == "etapip_gg":
  elements = ["Dptoetapip_gg", "Dptoetapip_gg_cc"]
  BDT_cut = "0.86"
  histo_title = r"$D^+ \to \eta_{\gamma\gamma} \pi^+$"
elif tree_name == "etapip_pipipi":
  elements = ["Dptoetapip_pipipi", "Dptoetapip_pipipi_cc"]
  BDT_cut = "0.77"
  histo_title = r"$D^+ \to \eta_{3\pi} \pi^+$"
elif tree_name == "etapip_gg_K":
  elements = ["DptoetaKp_gg", "DptoetaKp_gg_cc"]
  BDT_cut = "0.86"
  histo_title = r"$D^+ \to \eta_{\gamma\gamma} K^+$"
elif tree_name == "etapip_pipipi_K":
  elements = ["DptoetaKp_pipipi", "DptoetaKp_pipipi_cc"]
  BDT_cut = "0.77"
  histo_title = r"$D^+ \to \eta_{3\pi} K^+$"


Dp_M_range = "Dp_M > 0"
# Dp_M_range = "Dp_M > 1.78 and Dp_M < 1.94"

# BCS 선택 규칙: 'lowest' (요청) 또는 'highest' (일반적인 사용)
#BCS_PICK = 'lowest'   # <-- 필요 시 'highest' 로 변경
BCS_PICK = 'highest'   # <-- 필요 시 'highest' 로 변경

# -----------------------------
# 파일 로딩
# -----------------------------
file_list = []
if tree_name == "etapip_gg_K" or tree_name == "etapip_pipipi_K":
    for element in elements:
        pattern = f"{base_path}/{element}/260107_loose_v7_less_vars_ntuple/{tree_name}/min_unc_search/{BDT_cut}/*BDT.root"
        file_list += glob.glob(pattern)
elif tree_name == "etapip_gg" or tree_name == "etapip_pipipi":
    for element in elements:
        pattern = f"{base_path}/{element}/260107_loose_v7_less_vars_ntuple/{tree_name}/ref/min_unc_search/{BDT_cut}/*BDT.root"
        file_list += glob.glob(pattern)

if len(file_list) == 0:
    print("[WARN] 매칭되는 파일이 없습니다. 경로/패턴을 확인하세요.")
    sys.exit(0)

branches_all = ["__experiment__", "__run__", "__event__", "__production__",
                "Dp_isSignal","Dp_M","Dp_chiProb", "BDT"]

event_cols = ['__experiment__', '__run__', '__event__', '__production__']
dfs = []
#for fn in file_list:
#    with uproot.open(fn) as f:
#        tree = f[tree_name]
#        dfs.append(tree.arrays(branches_all, library="pd"))
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
df_all = df_all.rename(columns={"Dp_isSignal": "isSignal"})

# -----------------------------------------
# (A) 이벤트 단위 BCS 후보 선정
# -----------------------------------------
# NaN 안전 처리 (최솟값/최댓값 계산이 가능하도록)
if BCS_PICK == 'lowest':
    key_series = df_all['BDT'].fillna(np.inf)   # 낮은 값 선택 시, NaN은 배제되도록 inf로
    bcs_index = key_series.groupby(df_all[event_cols].apply(tuple, axis=1)).idxmin()
elif BCS_PICK == 'highest':
    key_series = df_all['BDT'].fillna(-np.inf)  # 높은 값 선택 시, NaN은 배제되도록 -inf로
    bcs_index = key_series.groupby(df_all[event_cols].apply(tuple, axis=1)).idxmax()
else:
    raise ValueError("BCS_PICK must be 'lowest' or 'highest'.")

# 새 컬럼: BCS로 선택된 후보(True)
df_all['bcs_by_bdt'] = False
df_all.loc[bcs_index, 'bcs_by_bdt'] = True

# -----------------------------------------
# (B) BCS 성능 지표 계산 ( BCS 기준)
# -----------------------------------------
# 전체 signal 이벤트 수 (이벤트 중 신호 후보 1개 이상 포함한 이벤트)
total_signal_events = (
    df_all[df_all['isSignal'] == 1][event_cols]
    .drop_duplicates()
    .shape[0]
)

# 1) Multi-Candidate Event Fraction
multi_cand_events_df = (
    df_all[df_all['multiplicity'] > 1][event_cols]
    .drop_duplicates()
)
multi_cand_fraction = 100.0 * multi_cand_events_df.shape[0] / df_all[event_cols].drop_duplicates().shape[0]

# 2) Signal Contained in Multi-Candidate Events
multi_signal_events_df = (
    df_all[df_all['multiplicity'] > 1]
    .groupby(event_cols)
    .filter(lambda x: (x['isSignal'] == 1).any())[event_cols]
    .drop_duplicates()
)
n_multi_cand_events = multi_cand_events_df.shape[0]
n_multi_signal_events = multi_signal_events_df.shape[0]
signal_in_multi_fraction = 100.0 * (n_multi_signal_events / n_multi_cand_events) if n_multi_cand_events > 0 else np.nan

# 3) Signal Chosen Among Multi-Cands (BCS가 신호를 택한 비율)
#    다중후보 & 신호포함 이벤트 집합에서, bcs_by_bdt 로 선택된 하나의 후보가 신호인지 체크
chosen_per_event_df = df_all[df_all['bcs_by_bdt']].copy()  # 이벤트당 1행
chosen_in_multi_sig_df = chosen_per_event_df.merge(multi_signal_events_df, on=event_cols, how='inner')
n_chosen_signal_in_multi = (chosen_in_multi_sig_df['isSignal'] == 1).sum()
chosen_signal_fraction = 100.0 * (n_chosen_signal_in_multi / n_multi_signal_events) if n_multi_signal_events > 0 else np.nan

# 4) Overall BCS Efficiency (BCS가 신호 이벤트에서 신호후보를 택한 비율)
n_correct_signal_picked = (
    chosen_per_event_df[chosen_per_event_df['isSignal'] == 1][event_cols]
    .drop_duplicates()
    .shape[0]
)
overall_bcs_eff = 100.0 * (n_correct_signal_picked / total_signal_events) if total_signal_events > 0 else np.nan

print("=== BCS Performance Metrics (BDT-based, pick: {}) ===".format(BCS_PICK))
print(f"1. Multi-Candidate Event Fraction (%)       : {multi_cand_fraction:.2f}")
print(f"2. Signal Contained in Multi-Cands (%)      : {signal_in_multi_fraction:.2f}")
print(f"3. Signal Chosen Among Multi-Cands (%)      : {chosen_signal_fraction:.2f}")
print(f"4. Overall BCS Efficiency (%)               : {overall_bcs_eff:.2f}")

# -------------------------------------------------
# (C) multiplicity 히스토그램 (이벤트 단위 1,2,3,4,5+)
# -------------------------------------------------
# 이벤트 단위로 중복 제거하여 multiplicity 분포를 집계
unique_events = df_all[event_cols + ['multiplicity']].drop_duplicates(subset=event_cols).copy()

# 5+ bin으로 묶기 (클리핑)
m_clipped = unique_events['multiplicity'].clip(upper=5)

# 카운트 확보 (1~5)
bins_k = [1,2,3,4,5]
counts = [(m_clipped == k).sum() for k in bins_k]


# unique_events, counts 는 이미 이전 코드에서 만든 것을 사용
total_events_hist = sum(counts)
multi_events_hist = sum(counts[1:])   # bin2+bin3+bin4+bin5
frac_hist = 100.0 * multi_events_hist / total_events_hist

print("multi_cand_fraction (earlier):", f"{multi_cand_fraction:.6f}")
print("multi_cand_fraction (from hist):", f"{frac_hist:.6f}")
print("abs diff:", abs(multi_cand_fraction - frac_hist))

# 0) 진단: 동일 이벤트에서 multiplicity가 서로 다른 경우가 있는지 확인
audit = (df_all
         .groupby(event_cols)['multiplicity']
         .agg(n_rows='size', n_unique='nunique', m_min='min', m_max='max',
              n_nan=lambda s: s.isna().sum())
         .reset_index())

n_inconsistent = (audit['n_unique'] > 1).sum()
n_allnan      = (audit['n_nan'] == audit['n_rows']).sum()
print(f"[CHECK] 이벤트 내 multiplicity가 서로 다른 경우: {n_inconsistent}")
print(f"[CHECK] 해당 이벤트가 모두 NaN인 경우: {n_allnan}")

# 1) 이벤트별 multiplicity를 일관되게 하나로 확정 (여기서는 'max' 사용)
per_event = (df_all
             .groupby(event_cols, as_index=False)['multiplicity']
             .max()   # == 이벤트 안에 한 번이라도 2개 이상 있으면 2 이상으로 보장
             .rename(columns={'multiplicity': 'multiplicity_event'}))

# 2) 히스토그램 카운트(1,2,3,4,5+) 및 분모/분자 정의를 '전체 이벤트 수'로 통일
den_all = per_event.shape[0]
m_clip = per_event['multiplicity_event'].clip(upper=5)

bins = [1,2,3,4,5]
counts = [(m_clip == k).sum() for k in bins]  # NaN은 어떤 bin에도 들어가지 않음

# (A) 히스토그램 기반 분자/분모를 '전체 이벤트 수(den_all)'로 맞춤
multi_from_bins = sum(counts[1:])  # 2,3,4,5+
frac_from_bins_den_all = 100.0 * multi_from_bins / den_all

# (B) 이벤트 테이블에서 직접 계산 (가장 정확)
multi_exact = (per_event['multiplicity_event'] > 1).sum()
frac_exact = 100.0 * multi_exact / den_all

print(f"[CHECK] multi_cand_fraction (exact)        : {frac_exact:.6f}")
print(f"[CHECK] multi_cand_fraction (from bins)    : {frac_from_bins_den_all:.6f}")
print(f"[CHECK] abs diff                           : {abs(frac_exact - frac_from_bins_den_all):.6f}")


labels = ['1','2','3','4','5+']

# 막대그래프
plt.figure(figsize=(6.8, 4.6))
plt.bar(labels, counts)
plt.title(f'{histo_title}')
plt.xlabel('Multiplicity')
plt.ylabel('Number of events')
# 막대 위에 개수 표시(선택)
for i, c in enumerate(counts):
    plt.text(i, c, str(c), ha='center', va='bottom', fontsize=10)
plt.tight_layout()
plt.savefig(f'multiplicity_hist_BDT_{tree_name}.png', dpi=160)
plt.show()

print(f"[INFO] Saved histogram as 'multiplicity_hist_BDT_{tree_name}.png'")
