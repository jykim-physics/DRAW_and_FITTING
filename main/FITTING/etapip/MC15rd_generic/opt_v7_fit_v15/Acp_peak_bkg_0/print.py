#!/usr/bin/env python3
import ROOT

# ============================================================
# Input files
# ============================================================

# etapip_gg_K
#file_ref1 = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_plus_0.86_KDE_fixed_2nd_cheby_weighted.root"
#file_ref2 = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_minus_0.86_KDE_fixed_2nd_cheby_weighted.root"

#file_nom1 = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_plus_0.86_KDE_fixed_2nd_cheby_Acp_peak_syst_nominal_weighted.root"
#file_nom2 = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_minus_0.86_KDE_fixed_2nd_cheby_Acp_peak_syst_nominal_weighted.root"

#file_plus1 = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_plus_0.86_KDE_fixed_2nd_cheby_Acp_peak_syst_plus_weighted.root"
#file_plus2 = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_minus_0.86_KDE_fixed_2nd_cheby_Acp_peak_syst_plus_weighted.root"

#file_minus1 = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_plus_0.86_KDE_fixed_2nd_cheby_Acp_peak_syst_minus_weighted.root"
#file_minus2 = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_minus_0.86_KDE_fixed_2nd_cheby_Acp_peak_syst_minus_weighted.root"

# etapip_ppipi_K
file_ref1 = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_plus_0.77_KDE_fixed_2nd_cheby_weighted.root"
file_ref2 = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_minus_0.77_KDE_fixed_2nd_cheby_weighted.root"

file_nom1 = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_plus_0.77_KDE_fixed_2nd_cheby_Acp_peak_syst_nominal_weighted.root"
file_nom2 = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_minus_0.77_KDE_fixed_2nd_cheby_Acp_peak_syst_nominal_weighted.root"

file_plus1 = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_plus_0.77_KDE_fixed_2nd_cheby_Acp_peak_syst_plus_weighted.root"
file_plus2 = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_minus_0.77_KDE_fixed_2nd_cheby_Acp_peak_syst_plus_weighted.root"

file_minus1 = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_plus_0.77_KDE_fixed_2nd_cheby_Acp_peak_syst_minus_weighted.root"
file_minus2 = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_minus_0.77_KDE_fixed_2nd_cheby_Acp_peak_syst_minus_weighted.root"


params = [
    "Acp",
    "Acp_Ds",
]


pairs = {
    "reference": (file_ref1, file_ref2),
    "nominal":   (file_nom1, file_nom2),
    "plus":      (file_plus1, file_plus2),
    "minus":     (file_minus1, file_minus2),
}


# ============================================================
# Helper functions
# ============================================================

def get_fit_result(path, objname="jykim"):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise RuntimeError(f"Cannot open file: {path}")

    result = f.Get(objname)
    if not result:
        raise RuntimeError(f"Cannot find object '{objname}' in file: {path}")

    # keep file alive
    result._file = f
    return result


def get_param_value(fit_result, name):
    par = fit_result.floatParsFinal().find(name)

    if not par:
        par = fit_result.constPars().find(name)

    if not par:
        raise RuntimeError(f"Cannot find parameter: {name}")

    return par.getVal(), par.getError()


def get_values_from_file(path, params):
    result = get_fit_result(path)
    values = {}

    for p in params:
        val, err = get_param_value(result, p)
        values[p] = {
            "val": val,
            "err": err,
        }

    return values


def average_pair(file_plus_charge, file_minus_charge, params):
    vals1 = get_values_from_file(file_plus_charge, params)
    vals2 = get_values_from_file(file_minus_charge, params)

    avg = {}

    for p in params:
        v1 = vals1[p]["val"]
        v2 = vals2[p]["val"]

        e1 = vals1[p]["err"]
        e2 = vals2[p]["err"]

        avg_val = 0.5 * (v1 + v2)

        # 참고용 error: 두 fit을 독립이라고 보면 0.5 * sqrt(e1^2 + e2^2)
        # 같은 dataset/systematic 비교 목적이면 central shift가 더 중요함.
        avg_err = 0.5 * (e1**2 + e2**2) ** 0.5

        avg[p] = {
            "plus_charge_val": v1,
            "minus_charge_val": v2,
            "avg_val": avg_val,
            "plus_charge_err": e1,
            "minus_charge_err": e2,
            "avg_err": avg_err,
        }

    return avg


# ============================================================
# Main
# ============================================================

all_results = {}

for label, (f1, f2) in pairs.items():
    all_results[label] = average_pair(f1, f2, params)


print()
print("Averaged values")
print("average = (CMS_p_plus + CMS_p_minus) / 2")
print()

print(
    f"{'Case':<12} "
    f"{'Parameter':<10} "
    f"{'p_plus':>15} "
    f"{'p_minus':>15} "
    f"{'Average':>15} "
    f"{'Avg_err':>15}"
)
print("-" * 90)

for label in ["reference", "nominal", "plus", "minus"]:
    for p in params:
        r = all_results[label][p]

        print(
            f"{label:<12} "
            f"{p:<10} "
            f"{r['plus_charge_val']:>15.8f} "
            f"{r['minus_charge_val']:>15.8f} "
            f"{r['avg_val']:>15.8f} "
            f"{r['avg_err']:>15.8f}"
        )

print()
print("Comparison with reference")
print()

print(
    f"{'Parameter':<10} "
    f"{'Reference':>15} "
    f"{'Case':<12} "
    f"{'Average':>15} "
    f"{'Diff':>15} "
    f"{'AbsDiff':>15}"
)
print("-" * 85)

for p in params:
    ref_avg = all_results["reference"][p]["avg_val"]

    diffs = {}

    for label in ["nominal", "plus", "minus"]:
        avg_val = all_results[label][p]["avg_val"]
        diff = avg_val - ref_avg
        abs_diff = abs(diff)

        diffs[label] = {
            "avg_val": avg_val,
            "diff": diff,
            "abs_diff": abs_diff,
        }

        print(
            f"{p:<10} "
            f"{ref_avg:>15.8f} "
            f"{label:<12} "
            f"{avg_val:>15.8f} "
            f"{diff:>15.8f} "
            f"{abs_diff:>15.8f}"
        )

    max_label = max(diffs, key=lambda k: diffs[k]["abs_diff"])
    max_info = diffs[max_label]

    print(
        f"--> {p}: largest difference = {max_label}, "
        f"Diff = {max_info['diff']:.8f}, "
        f"AbsDiff = {max_info['abs_diff']:.8f}"
    )
    print()
