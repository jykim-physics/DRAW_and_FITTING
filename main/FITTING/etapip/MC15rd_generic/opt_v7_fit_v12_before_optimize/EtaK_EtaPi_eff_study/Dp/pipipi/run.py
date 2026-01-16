import ROOT
import sys
import glob

# --- 1. Argument Parsing ---
# 사용법: python script.py [변수명] [min] [max] [x축이름] [출력파일명] [Log여부(True/False)] [레전드위치(left/right)]
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

# --- 2. TChain 설정 (파일 묶기) ---
# Category A: Dp -> eta Kp
path_A = [
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DptoetaKp_pipipi/260107_loose_v7_less_vars_ntuple/etapip_pipipi_K/min_unc_search/no_bdt/*.root",
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/DptoetaKp_pipipi_cc/260107_loose_v7_less_vars_ntuple/etapip_pipipi_K/min_unc_search/no_bdt/*.root"
]
chain_A = ROOT.TChain("etapip_pipipi_K")
for p in path_A:
    chain_A.Add(p)

# Category B: Dp -> etapip
path_B = [
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_pipipi/260107_loose_v7_less_vars_ntuple/etapip_pipipi/ref/min_unc_search/no_bdt/*.root",
    "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_pipipi_cc/260107_loose_v7_less_vars_ntuple/etapip_pipipi/ref/min_unc_search/no_bdt/*.root"
]
chain_B = ROOT.TChain("etapip_pipipi")
for p in path_B:
    chain_B.Add(p)

# --- 3. 히스토그램 생성 ---
n_bins = 50 if var_name == "Dp_CMS_p" else 50
h_A = ROOT.TH1F("h_A", "Category A", n_bins, min_bin, max_bin)
h_B = ROOT.TH1F("h_B", "Category B", n_bins, min_bin, max_bin)

h_A.Sumw2()
h_B.Sumw2()

# --- 4. 데이터 채우기 (Cut 적용) ---
cut_string = "Dp_isSignal == 1"
print(f"Filling Category A from {chain_A.GetEntries()} entries...")
chain_A.Project("h_A", var_name, cut_string)
print(f"Filling Category B from {chain_B.GetEntries()} entries...")
chain_B.Project("h_B", var_name, cut_string)

# --- 5. Normalization ---
if h_A.Integral() > 0:
    h_A.Scale(1.0 / h_A.Integral())
if h_B.Integral() > 0:
    h_B.Scale(1.0 / h_B.Integral())

# --- 6. 스타일 및 그리기 ---
c = ROOT.TCanvas("c", "Compare MC", 800, 600)

# Category A 스타일 설정
h_A.SetLineColor(ROOT.kBlue)
h_A.SetLineWidth(2)
h_A.SetMarkerSize(0)  # 마커 크기를 0으로 설정하여 점을 제거

# Category B 스타일 설정
h_B.SetLineColor(ROOT.kRed)
h_B.SetLineWidth(2)
h_B.SetMarkerSize(0)  # 마커 크기를 0으로 설정하여 점을 제거

h_A.SetXTitle(display_var_name)
#h_A.SetYTitle("Normalized Units")

# Y축 범위 설정
h_max = max(h_A.GetMaximum(), h_B.GetMaximum())

if use_log_y == 'True':
    c.SetLogy()
    min_val = 1e-4
    h_A.SetMinimum(min_val)
    h_A.SetMaximum(h_max * 50)
else:
    h_A.SetMinimum(0)
    h_A.SetMaximum(h_max * 1.3)

# --- Draw Options ---
# HIST: 계단 모양의 라인만 그림
# E: Error bar를 그림
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
# "le" 옵션: Line(l)과 Error bar(e)를 범례에 표시
#legend.AddEntry(h_A, "D^{+} #rightarrow #eta_{3#pi} K^{+}", "le")
#legend.AddEntry(h_B, "D^{+} #rightarrow #eta_{3#pi} #pi^{+}", "le")
legend.AddEntry(h_A, "D^{+} #rightarrow #eta_{3#pi} K^{+}", "l")
legend.AddEntry(h_B, "D^{+} #rightarrow #eta_{3#pi} #pi^{+}", "l")
legend.Draw()

c.SaveAs(output_img_fname)
