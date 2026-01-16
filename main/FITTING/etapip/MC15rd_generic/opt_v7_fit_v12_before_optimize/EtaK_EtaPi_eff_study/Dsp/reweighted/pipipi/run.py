import ROOT
import sys
import glob

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
# Category A
path_A = [
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DsptoetaKp_pipipi/260107_loose_v7_less_vars_ntuple/etapip_pipipi_K/min_unc_search/no_bdt/weighted/*.root",
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DsptoetaKp_pipipi_cc/260107_loose_v7_less_vars_ntuple/etapip_pipipi_K/min_unc_search/no_bdt/weighted/*.root"
]
chain_A = ROOT.TChain("etapip_pipipi_K")
for p in path_A: chain_A.Add(p)

# Category B
path_B = [
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dsptoetapip_pipipi/260107_loose_v7_less_vars_ntuple/etapip_pipipi/ref/min_unc_search/no_bdt/weighted/*.root",
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dsptoetapip_pipipi_cc/260107_loose_v7_less_vars_ntuple/etapip_pipipi/ref/min_unc_search/no_bdt/weightd/*.root"
]
chain_B = ROOT.TChain("etapip_pipipi")
for p in path_B: chain_B.Add(p)

# --- 3. 히스토그램 생성 ---
n_bins = 50 # 필요시 var_name 조건에 따라 변경
h_A = ROOT.TH1F("h_A", "Category A", n_bins, min_bin, max_bin)
h_B = ROOT.TH1F("h_B", "Category B", n_bins, min_bin, max_bin)

# 가중치 적용 시 올바른 오차 계산을 위해 반드시 호출
h_A.Sumw2()
h_B.Sumw2()

# --- 4. 데이터 채우기 (Reweighting 적용) ---
# Weight 적용 방식: (Selection Cut) * (Weight Column)
base_cut = "etapip_Eta_isSignal == 1 && etapip_Eta_genMotherID == Pip_genMotherID && abs(Pip_genMotherPDG)==431"
weight_string = f"({base_cut}) * ds_weight"

print(f"Filling Category A with weight 'ds_weight'...")
chain_A.Project("h_A", var_name, weight_string)

print(f"Filling Category B with weight 'ds_weight'...")
chain_B.Project("h_B", var_name, weight_string)

# --- 5. Normalization ---
if h_A.Integral() > 0:
    h_A.Scale(1.0 / h_A.Integral())
if h_B.Integral() > 0:
    h_B.Scale(1.0 / h_B.Integral())

# --- 6. 스타일 및 그리기 ---
c = ROOT.TCanvas("c", "Compare MC", 800, 600)

# 공통 스타일 설정 함수
def set_hist_style(hist, color):
    hist.SetLineColor(color)
    hist.SetLineWidth(2)
    hist.SetMarkerSize(0)  # 점 제거
    hist.SetXTitle(display_var_name)

set_hist_style(h_A, ROOT.kBlue)
set_hist_style(h_B, ROOT.kRed)

h_max = max(h_A.GetMaximum(), h_B.GetMaximum())

if use_log_y == 'True':
    c.SetLogy()
    h_A.SetMinimum(1e-4)
    h_A.SetMaximum(h_max * 50)
else:
    h_A.SetMinimum(0)
    h_A.SetMaximum(h_max * 1.3)

# HIST: 계단식 라인, E: 가중치가 적용된 오차 막대
#h_A.Draw("HIST E")
#h_B.Draw("HIST E SAME")
h_A.Draw("HIST")
h_B.Draw("HIST SAME")

# --- 7. Legend ---
if legend_loc == 'left':
    legend = ROOT.TLegend(0.2, 0.75, 0.45, 0.9)
else:
    legend = ROOT.TLegend(0.65, 0.75, 0.9, 0.9)

legend.SetFillColorAlpha(ROOT.kWhite, 0.0)
legend.SetBorderSize(0)
legend.SetTextFont(42)
legend.AddEntry(h_A, "D^{+}_{s} #rightarrow #eta_{#gamma#gamma} K^{+}", "l")
legend.AddEntry(h_B, "D^{+}_{s} #rightarrow #eta_{#gamma#gamma} #pi^{+}", "l")
legend.Draw()

c.SaveAs(output_img_fname)
