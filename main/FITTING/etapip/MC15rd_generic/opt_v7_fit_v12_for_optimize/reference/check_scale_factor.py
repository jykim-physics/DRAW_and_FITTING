import ROOT
import math


# etapip_gg
file_mc = "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/MC15rd_etapip_gg_ref_fit_loose_v7_fitv12_bdt_train_Dp_CMS_p_all_0.86_sumw2fixed_weighted.root"
file_proc13 = "/share/storage/jykim/plots/proc_all/etapip/gg/generic/fitresult/proc13_etapip_gg_ref_fit_opt_loose_v7_fitv12_bdt_train_Dp_CMS_p_all_0.86_sumw2fixed.root"
# etapip_pipipi
#file_mc = "/share/storage/jykim/plots/MC15rd/etapip/pipipi/generic/fitresult/MC15rd_etapip_pipipi_ref_bdt_fit_loose_v7_fitv12_bdt_train_Dp_CMS_p_all_0.77_sumw2fixed_weighted.root"
#file_proc13 = "/share/storage/jykim/plots/proc_all/etapip/pipipi/generic/fitresult/proc13_etapip_pipipi_ref_fit_opt_loose_v7_fitv12_bdt_train_Dp_CMS_p_all_0.77_sumw2fixed.root"

key = "jykim"

params = ["N_total", "N_total_Ds"]


def get_var_from_file(filename, key, varname):
    f = ROOT.TFile.Open(filename)
    if not f or f.IsZombie():
        raise RuntimeError(f"Cannot open file: {filename}")

    obj = f.Get(key)
    if obj is None:
        f.Close()
        raise RuntimeError(f"Cannot find key '{key}' in file: {filename}")

    var = None

    # Case 1: RooFitResult
    if obj.InheritsFrom("RooFitResult"):
        var = obj.floatParsFinal().find(varname)
        if var is None:
            var = obj.constPars().find(varname)

    # Case 2: RooWorkspace
    elif obj.InheritsFrom("RooWorkspace"):
        var = obj.var(varname)

    # Case 3: RooArgSet / RooArgList
    elif obj.InheritsFrom("RooArgSet") or obj.InheritsFrom("RooArgList"):
        var = obj.find(varname)

    else:
        # fallback: try find directly if available
        if hasattr(obj, "find"):
            var = obj.find(varname)

    if var is None:
        print(f"\nObjects in file {filename}:")
        f.ls()
        f.Close()
        raise RuntimeError(f"Cannot find variable '{varname}' under key '{key}'")

    value = var.getVal()
    error = var.getError() if hasattr(var, "getError") else 0.0

    f.Close()
    return value, error


def ratio_with_error(proc_val, proc_err, mc_val, mc_err):
    if proc_val == 0 or mc_val == 0:
        return float("nan"), float("nan")

    ratio = proc_val / mc_val

    rel_err2 = 0.0
    if proc_err > 0:
        rel_err2 += (proc_err / proc_val) ** 2
    if mc_err > 0:
        rel_err2 += (mc_err / mc_val) ** 2

    ratio_err = abs(ratio) * math.sqrt(rel_err2)
    return ratio, ratio_err


print("\n=== Data/MC scaling factor check ===")
print(f"MC file     : {file_mc}")
print(f"proc13 file : {file_proc13}")
print(f"key         : {key}\n")

for par in params:
    mc_val_raw, mc_err_raw = get_var_from_file(file_mc, key, par)

    mc_val_scaled = mc_val_raw / 4.0
    mc_err_scaled = mc_err_raw / 4.0

    proc_val, proc_err = get_var_from_file(file_proc13, key, par)

    ratio, ratio_err = ratio_with_error(
        proc_val, proc_err,
        mc_val_scaled, mc_err_scaled
    )

    print(f"[{par}]")
    print(f"  MC raw        = {mc_val_raw:.6g} ± {mc_err_raw:.6g}")
    print(f"  MC / 4        = {mc_val_scaled:.6g} ± {mc_err_scaled:.6g}")
    print(f"  proc13        = {proc_val:.6g} ± {proc_err:.6g}")
    print(f"  proc13 / MC   = {ratio:.6g} ± {ratio_err:.6g}")
    print()
