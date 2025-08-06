import ROOT
import math
import os
import glob

# 기준값 Acp (original)
file_original_plus  = "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/MC15rd_etapip_gg_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_plus_0.83_new_Ds_correct_weighted.root"
file_original_minus = "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/MC15rd_etapip_gg_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_minus_0.83_new_Ds_correct_weighted.root"

def get_acp_and_error(file_path):
    f = ROOT.TFile.Open(file_path)
    if not f or f.IsZombie():
        raise IOError(f"Cannot open file: {file_path}")
    result = f.Get("jykim")
    if not result:
        raise KeyError(f"Cannot find key 'jykim' in file: {file_path}")
    acp = result.floatParsFinal().find("Acp")
    if not acp:
        raise KeyError(f"'Acp' not found in RooFitResult of {file_path}")
    val, err = acp.getVal(), acp.getError()
    f.Close()
    return val, err

# Get reference values
x, dx = get_acp_and_error(file_original_plus)
y, dy = get_acp_and_error(file_original_minus)

Araw_original = (x + y) / 2
Araw_original_err = math.sqrt(dx**2 + dy**2) / 2

print(f"✅ Araw (original): ({Araw_original * 100:.3f}% ± {Araw_original_err * 100:.3f}%)\n")

# 대상 디렉토리 (float 변형 파일들 - p_minus 기준)
target_dir = "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/"
target_pattern = os.path.join(target_dir, "*_Dp_CMS_p_minus_0.83_new_Ds_correct_float_var_*_weighted.root")
float_files = sorted(glob.glob(target_pattern))

# 기준 plus 파일은 변하지 않음
float_plus_file = "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/MC15rd_etapip_gg_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_plus_0.83_new_Ds_correct_float_var_mean_weighted.root"
x_f, dx_f = get_acp_and_error(float_plus_file)

# 반복
print("🧪 Comparing each float variation:")
for file_path in float_files:
    filename = os.path.basename(file_path)
    try:
        y_f, dy_f = get_acp_and_error(file_path)

        # Araw(after)
        Araw_after = (x_f + y_f) / 2
        Araw_after_err = math.sqrt(dx_f**2 + dy_f**2) / 2

        # Difference
        delta = Araw_after - Araw_original
        delta_err = math.sqrt(abs(Araw_after_err**2 - Araw_original_err**2))

        # Convert all to %
        Araw_after_pct = Araw_after * 100
        Araw_after_err_pct = Araw_after_err * 100
        delta_pct = delta * 100
        delta_err_pct = delta_err * 100

        print(f"{filename}")
        print(f"  → Araw(after): ({Araw_after_pct:.3f}% ± {Araw_after_err_pct:.3f}%)")
        print(f"  → Δ(Araw)    : ({delta_pct:+.3f}% ± {delta_err_pct:.3f}%)\n")

    except Exception as e:
        print(f"{filename}: ❌ Error: {e}")

