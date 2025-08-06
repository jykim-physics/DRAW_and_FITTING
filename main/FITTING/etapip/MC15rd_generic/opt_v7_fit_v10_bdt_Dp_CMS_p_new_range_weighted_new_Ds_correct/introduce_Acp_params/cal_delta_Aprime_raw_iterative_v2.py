import ROOT
import math
import os
import glob

# etapip_gg
# original files (baseline)
file_original_plus  = "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/MC15rd_etapip_gg_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_plus_0.83_new_Ds_correct_weighted.root"
file_original_minus = "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/MC15rd_etapip_gg_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_minus_0.83_new_Ds_correct_weighted.root"

# float-varied files (both p_plus and p_minus)
target_dir = "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/"
pattern_plus = os.path.join(target_dir, "*_p_plus_0.83_new_Ds_correct_float_var_*_weighted.root")
pattern_minus = os.path.join(target_dir, "*_p_minus_0.83_new_Ds_correct_float_var_*_weighted.root")

plus_files = sorted(glob.glob(pattern_plus))
minus_files = sorted(glob.glob(pattern_minus))

# Helper function
def get_acp_and_error(file_path):
    f = ROOT.TFile.Open(file_path)
    if not f or f.IsZombie():
        raise IOError(f"Cannot open file: {file_path}")
    result = f.Get("jykim")
    if not result:
        raise KeyError(f"'jykim' key not found in {file_path}")
    acp = result.floatParsFinal().find("Acp")
    if not acp:
        raise KeyError(f"'Acp' not found in RooFitResult of {file_path}")
    val, err = acp.getVal(), acp.getError()
    f.Close()
    return val, err

# Get baseline Araw
x, dx = get_acp_and_error(file_original_plus)
y, dy = get_acp_and_error(file_original_minus)

Araw_original = (x + y) / 2
Araw_original_err = math.sqrt(dx**2 + dy**2) / 2

print(f"✅ Araw (original): ({Araw_original * 100:.3f}% ± {Araw_original_err * 100:.3f}%)\n")

# Match files by float_var component (e.g., Ds_mean, sigma_gaussian, etc.)
float_pairs = {}
for pfile in plus_files:
    var_name = pfile.split("float_var_")[-1]
    for mfile in minus_files:
        if mfile.endswith(var_name):
            float_pairs[var_name] = (pfile, mfile)
            break

# Compute and print
print("🧪 Comparing float-varied Araw (in %):")
for var, (pfile, mfile) in float_pairs.items():
    try:
        x_f, dx_f = get_acp_and_error(pfile)
        y_f, dy_f = get_acp_and_error(mfile)

        Araw_after = (x_f + y_f) / 2
        Araw_after_err = math.sqrt(dx_f**2 + dy_f**2) / 2

        delta = Araw_after - Araw_original
        delta_err = math.sqrt(abs(Araw_after_err**2 - Araw_original_err**2))

        # Print in %
        print(f"[{var.replace('_weighted.root','')}]")
        print(f"  → Araw(after): ({Araw_after * 100:.3f}% ± {Araw_after_err * 100:.3f}%)")
        print(f"  → Δ(Araw)    : ({delta * 100:+.3f}% ± {delta_err * 100:.3f}%)\n")

    except Exception as e:
        print(f"{var}: ❌ Error: {e}")

