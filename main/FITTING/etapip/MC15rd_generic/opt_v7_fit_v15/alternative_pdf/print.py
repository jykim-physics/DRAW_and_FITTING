#!/usr/bin/env python3
import ROOT

# etapip_gg_K
#file_ref = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_all_0.86_KDE_fixed_2nd_cheby_weighted.root"
#file_cmp = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_all_0.86_KDE_fixed_2nd_cheby_extended_exp_weighted.root"

# etapip_pipipi_K
file_ref = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_all_0.77_KDE_fixed_2nd_cheby_weighted.root"
file_cmp = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_train_Dp_CMS_p_all_0.77_KDE_fixed_2nd_cheby_extended_exp_weighted.root"

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
        raise RuntimeError(f"Cannot open file: {path}")

    result = f.Get(objname)
    if not result:
        raise RuntimeError(f"Cannot find object '{objname}' in file: {path}")

    # keep file alive by attaching it to result
    result._file = f
    return result


def get_param_value(fit_result, name):
    pars = fit_result.floatParsFinal()
    par = pars.find(name)

    if not par:
        # 혹시 fixed parameter에 들어간 경우 대비
        pars_const = fit_result.constPars()
        par = pars_const.find(name)

    if not par:
        raise RuntimeError(f"Cannot find parameter: {name}")

    return par.getVal(), par.getError()


result_ref = get_fit_result(file_ref)
result_cmp = get_fit_result(file_cmp)

print("Reference file:")
print(file_ref)
print()
print("Comparison file:")
print(file_cmp)
print()
print(f"{'Parameter':<15} {'Ref':>15} {'Cmp':>15} {'Diff':>15} {'RelDiff [%]':>15}")
print("-" * 80)

for p in params:
    ref_val, ref_err = get_param_value(result_ref, p)
    cmp_val, cmp_err = get_param_value(result_cmp, p)

    diff = cmp_val - ref_val

    if ref_val != 0:
        rel_diff = diff / ref_val * 100.0
        rel_diff_str = f"{rel_diff: .6f}"
    else:
        rel_diff_str = "nan"

    print(
        f"{p:<15} "
        f"{ref_val:>15.6f} "
        f"{cmp_val:>15.6f} "
        f"{diff:>15.6f} "
        f"{rel_diff_str:>15}"
    )
