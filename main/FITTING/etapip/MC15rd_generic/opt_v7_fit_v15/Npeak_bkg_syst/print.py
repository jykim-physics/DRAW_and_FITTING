#!/usr/bin/env python3
import os
import re
import ROOT

# etapip_gg_K
#file_ref = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_all_0.86_KDE_fixed_2nd_cheby_weighted.root"
#file_cmp1 = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_all_0.86_KDE_fixed_2nd_cheby_Npeak_bkg_sys_plus_weighted.txt"
#file_cmp2 = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_all_0.86_KDE_fixed_2nd_cheby_Npeak_bkg_sys_minus_weighted.txt"
# etapip_pipipi_K
file_ref = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_all_0.77_KDE_fixed_2nd_cheby_weighted.root"
file_cmp1 = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_all_0.77_KDE_fixed_2nd_cheby_Npeak_bkg_sys_plus_weighted.root"
file_cmp2 = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_all_0.77_KDE_fixed_2nd_cheby_Npeak_bkg_sys_minus_weighted.root"

params = [
    "N_total",
    "N_total_Ds",
    "Acp",
    "Acp_Ds",
    "Nbkg_total",
]


def get_fit_result(path, objname="jykim"):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise RuntimeError(f"Cannot open ROOT file: {path}")

    result = f.Get(objname)
    if not result:
        raise RuntimeError(f"Cannot find object '{objname}' in file: {path}")

    result._file = f
    return result


def get_param_value_from_root(path, name, objname="jykim"):
    result = get_fit_result(path, objname)

    par = result.floatParsFinal().find(name)

    if not par:
        par = result.constPars().find(name)

    if not par:
        raise RuntimeError(f"Cannot find parameter '{name}' in ROOT file: {path}")

    return par.getVal(), par.getError()


def get_param_value_from_txt(path, name):
    """
    Try to parse lines like:
      N_total 123.45 6.78
      N_total = 123.45 +/- 6.78
      N_total : 123.45 +- 6.78
      N_total 123.45 +/- 6.78
      RooRealVar::N_total = 123.45 +/- 6.78
    """

    number = r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?"

    patterns = [
        # name = value +/- error
        rf"\b{name}\b\s*(?:=|:)?\s*({number})\s*(?:\+/-|\+-|±)\s*({number})",

        # name value error
        rf"\b{name}\b\s+({number})\s+({number})",

        # name = value only
        rf"\b{name}\b\s*(?:=|:)\s*({number})",
    ]

    with open(path, "r") as f:
        text = f.read()

    for pat in patterns:
        m = re.search(pat, text)
        if m:
            val = float(m.group(1))
            err = float(m.group(2)) if m.lastindex and m.lastindex >= 2 else 0.0
            return val, err

    raise RuntimeError(f"Cannot find parameter '{name}' in txt file: {path}")


def get_param_value(path, name):
    ext = os.path.splitext(path)[1].lower()

    if ext == ".root":
        return get_param_value_from_root(path, name)

    if ext == ".txt":
        return get_param_value_from_txt(path, name)

    raise RuntimeError(f"Unsupported file extension: {path}")


def calc_reldiff(ref_val, cmp_val):
    diff = cmp_val - ref_val

    if ref_val != 0:
        rel_diff = diff / ref_val * 100.0
    else:
        rel_diff = float("nan")

    return diff, rel_diff


comparisons = [
    ("cmp1_plus", file_cmp1),
    ("cmp2_minus", file_cmp2),
]


print("Reference file:")
print(file_ref)
print()
print("Comparison files:")
print(f"cmp1_plus  : {file_cmp1}")
print(f"cmp2_minus : {file_cmp2}")
print()

print(
    f"{'Parameter':<15} "
    f"{'Ref':>15} "
    f"{'Cmp1':>15} {'RelDiff1 [%]':>15} "
    f"{'Cmp2':>15} {'RelDiff2 [%]':>15} "
    f"{'Larger |RelDiff|':>20}"
)
print("-" * 120)

for p in params:
    ref_val, ref_err = get_param_value(file_ref, p)

    cmp1_val, cmp1_err = get_param_value(file_cmp1, p)
    cmp2_val, cmp2_err = get_param_value(file_cmp2, p)

    diff1, rel_diff1 = calc_reldiff(ref_val, cmp1_val)
    diff2, rel_diff2 = calc_reldiff(ref_val, cmp2_val)

    abs1 = abs(rel_diff1)
    abs2 = abs(rel_diff2)

    if abs1 > abs2:
        larger = "cmp1_plus"
    elif abs2 > abs1:
        larger = "cmp2_minus"
    else:
        larger = "same"

    print(
        f"{p:<15} "
        f"{ref_val:>15.6f} "
        f"{cmp1_val:>15.6f} {rel_diff1:>15.6f} "
        f"{cmp2_val:>15.6f} {rel_diff2:>15.6f} "
        f"{larger:>20}"
    )

print()
print("Definition:")
print("RelDiff [%] = (Cmp - Ref) / Ref * 100")
