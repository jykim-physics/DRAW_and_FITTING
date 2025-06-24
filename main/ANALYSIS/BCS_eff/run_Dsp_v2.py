import uproot
import pandas as pd
import numpy as np
import glob

# --- 설정 ---
base_path = "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC"
tree_name = "etapip_gg"
elements = ["Dsptoetapip_gg", "Dsptoetapip_gg_cc"]
BDT_cut = 0.83
tree_name = "etapip_pipipi"
elements = ["Dsptoetapip_pipipi", "Dsptoetapip_pipipi_cc"]
BDT_cut = 0.74
tree_name = "etapip_gg_K"
elements = ["DsptoetaKp_gg", "DsptoetaKp_gg_cc"]
BDT_cut = 0.91
tree_name = "etapip_pipipi_K"
elements = ["DsptoetaKp_pipipi", "DsptoetaKp_pipipi_cc"]
BDT_cut = 0.92
Dp_M_range = "Dp_M > 0"

signal_cut = (
    "(etapip_Eta_isSignal == 1) & "
    "(Pip_genMotherID == etapip_Eta_genMotherID) & "
    "((Pip_genMotherPDG == 431 and Pip_mcPDG == 211) | "
    "(Pip_genMotherPDG == -431 and Pip_mcPDG == -211))"
)
signal_cut = (
    "(etapip_Eta_isSignal == 1) & "
    "(Pip_genMotherID == etapip_Eta_genMotherID) & "
    "((Pip_genMotherPDG == 431 and Pip_mcPDG == 321) | "
    "(Pip_genMotherPDG == -431 and Pip_mcPDG == -321))"
)

# --- 데이터 로드 ---
file_list = []
for element in elements:
    pattern = f"{base_path}/{element}/250216_loose_v7/{tree_name}/no_BCS/{BDT_cut}/weighted/*.no_BCS.root"
    file_list += glob.glob(pattern)

branches_all = [
    "__experiment__", "__run__", "__event__", "__production__",
    "multiplicity", "Dp_M", "rank", "ds_weight",
    "etapip_Eta_isSignal", "Pip_genMotherID", "Pip_genMotherPDG",
    "Pip_mcPDG", "etapip_Eta_genMotherPDG", "etapip_Eta_genMotherID"
]

dataframes = []
for file_name in file_list:
    with uproot.open(file_name) as file:
        tree = file[tree_name]
        df_temp = tree.arrays(branches_all, library="pd")
        dataframes.append(df_temp)

df_all = pd.concat(dataframes, ignore_index=True)
df_all = df_all.query(Dp_M_range)

# 이벤트 구분 키
event_cols = ["__experiment__", "__run__", "__event__", "__production__"]

# 진짜 시그널 정의
df_all["isTrueSignal"] = df_all.eval(signal_cut)

# =====================
#     메트릭 계산
# =====================

# 1. 전체 시그널 이벤트의 가중치 합
total_signal_weight = (
    df_all[df_all["isTrueSignal"]]
    .groupby(event_cols)["ds_weight"].first()
    .sum()
)

# 2. 다중 후보 이벤트의 가중치 합
multi_cand_events_weight = (
    df_all[df_all["multiplicity"] > 1]
    .groupby(event_cols)["ds_weight"].first()
    .sum()
)

# 3. 시그널 포함된 다중 후보 이벤트의 가중치 합
#multi_cand_signals_weight = (
#    df_all[(df_all["multiplicity"] > 1) & (df_all["isTrueSignal"])]
#    .groupby(event_cols)["ds_weight"].first()
#    .sum()
#)
multi_cand_signals_weight = (
    df_all[df_all["multiplicity"] > 1]
    .groupby(event_cols)
    .filter(lambda x: (x["isTrueSignal"] == True).any())
    .drop_duplicates(subset=event_cols)
    .groupby(event_cols)["ds_weight"].first()
    .sum()
)


# 4. 다중 후보 중에서 시그널이고 rank==1인 이벤트의 가중치 합
chosen_signals_weight = (
    df_all[(df_all["multiplicity"] > 1) & (df_all["isTrueSignal"]) & (df_all["rank"] == 1)]
    .groupby(event_cols)["ds_weight"].first()
    .sum()
)

# 5. 전체에서 rank==1인 시그널 이벤트의 가중치 합
overall_bcs_weight = (
    df_all[(df_all["isTrueSignal"]) & (df_all["rank"] == 1)]
    .groupby(event_cols)["ds_weight"].first()
    .sum()
)

# =====================
#     출력 계산
# =====================

multi_cand_fraction = 100 * multi_cand_events_weight / df_all.groupby(event_cols)["ds_weight"].first().sum()
signal_in_multi_fraction = 100 * multi_cand_signals_weight / multi_cand_events_weight
chosen_signal_fraction = 100 * chosen_signals_weight / multi_cand_signals_weight
overall_bcs_eff = 100 * overall_bcs_weight / total_signal_weight

# =====================
#     출력
# =====================

print("=== Weighted BCS Performance Metrics (Method A) ===")
print(f"1. Multi-Candidate Event Fraction (%)       : {multi_cand_fraction:.2f}")
print(f"2. Signal Contained in Multi-Cands (%)      : {signal_in_multi_fraction:.2f}")
print(f"3. Signal Chosen Among Multi-Cands (%)      : {chosen_signal_fraction:.2f}")
print(f"4. Overall BCS Efficiency (%)               : {overall_bcs_eff:.2f}")

