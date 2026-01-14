import ROOT
import sys

# --- 1. Get Arguments ---
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

cdata_mc = ROOT.TCanvas("cdata_mc", "Data and MC Comparison", 800, 800)

# --- 2. Pad Setup ---
pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1)
pad2 = ROOT.TPad("pad2", "pad2", 0, 0.0, 1, 0.3)
pad1.SetBottomMargin(0.02)
#pad2.SetTopMargin(0)
pad2.SetTopMargin(0.04)
pad2.SetBottomMargin(0.28)
pad1.Draw()
pad2.Draw()

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

# --- 3. Fill Histograms ---
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
h_data.SetMarkerColorAlpha(ROOT.kBlue, 0.8)  # 50% transparent blue
h_MC.SetMarkerColorAlpha(ROOT.kRed, 0.8)     # 50% transparent red

# --- 4. Log Scale vs Linear Scale Logic ---
# Note: This must be done on pad1, not the whole canvas, to avoid messing up pad2
h_max = max(h_data.GetMaximum(), h_MC.GetMaximum())

pad1.cd() # Make sure we are operating on the upper pad

if use_log_y == 'True':
    pad1.SetLogy() # Apply Log Y to the upper pad

    # Set Minimum > 0 to avoid log(0) errors
    if if_normalized == 'True':
        min_val = 1e-4 # Small epsilon for normalized plots
    else:
        min_val = 0.1  # 0.1 for raw counts

    h_data.SetMinimum(min_val)
    h_MC.SetMinimum(min_val)

    # Log scale needs much more headroom at the top
    h_data.SetMaximum(h_max * 100)
    h_MC.SetMaximum(h_max * 100)

else:
    pad1.SetLogy(0) # Ensure Linear
    h_MC.SetMinimum(0)
    h_data.SetMinimum(0)
    h_data.SetMaximum(h_max * 1.2)
    h_MC.SetMaximum(h_max * 1.2)

# --- 5. Draw Upper Pad ---
h_MC.Draw("PE")
h_data.Draw("PE SAME")

if legend_loc == 'left':
    legend = ROOT.TLegend(0.2, 0.75, 0.4, 0.9)
else:
    legend = ROOT.TLegend(0.7, 0.75, 0.9, 0.9)
legend.AddEntry(h_data, "Data", "PE")
legend.AddEntry(h_MC, "MC", "PE")
legend.Draw()

# --- 6. Draw Lower Pad (Ratio) ---
pad2.cd()
h_ratio = h_data.Clone("h_ratio")
h_ratio.Divide(h_MC)  # Ratio of data to MC

h_ratio.SetYTitle("Data / MC")
h_ratio.SetMinimum(0)
h_ratio.SetMaximum(2)

h_ratio.GetXaxis().SetTitleSize(0.12)  # Increase X-axis title size
h_ratio.GetYaxis().SetTitleSize(0.12)  # Increase Y-axis title size
h_ratio.GetXaxis().SetLabelSize(0.1)   # Increase X-axis label size
h_ratio.GetYaxis().SetLabelSize(0.08)  # Increase Y-axis label size
h_ratio.GetXaxis().SetTitleOffset(1.00)  # Adjust X-axis title offset
h_ratio.GetYaxis().SetTitleOffset(0.6)   # Adjust Y-axis title offset

h_ratio.SetMarkerColor(ROOT.kBlack)
h_ratio.SetLineColor(ROOT.kBlack)
h_ratio.Draw("PE")

line = ROOT.TLine(h_ratio.GetXaxis().GetXmin(), 1, h_ratio.GetXaxis().GetXmax(), 1)
line.SetLineStyle(2)  # Dashed line style
line.Draw()

cdata_mc.SaveAs(f"{output_img_fname}")

root_file.Close()
MC_root_file.Close()
