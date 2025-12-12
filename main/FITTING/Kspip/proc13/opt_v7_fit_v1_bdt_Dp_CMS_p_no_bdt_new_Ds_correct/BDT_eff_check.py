import ROOT
import sys

# Inputs
data_fname = sys.argv[1]
MC_fname = sys.argv[2]
output_img_fname = sys.argv[3]
var_name = sys.argv[4]
min_bin = float(sys.argv[5])
max_bin = float(sys.argv[6])
display_var_name = sys.argv[7]
if_normalized = sys.argv[8]
legend_loc = sys.argv[9]

# --- NEW: Define your cut value here ---
#cut_value = 0.92
cut_value = float(sys.argv[10])
# ---------------------------------------

ROOT.gROOT.SetBatch(True) # Prevent canvas from popping up
ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

root_file = ROOT.TFile(f"{data_fname}", "READ")
data_combined = root_file.Get("sweight")

MC_root_file = ROOT.TFile(f"{MC_fname}", "READ")
MC_combined = MC_root_file.Get("sweight")

cdata_mc = ROOT.TCanvas("cdata_mc", "Data and MC Histogram", 800, 600)

h_data = ROOT.TH1F("h_data", "Data Histogram", 100, min_bin, max_bin)
h_MC = ROOT.TH1F("h_MC", "MC Histogram", 100, min_bin, max_bin)

h_data.Sumw2()
h_MC.Sumw2()

h_data.SetXTitle(f"{display_var_name}")
h_MC.SetXTitle(f"{display_var_name}")

# --- Fill Data ---
print(">>> Filling Data Histogram...")
for i in range(data_combined.numEntries()):
    entry = data_combined.get(i)
    target_value = entry.getRealValue(f"{var_name}")
    N_total_sw = entry.getRealValue("N_total_sw")

    # Fill with sWeight
    h_data.Fill(target_value, N_total_sw)

# --- Fill MC ---
print(">>> Filling MC Histogram...")
for i in range(MC_combined.numEntries()):
    entry = MC_combined.get(i)
    target_value = entry.getRealValue(f"{var_name}")
    N_total_sw = entry.getRealValue("N_total_sw")

    # Fill with sWeight
    h_MC.Fill(target_value, N_total_sw)

# ==============================================================================
#  CALCULATE EFFICIENCY (Integral from min_bin to cut_value)
# ==============================================================================

# 1. Find the bin number that corresponds to the cut value (e.g., 0.92)
bin_cut_index = h_data.FindBin(cut_value)

# 2. Integrate from the first bin (1) up to the cut bin
#    Note: To integrate from 0 to cut, we assume min_bin is 0.
#    If min_bin < 0, this integrates from min_bin to cut.
data_integral_pass = h_data.Integral(1, bin_cut_index)
data_integral_total = h_data.Integral() # Total sum of weights

mc_integral_pass = h_MC.Integral(1, bin_cut_index)
mc_integral_total = h_MC.Integral()

# 3. Calculate Efficiencies
# Check for division by zero
eff_data = (data_integral_pass / data_integral_total) if data_integral_total > 0 else 0
eff_mc = (mc_integral_pass / mc_integral_total) if mc_integral_total > 0 else 0

print("-" * 60)
print(f"Efficiency Calculation for variable: {var_name}")
print(f"Integration Range: [{min_bin} , {cut_value}]")
print("-" * 60)
print(f"Data Efficiency: {eff_data:.6f}  (Pass: {data_integral_pass:.2f} / Total: {data_integral_total:.2f})")
print(f"MC Efficiency:   {eff_mc:.6f}  (Pass: {mc_integral_pass:.2f} / Total: {mc_integral_total:.2f})")

if eff_mc > 0:
    print(f"Data/MC Ratio:   {eff_data/eff_mc:.6f}")
    print(f"(Data-MC)/MC:   {(eff_data-eff_mc)/eff_mc:.6f}")
print("-" * 60)

# ==============================================================================

# Normalization for Plotting (User request)
if if_normalized == 'True':
    if h_data.Integral() > 0: h_data.Scale(1.0 / h_data.Integral())
    if h_MC.Integral() > 0: h_MC.Scale(1.0 / h_MC.Integral())

h_data.SetLineColorAlpha(ROOT.kBlue, 0.8)
h_MC.SetLineColorAlpha(ROOT.kRed, 0.8)
h_data.SetMarkerColorAlpha(ROOT.kBlue, 0.8)
h_MC.SetMarkerColorAlpha(ROOT.kRed, 0.8)

h_MC.SetMinimum(0)
h_data.SetMinimum(0)

h_max = max(h_data.GetMaximum(), h_MC.GetMaximum())
h_data.SetMaximum(h_max * 1.2)
h_MC.SetMaximum(h_max * 1.2)

h_MC.Draw("PE")
h_data.Draw("PE SAME")

if legend_loc == 'left':
    legend = ROOT.TLegend(0.2, 0.75, 0.4, 0.9)
else:
    legend = ROOT.TLegend(0.7, 0.75, 0.9, 0.9)
legend.AddEntry(h_data, "Data", "PE")
legend.AddEntry(h_MC, "MC", "PE")
legend.Draw()

cdata_mc.SaveAs(f"{output_img_fname}")

root_file.Close()
MC_root_file.Close()
