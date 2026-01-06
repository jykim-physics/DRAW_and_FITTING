import ROOT

# === Setup Belle2 Style ===
ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

# === User inputs ===
#data_fname = "/share/storage/jykim/sweight/proc13/KsKp/gg/proc13_Kspip_gg_K_fit_opt_loose_v7_fitv1_Ds_no_bdt.root"
#MC_fname = "/share/storage/jykim/sweight/MC15rd/KsKp/gg/MC15rd_Kspip_gg_K_fit_opt_loose_v7_fitv1_Ds_no_bdt.root"
data_fname = "/share/storage/jykim/sweight/proc13/KsKp/pipipi/proc13_Kspip_pipipi_K_fit_opt_loose_v7_fitv1_Ds_no_bdt_new_Ds_correct.root"
MC_fname = "/share/storage/jykim/sweight/MC15rd/KsKp/pipipi/MC15rd_Kspip_pipipi_K_fit_opt_loose_v7_fitv1_Ds_no_bdt_new_Ds_correct.root"
var_name = "Dp_CMS_p"              # variable to compare
display_var_name = "D_{s}^{+} CMS Momentum (GeV/c)"
min_bin = 2.5
#max_bin = 6.0
max_bin = 7.5
#n_bins = 70
n_bins = 50
weight_hist_output = "Dp_CMS_p_weights.root"
plot_output_name = "Dp_CMS_p_weights_plot.png"

# === Load RooDataSets ===
root_file = ROOT.TFile(data_fname, "READ")
data_combined = root_file.Get("sweight")
data_combined.Print()

MC_root_file = ROOT.TFile(MC_fname, "READ")
MC_combined = MC_root_file.Get("sweight")
MC_combined.Print()

# === Create histograms ===
h_data = ROOT.TH1F("h_data", "Data Histogram", n_bins, float(min_bin), float(max_bin))
h_MC   = ROOT.TH1F("h_MC",   "MC Histogram",   n_bins, float(min_bin), float(max_bin))

h_data.Sumw2()
h_MC.Sumw2()

h_data.SetXTitle(display_var_name)
h_MC.SetXTitle(display_var_name)

# === Fill data histogram using sWeights ===
for i in range(data_combined.numEntries()):
    entry = data_combined.get(i)
    value = entry.getRealValue(var_name)
    weight = entry.getRealValue("N_total_sw")  # sWeight
    h_data.Fill(value, weight)

# === Fill MC histogram using sWeights (or plain weight = 1 if not sWeighted) ===
for i in range(MC_combined.numEntries()):
    entry = MC_combined.get(i)
    value = entry.getRealValue(var_name)
    weight = entry.getRealValue("N_total_sw")  # sWeight

    if i % 100000 == 0:
        print(f"MC Entry {i}: {var_name} = {value}, weight = {weight}")

    h_MC.Fill(value, weight)

# === Normalize (optional, you can comment this if absolute scale is needed) ===
h_data.Scale(1.0 / h_data.Integral())
h_MC.Scale(1.0 / h_MC.Integral())

# === Create weight histogram ===
h_weights = h_data.Clone("h_weights")
h_weights.SetTitle("Data / MC weights for Dp_CMS_p")
h_weights.Divide(h_MC)

for i in range(1, h_weights.GetNbinsX() + 1):
    content = h_weights.GetBinContent(i)
    print(f"Weight in the Bin content: {content}")

# === Save weight histogram to ROOT file ===
f_out = ROOT.TFile(weight_hist_output, "RECREATE")
h_weights.Write()
f_out.Close()

print(f"✅ Weight histogram saved to: {weight_hist_output}")


# === DRAWING THE PLOT ===
c1 = ROOT.TCanvas("c1", "c1", 800, 600)

h_weights.SetMinimum(0)
h_weights.SetMaximum(15)

# Draw with error bars ("E1")
h_weights.Draw("E1")

# Add a reference line at 1.0
line = ROOT.TLine(float(min_bin), 1.0, float(max_bin), 1.0)
line.SetLineColor(ROOT.kRed)
line.SetLineStyle(2) # Dashed line
line.Draw()

# Save the plot
c1.SaveAs(plot_output_name)
print(f"✅ Weight plot saved to: {plot_output_name}")
