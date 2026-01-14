import ROOT
import sys

# --- 1. Update Argument Parsing ---
data_fname = sys.argv[1]
MC_fname = sys.argv[2]
output_img_fname = sys.argv[3]
var_name = sys.argv[4]
min_bin = sys.argv[5]
max_bin = sys.argv[6]
display_var_name = sys.argv[7]
if_normalized = sys.argv[8]
legend_loc = sys.argv[9]
use_log_y = sys.argv[10]  # <--- NEW ARGUMENT ('True' or 'False')

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

root_file = ROOT.TFile(f"{data_fname}", "READ")
data_combined = root_file.Get("sweight")
# data_combined.Print()

MC_root_file = ROOT.TFile(f"{MC_fname}", "READ")
MC_combined = MC_root_file.Get("sweight")
# MC_combined.Print()

cdata_mc = ROOT.TCanvas("cdata_mc", "Data and MC Histogram", 800, 600)

if var_name != "Dp_CMS_p":
  h_data = ROOT.TH1F("h_data", "Data Histogram", 50, float(min_bin), float(max_bin))
  h_MC = ROOT.TH1F("h_MC", "MC Histogram", 50, float(min_bin), float(max_bin))
else:
  h_data = ROOT.TH1F("h_data", "Data Histogram", 100, float(min_bin), float(max_bin))
  h_MC = ROOT.TH1F("h_MC", "MC Histogram", 100, float(min_bin), float(max_bin))

h_data.Sumw2()
h_MC.Sumw2()

h_data.SetXTitle(f"{display_var_name}")
h_MC.SetXTitle(f"{display_var_name}")

# --- Fill Loops (Unchanged) ---
for i in range(data_combined.numEntries()):
    entry = data_combined.get(i)
    target_value = entry.getRealValue(f"{var_name}")
    N_total_sw = entry.getRealValue("N_total_sw")
    total_weight = 1 * N_total_sw
    #if i % 100000 == 0:
    #    print(f"Entry {i}: {var_name} value = {target_value}, N_total_sw = {N_total_sw}, total_weight = {total_weight}")
    h_data.Fill(target_value, total_weight)

for i in range(MC_combined.numEntries()):
    entry = MC_combined.get(i)
    target_value = entry.getRealValue(f"{var_name}")
    N_total_sw = entry.getRealValue("N_total_sw")
    total_weight = 1 * N_total_sw
    #if i % 100000 == 0:
    #    print(f"MC Entry {i}: {var_name} value = {target_value}, N_total_sw = {N_total_sw}, total_weight = {total_weight}")
    h_MC.Fill(target_value, total_weight)

if if_normalized == 'True':
    h_data.Scale(1.0 / h_data.Integral())
    h_MC.Scale(1.0 / h_MC.Integral())

h_data.SetLineColorAlpha(ROOT.kBlue, 0.8)
h_MC.SetLineColorAlpha(ROOT.kRed, 0.8)
h_data.SetMarkerColorAlpha(ROOT.kBlue, 0.8)
h_MC.SetMarkerColorAlpha(ROOT.kRed, 0.8)

# --- 2. Logic for Log Scale vs Linear Scale ---
h_max = max(h_data.GetMaximum(), h_MC.GetMaximum())

if use_log_y == 'True':
    cdata_mc.SetLogy() # Set Canvas to Log Scale

    # Log scale requires a positive minimum (> 0)
    if if_normalized == 'True':
        min_val = 1e-5 # Small epsilon for normalized plots
    else:
        min_val = 0.1  # 0.1 for raw counts (since counts can't be between 0 and 1 usually)

    h_data.SetMinimum(min_val)
    h_MC.SetMinimum(min_val)

    # Log scale needs a much higher max to prevent cutting off peaks visually
    h_data.SetMaximum(h_max * 50)
    h_MC.SetMaximum(h_max * 50)

else:
    cdata_mc.SetLogy(0) # Ensure Linear
    h_MC.SetMinimum(0)
    h_data.SetMinimum(0)
    h_data.SetMaximum(h_max * 1.2)
    h_MC.SetMaximum(h_max * 1.2)

# --- Drawing ---
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
