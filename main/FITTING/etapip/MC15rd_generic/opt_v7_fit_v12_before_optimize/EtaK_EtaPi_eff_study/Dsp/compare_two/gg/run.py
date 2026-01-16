import ROOT
import sys

# --- 1. Argument Parsing ---
var_name         = sys.argv[1]
min_bin          = float(sys.argv[2])
max_bin          = float(sys.argv[3])
display_var_name = sys.argv[4]
output_img_fname = sys.argv[5]
use_log_y        = sys.argv[6]
legend_loc       = sys.argv[7]

# Belle2Style 설정
ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

# --- 2. TChain 설정 ---
chain_A = ROOT.TChain("etapip_gg_K")
path_A = [
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DsptoetaKp_gg/260107_loose_v7_less_vars_ntuple/etapip_gg_K/min_unc_search/no_bdt/*.root",
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DsptoetaKp_gg_cc/260107_loose_v7_less_vars_ntuple/etapip_gg_K/min_unc_search/no_bdt/*.root"
]
for p in path_A: chain_A.Add(p)

chain_A_w = ROOT.TChain("etapip_gg_K")
path_A_w = [
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DsptoetaKp_gg/260107_loose_v7_less_vars_ntuple/etapip_gg_K/min_unc_search/no_bdt/weighted/*.root",
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DsptoetaKp_gg_cc/260107_loose_v7_less_vars_ntuple/etapip_gg_K/min_unc_search/no_bdt/weighted/*.root"
]
for p in path_A_w: chain_A_w.Add(p)

chain_B = ROOT.TChain("etapip_gg")
path_B = [
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dsptoetapip_gg/260107_loose_v7_less_vars_ntuple/etapip_gg/ref/min_unc_search/no_bdt/*.root",
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dsptoetapip_gg_cc/260107_loose_v7_less_vars_ntuple/etapip_gg/ref/min_unc_search/no_bdt/*.root"
]
for p in path_B: chain_B.Add(p)
chain_B_w = ROOT.TChain("etapip_gg")
path_B_w = [
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dsptoetapip_gg/260107_loose_v7_less_vars_ntuple/etapip_gg/ref/min_unc_search/no_bdt/weighted/*.root",
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dsptoetapip_gg_cc/260107_loose_v7_less_vars_ntuple/etapip_gg/ref/min_unc_search/no_bdt/weighted/*.root"
]
for p in path_B_w: chain_B_w.Add(p)

# --- 3. 히스토그램 생성 (4개) ---
n_bins = 50
h_A_w   = ROOT.TH1F("h_A_w",   "Cat A Weighted",   n_bins, min_bin, max_bin)
h_A_raw = ROOT.TH1F("h_A_raw", "Cat A Unweighted", n_bins, min_bin, max_bin)
h_B_w   = ROOT.TH1F("h_B_w",   "Cat B Weighted",   n_bins, min_bin, max_bin)
h_B_raw = ROOT.TH1F("h_B_raw", "Cat B Unweighted", n_bins, min_bin, max_bin)

for h in [h_A_w, h_A_raw, h_B_w, h_B_raw]:
    h.Sumw2()

# --- 4. 데이터 채우기 ---
base_cut = "etapip_Eta_isSignal == 1 && etapip_Eta_genMotherID == Pip_genMotherID && abs(Pip_genMotherPDG)==431"
weight_string = f"({base_cut}) * ds_weight"

print("Filling Category A...")
chain_A_w.Project("h_A_w",   var_name, weight_string) # Weighted
chain_A.Project("h_A_raw", var_name, base_cut)      # Unweighted

print("Filling Category B...")
chain_B_w.Project("h_B_w",   var_name, weight_string) # Weighted
chain_B.Project("h_B_raw", var_name, base_cut)      # Unweighted

# --- 5. Normalization ---
for h in [h_A_w, h_A_raw, h_B_w, h_B_raw]:
    if h.Integral() > 0:
        h.Scale(1.0 / h.Integral())

# --- 6. 스타일 및 그리기 ---
c = ROOT.TCanvas("c", "Compare Reweighting", 800, 600)

# 스타일 정의 함수
def apply_style(hist, color, style, label):
    hist.SetLineColor(color)
    hist.SetLineStyle(style) # 1: Solid, 2: Dashed
    hist.SetLineWidth(3)
    hist.SetMarkerSize(0)
    hist.SetXTitle(display_var_name)

# A: Blue / B: Red
# Weighted: Solid(1) / Raw: Dashed(2)
apply_style(h_A_w,   ROOT.kBlue,      1, "A (Weighted)")
apply_style(h_A_raw, ROOT.kBlue-7,    2, "A (Unweighted)")
apply_style(h_B_w,   ROOT.kRed,       1, "B (Weighted)")
apply_style(h_B_raw, ROOT.kRed-7,     2, "B (Unweighted)")

# Y축 범위 최적화
h_max = max([h.GetMaximum() for h in [h_A_w, h_A_raw, h_B_w, h_B_raw]])

if use_log_y == 'True':
    c.SetLogy()
    h_A_w.SetMinimum(1e-4)
    h_A_w.SetMaximum(h_max * 50)
else:
    h_A_w.SetMinimum(0)
    h_A_w.SetMaximum(h_max * 1.3)

# 그리기
h_A_w.Draw("HIST E")
h_A_raw.Draw("HIST E SAME")
h_B_w.Draw("HIST E SAME")
h_B_raw.Draw("HIST E SAME")

'''
# --- 7. Legend ---
if legend_loc == 'left':
    legend = ROOT.TLegend(0.18, 0.70, 0.50, 0.92)
else:
    legend = ROOT.TLegend(0.60, 0.70, 0.92, 0.92)

legend.SetFillColorAlpha(ROOT.kWhite, 0.0)
legend.SetBorderSize(0)
legend.SetTextFont(42)
legend.SetTextSize(0.03)
'''


# --- 7. Legend ---
# Expanded the width (x-axis) and depth (y-axis) to fit larger text
if legend_loc == 'left':
    # x1 decreased, x2 increased, y1 decreased
    legend = ROOT.TLegend(0.18, 0.62, 0.58, 0.92)
else:
    # x1 decreased, y1 decreased
    legend = ROOT.TLegend(0.55, 0.62, 0.95, 0.92)

legend.SetFillColorAlpha(ROOT.kWhite, 0.0)
legend.SetBorderSize(0)
legend.SetTextFont(42)

# Increased from 0.03 to 0.05
legend.SetTextSize(0.05)

legend.AddEntry(h_A_w,   "D^{+}_{s} #rightarrow #eta_{#gamma#gamma} K^{+} (w)", "l")
legend.AddEntry(h_A_raw, "D^{+}_{s} #rightarrow #eta_{#gamma#gamma} K^{+} (raw)", "l")
legend.AddEntry(h_B_w,   "D^{+}_{s} #rightarrow #eta_{#gamma#gamma} #pi^{+} (w)", "l")
legend.AddEntry(h_B_raw, "D^{+}_{s} #rightarrow #eta_{#gamma#gamma} #pi^{+} (raw)", "l")
legend.Draw()

c.SaveAs(output_img_fname)
