import ROOT
import sys

data_fname = sys.argv[1]
MC_fname = sys.argv[2]
output_img_fname = sys.argv[3]
var_name = sys.argv[4]
min_bin = sys.argv[5]
max_bin = sys.argv[6]
display_var_name = sys.argv[7]
if_normalized = sys.argv[8]
legend_loc = sys.argv[9]



ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

root_file = ROOT.TFile(f"{data_fname}", "READ")
data_combined = root_file.Get("sweight")
data_combined.Print()

MC_root_file = ROOT.TFile(f"{MC_fname}", "READ")
MC_combined = MC_root_file.Get("sweight")
MC_combined.Print()

cdata_mc = ROOT.TCanvas("cdata_mc", "Data and MC Histogram", 800, 600)


h_data = ROOT.TH1F("h_data", "Data Histogram", 100, float(min_bin), float(max_bin))
h_MC = ROOT.TH1F("h_MC", "MC Histogram", 100, float(min_bin), float(max_bin))

h_data.Sumw2()
h_MC.Sumw2()

h_data.SetXTitle(f"{display_var_name}")
h_MC.SetXTitle(f"{display_var_name}")

for i in range(data_combined.numEntries()):
    entry = data_combined.get(i)

    target_value = entry.getRealValue(f"{var_name}")
    N_total_sw = entry.getRealValue("N_total_sw")

    total_weight = 1 * N_total_sw

    if i % 100000 == 0:
        print(f"Entry {i}: {var_name} value = {target_value}, N_total_sw = {N_total_sw}, total_weight = {total_weight}")

    h_data.Fill(target_value, total_weight)

for i in range(MC_combined.numEntries()):
    entry = MC_combined.get(i)

    target_value = entry.getRealValue(f"{var_name}")
    N_total_sw = entry.getRealValue("N_total_sw")

    total_weight = 1 * N_total_sw

    if i % 100000 == 0:
        print(f"MC Entry {i}: {var_name} value = {target_value}, N_total_sw = {N_total_sw}, total_weight = {total_weight}")

    h_MC.Fill(target_value, total_weight)

if if_normalized == 'True':
	h_data.Scale(1.0 / h_data.Integral())
	h_MC.Scale(1.0 / h_MC.Integral())

#h_data.SetLineColor(ROOT.kBlue)
#h_MC.SetLineColor(ROOT.kRed)
h_data.SetLineColorAlpha(ROOT.kBlue, 0.8)
h_MC.SetLineColorAlpha(ROOT.kRed, 0.8)

#h_data.SetMarkerStyle(20)  # Marker for data
#h_data.SetMarkerColor(ROOT.kBlue)  # Color for markers
#h_MC.SetMarkerStyle(21)  # Marker for MC
#h_MC.SetMarkerColor(ROOT.kRed)  # Color for markers

h_data.SetMarkerColorAlpha(ROOT.kBlue, 0.8)  # 50% transparent blue
h_MC.SetMarkerColorAlpha(ROOT.kRed, 0.8)    # 50% transparent red


h_MC.SetMinimum(0)
h_data.SetMinimum(0)

h_max = max(h_data.GetMaximum(), h_MC.GetMaximum())  # Find the larger max value
h_data.SetMaximum(h_max * 1.2)  # Add some margin (e.g., 20%)
h_MC.SetMaximum(h_max * 1.2)

h_MC.Draw("PE")
h_data.Draw("PE SAME")

if legend_loc == 'left':
    legend = ROOT.TLegend(0.2, 0.75, 0.4, 0.9)  # Adjusted position to move it to the left
else:
    legend = ROOT.TLegend(0.7, 0.75, 0.9, 0.9)
legend.AddEntry(h_data, "Data", "PE")  # "lep" for line and marker
legend.AddEntry(h_MC, "MC", "PE")  # "lep" for line and marker
legend.Draw()

cdata_mc.SaveAs(f"{output_img_fname}")

root_file.Close()
MC_root_file.Close()

