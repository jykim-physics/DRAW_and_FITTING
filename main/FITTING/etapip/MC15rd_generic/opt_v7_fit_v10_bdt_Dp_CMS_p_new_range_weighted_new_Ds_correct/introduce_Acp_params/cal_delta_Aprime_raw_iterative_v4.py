import ROOT
import glob
import os
import math

# Configuration
#target_dir = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/"
#file_original_plus  = os.path.join(target_dir, "MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_plus_0.92_new_Ds_correct_weighted.root")
#file_original_minus = os.path.join(target_dir, "MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_minus_0.92_new_Ds_correct_weighted.root")

#pattern_plus = os.path.join(target_dir, "*fitv10_bdt_train_Dp_CMS_p_plus_0.92_new_Ds_correct_float_var_*_weighted.root")
#pattern_minus = os.path.join(target_dir, "*fitv10_bdt_train_Dp_CMS_p_minus_0.92_new_Ds_correct_float_var_*_weighted.root")

# etapip_gg_K
file_original_plus  = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/                                         MC15rd_etaKp_gg_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_plus_0.91_new_Ds_correct_weighted.root"
file_original_minus = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/                                         MC15rd_etaKp_gg_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_minus_0.91_new_Ds_correct_weighted.root"

target_dir = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/"
pattern_plus = os.path.join(target_dir, "*fitv10_bdt_train_Dp_CMS_p_plus_0.91_new_Ds_correct_float_var_*_weighted.root")
pattern_minus = os.path.join(target_dir, "*fitv10_bdt_train_Dp_CMS_p_minus_0.91_new_Ds_correct_float_var_*_weighted.root")

plus_files = sorted(glob.glob(pattern_plus))
minus_files = sorted(glob.glob(pattern_minus))

variables = ["Acp", "Acp_Ds"]

def get_var_from_result(file_path, varname):
    f = ROOT.TFile.Open(file_path)
    if not f or f.IsZombie():
        raise IOError(f"Cannot open file: {file_path}")
    result = f.Get("jykim")
    if not result:
        f.Close()
        raise KeyError(f"'jykim' (RooFitResult) not found in {file_path}")

    v = result.floatParsFinal().find(varname)
    if not v:
        f.Close()
        raise KeyError(f"'{varname}' not found in RooFitResult of {file_path}")

    val, err = v.getVal(), v.getError()
    f.Close()
    return val, err

# Match float-var pairs
float_pairs = {}
for pfile in plus_files:
    # Extract the tag (e.g., 'argus_c' from '...float_var_argus_c_weighted.root')
    tag = pfile.split("float_var_")[-1].replace("_weighted.root", "")
    for mfile in minus_files:
        if tag in mfile:
            float_pairs[tag] = (pfile, mfile)
            break

# Process
for var in variables:
    print(f"\n{'='*70}")
    print(f"📊 SYSTEMATIC STUDY FOR VARIABLE: {var}")
    print(f"{'='*70}")

    # Baseline calculations
    x, dx = get_var_from_result(file_original_plus, var)
    y, dy = get_var_from_result(file_original_minus, var)
    Araw_original = (x + y) / 2
    Araw_original_err = math.sqrt(dx**2 + dy**2) / 2

    print(f"✅ Baseline (Original Files):")
    print(f"  [+] {var}: {x*100:8.4f}% ± {dx*100:.4f}%")
    print(f"  [-] {var}: {y*100:8.4f}% ± {dy*100:.4f}%")
    print(f"  Total Araw: {Araw_original*100:8.4f}% ± {Araw_original_err*100:.4f}%\n")

    print(f"🧪 Comparing float-varied Araw (values in %):")
    print(f"{'-'*70}")

    for tag, (pfile, mfile) in float_pairs.items():
        try:
            # 1. Get the target variable (Acp or Acp_Ds)
            x_f, dx_f = get_var_from_result(pfile, var)
            y_f, dy_f = get_var_from_result(mfile, var)

            # 2. Get the specific float_var parameter name from the tag
            # This fetches 'Acp_varname' as requested
            var_param_name = f"Acp_{tag}"

            val_p_spec, err_p_spec = get_var_from_result(pfile, var_param_name)
            val_m_spec, err_m_spec = get_var_from_result(mfile, var_param_name)

            # 3. Calculate Araw
            Araw_after = (x_f + y_f) / 2
            Araw_after_err = math.sqrt(dx_f**2 + dy_f**2) / 2
            delta = Araw_after - Araw_original

            # Error on difference (assuming high correlation between original and varied fit)
            delta_err = math.sqrt(abs(Araw_after_err**2 - Araw_original_err**2))

            print(f"🏷️  Tag: [{tag}]")
            print(f"  (+) From Plus  File: {var_param_name} = {val_p_spec:8.4f} ± {err_p_spec:.4f}")
            print(f"  (-) From Minus File: {var_param_name} = {val_m_spec:8.4f} ± {err_m_spec:.4f}")
            print(f"  → Combined Araw: {Araw_after*100:8.3f}% ± {Araw_after_err*100:.3f}%")
            print(f"  → Δ(Araw)      : {delta*100:+8.3f}% ± {delta_err*100:.3f}%\n")

        except Exception as e:
            print(f"⚠️  [{tag}] Error: {e}")
