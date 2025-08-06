import ROOT
import math
import os
import glob

# etapip_gg
# Baseline files
#file_original_plus  = "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/MC15rd_etapip_gg_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_plus_0.83_new_Ds_correct_weighted.root"
#file_original_minus = "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/MC15rd_etapip_gg_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_minus_0.83_new_Ds_correct_weighted.root"

# Float-varied files (p_plus / p_minus)
#target_dir = "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/"
#pattern_plus = os.path.join(target_dir, "*fitv10_bdt_train_Dp_CMS_p_plus_0.83_new_Ds_correct_float_var_*_weighted.root")
#pattern_minus = os.path.join(target_dir, "*fitv10_bdt_train_Dp_CMS_p_minus_0.83_new_Ds_correct_float_var_*_weighted.root")

# etapip_pipipi
#file_original_plus  = "/share/storage/jykim/plots/MC15rd/etapip/pipipi/generic/fitresult/MC15rd_etapip_pipipi_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_plus_0.74_new_Ds_correct_weighted.root"
#file_original_minus = "/share/storage/jykim/plots/MC15rd/etapip/pipipi/generic/fitresult/MC15rd_etapip_pipipi_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_minus_0.74_new_Ds_correct_weighted.root"

#target_dir = "/share/storage/jykim/plots/MC15rd/etapip/pipipi/generic/fitresult/"
#pattern_plus = os.path.join(target_dir, "*fitv10_bdt_train_Dp_CMS_p_plus_0.74_new_Ds_correct_float_var_*_weighted.root")
#pattern_minus = os.path.join(target_dir, "*fitv10_bdt_train_Dp_CMS_p_minus_0.74_new_Ds_correct_float_var_*_weighted.root")

# etapip_gg_K
#file_original_plus  = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_plus_0.91_new_Ds_correct_weighted.root"
#file_original_minus = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_minus_0.91_new_Ds_correct_weighted.root"

#target_dir = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/"
#pattern_plus = os.path.join(target_dir, "*fitv10_bdt_train_Dp_CMS_p_plus_0.91_new_Ds_correct_float_var_*_weighted.root")
#pattern_minus = os.path.join(target_dir, "*fitv10_bdt_train_Dp_CMS_p_minus_0.91_new_Ds_correct_float_var_*_weighted.root")

# etapip_pipipi_K
file_original_plus  = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_plus_0.92_new_Ds_correct_weighted.root"
file_original_minus = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_minus_0.92_new_Ds_correct_weighted.root"

target_dir = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/"
pattern_plus = os.path.join(target_dir, "*fitv10_bdt_train_Dp_CMS_p_plus_0.92_new_Ds_correct_float_var_*_weighted.root")
pattern_minus = os.path.join(target_dir, "*fitv10_bdt_train_Dp_CMS_p_minus_0.92_new_Ds_correct_float_var_*_weighted.root")

plus_files = sorted(glob.glob(pattern_plus))
minus_files = sorted(glob.glob(pattern_minus))

# Variable list to process
variables = ["Acp", "Acp_Ds"]

# RooFitResult helper
def get_var_from_result(file_path, varname):
    f = ROOT.TFile.Open(file_path)
    if not f or f.IsZombie():
        raise IOError(f"Cannot open file: {file_path}")
    result = f.Get("jykim")
    if not result:
        raise KeyError(f"'jykim' key not found in {file_path}")
    v = result.floatParsFinal().find(varname)
    if not v:
        raise KeyError(f"'{varname}' not found in RooFitResult of {file_path}")
    val, err = v.getVal(), v.getError()
    f.Close()
    return val, err

# Match float-var pairs
float_pairs = {}
for pfile in plus_files:
    var_name = pfile.split("float_var_")[-1]
    for mfile in minus_files:
        if mfile.endswith(var_name):
            float_pairs[var_name] = (pfile, mfile)
            break

# Compute for each variable
for var in variables:
    print(f"\n===================== 📊 Variable: {var} =====================")

    # Baseline Araw(original)
    x, dx = get_var_from_result(file_original_plus, var)
    y, dy = get_var_from_result(file_original_minus, var)
    Araw_original = (x + y) / 2
    Araw_original_err = math.sqrt(dx**2 + dy**2) / 2
    print(f"✅ Araw (original): ({Araw_original * 100:.3f}% ± {Araw_original_err * 100:.3f}%)\n")

    # Loop over float-var files
    print("🧪 Comparing float-varied Araw (in %):")
    for tag, (pfile, mfile) in float_pairs.items():
        try:
            x_f, dx_f = get_var_from_result(pfile, var)
            y_f, dy_f = get_var_from_result(mfile, var)

            Araw_after = (x_f + y_f) / 2
            Araw_after_err = math.sqrt(dx_f**2 + dy_f**2) / 2

            delta = Araw_after - Araw_original
            delta_err = math.sqrt(abs(Araw_after_err**2 - Araw_original_err**2))

            # Percent format
            print(f"[{tag.replace('_weighted.root','')}]")
            print(f"  → Araw(after): ({Araw_after * 100:.3f}% ± {Araw_after_err * 100:.3f}%)")
            print(f"  → Δ(Araw)    : ({delta * 100:+.3f}% ± {delta_err * 100:.3f}%)\n")

        except Exception as e:
            print(f"[{tag}] ❌ Error processing variable '{var}': {e}")

