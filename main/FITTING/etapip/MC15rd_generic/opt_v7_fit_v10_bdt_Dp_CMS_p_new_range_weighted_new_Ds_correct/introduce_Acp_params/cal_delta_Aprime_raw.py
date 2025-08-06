import ROOT
import math

# 파일 경로들
files = {
    "original_plus": "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/MC15rd_etapip_gg_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_plus_0.83_new_Ds_correct_weighted.root",
    "original_minus": "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/MC15rd_etapip_gg_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_minus_0.83_new_Ds_correct_weighted.root",
    "float_plus": "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/MC15rd_etapip_gg_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_plus_0.83_new_Ds_correct_float_var_mean_weighted.root",
    "float_minus": "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/MC15rd_etapip_gg_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_minus_0.83_new_Ds_correct_float_var_mean_weighted.root"
}

# Acp 값을 추출하는 함수
def get_acp_and_error(filename):
    f = ROOT.TFile.Open(filename)
    if not f or f.IsZombie():
        raise IOError(f"Cannot open file: {filename}")

    result = f.Get("jykim")
    if not result:
        raise KeyError(f"'jykim' RooFitResult not found in {filename}")

    acp = result.floatParsFinal().find("Acp")
    if not acp:
        raise KeyError(f"'Acp' not found in RooFitResult in {filename}")

    val = acp.getVal()
    err = acp.getError()
    f.Close()
    return val, err

# Acp 값들 읽기
x, dx = get_acp_and_error(files["original_plus"])
y, dy = get_acp_and_error(files["original_minus"])
X, dX = get_acp_and_error(files["float_plus"])
Y, dY = get_acp_and_error(files["float_minus"])

# Araw 계산
Araw_original = (x + y) / 2
Araw_original_err = math.sqrt(dx**2 + dy**2) / 2

Araw_after = (X + Y) / 2
Araw_after_err = math.sqrt(dX**2 + dY**2) / 2

# 차이 계산
delta = Araw_after - Araw_original
delta_err = math.sqrt(abs(Araw_after_err**2 - Araw_original_err**2))

# 결과 출력
print(f"Original Araw       = ({Araw_original*100:.6f}% ± {Araw_original_err*100:.6f}%)")
print(f"After Araw (float)  = ({Araw_after*100:.6f}% ± {Araw_after_err*100:.6f}%)")
print(f"Difference          = ({delta*100:.6f}% ± {delta_err*100:.6f}%)")

