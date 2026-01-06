import ROOT

# === Setup Belle2 Style ===
# Ensure the path is correct for your environment
ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

# === User inputs ===
data_fname = "/share/storage/jykim/sweight/proc13/KsKp/gg/proc13_Kspip_gg_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct.root"
MC_fname = "/share/storage/jykim/sweight/MC15rd/KsKp/gg/MC15rd_Kspip_gg_K_fit_opt_loose_v7_fitv2_Ds_no_bdt_new_Ds_correct.root"

# === User inputs ===
var_name = "Dp_CMS_p"
display_var_name = "D_{s}^{+} CMS Momentum (GeV/c)"
min_bin = 2.5

# 1. Define your desired bins and width first
#n_bins = 50   #  bins
n_bins = 23 * 4   # 92 bins
#bin_width = 0.1 # Exact width you want
bin_width = 0.025 # Exact width you want

# 2. Calculate max_bin dynamically
# This ensures consistency: max = min + (N * width)
max_bin = min_bin + (n_bins * bin_width)

# Print to verify (use :.5f to hide the tiny floating point error)
print(f"Calculated max_bin: {max_bin}")
print(f"Width of one bin: {(max_bin - min_bin)/n_bins:.5f}")

weight_hist_output = "Dp_CMS_p_weights.root"
plot_output_name = "Dp_CMS_p_weights_plot.png"

# === Load RooDataSets ===
root_file = ROOT.TFile(data_fname, "READ")
data_combined = root_file.Get("sweight")

MC_root_file = ROOT.TFile(MC_fname, "READ")
MC_combined = MC_root_file.Get("sweight")

# === Create histograms ===
# Now use the calculated max_bin
h_data = ROOT.TH1F("h_data", "Data Histogram", n_bins, float(min_bin), float(max_bin))
h_MC   = ROOT.TH1F("h_MC",   "MC Histogram",   n_bins, float(min_bin), float(max_bin))

# Important: Sumw2 ensures errors are calculated as sqrt(sum(weights^2))
h_data.Sumw2()
h_MC.Sumw2()

h_data.SetXTitle(display_var_name)
h_MC.SetXTitle(display_var_name)

# === Fill data histogram using sWeights ===
for i in range(data_combined.numEntries()):
    entry = data_combined.get(i)
    value = entry.getRealValue(var_name)
    weight = entry.getRealValue("N_total_sw")
    h_data.Fill(value, weight)

# === Fill MC histogram using sWeights ===
for i in range(MC_combined.numEntries()):
    entry = MC_combined.get(i)
    value = entry.getRealValue(var_name)
    weight = entry.getRealValue("N_total_sw")

    #if i % 100000 == 0:
    #    print(f"MC Entry {i}: {var_name} = {value}, weight = {weight}")

    h_MC.Fill(value, weight)

# === Normalize ===
if h_data.Integral() > 0:
    h_data.Scale(1.0 / h_data.Integral())
if h_MC.Integral() > 0:
    h_MC.Scale(1.0 / h_MC.Integral())

# === Create weight histogram ===
h_weights = h_data.Clone("h_weights")
h_weights.SetTitle("Data/MC Weights")
h_weights.SetYTitle("Weight (Data / MC)")

# Divide propagates errors correctly because Sumw2 was called earlier
h_weights.Divide(h_MC)

# =================================================================
#  SAFETY CHECK: REMOVE NEGATIVE WEIGHTS
# =================================================================
# Iterates through all bins to find negative content (statistical fluctuation)
# and forces it to 0.0 to prevent physics tools from crashing.
for i in range(1, h_weights.GetNbinsX() + 2):
    content = h_weights.GetBinContent(i)
    print(f"Weight in the Bin content: {content}")
    if content < 0:
        print(f"⚠️ Warning: Negative weight ratio found in Bin {i} ({content:.4f}). Forcing to 1.0.")
        h_weights.SetBinContent(i, 1.0)
        h_weights.SetBinError(i, 0.0) # Reset error as well

overflow_index = h_weights.GetNbinsX() + 1
#underflow_index = 0  # 혹시 2.5 미만 값도 0으로 만들고 싶다면 사용

# 1. Overflow Bin (4.8 이상)을 0으로 설정
print(f"Checking Overflow Bin before clean: {h_weights.GetBinContent(overflow_index)}")
h_weights.SetBinContent(overflow_index, 1.0)
h_weights.SetBinError(overflow_index, 0.0)
print("✅ Overflow bin (>= 4.8) forced to 0.0")

for i in range(1, h_weights.GetNbinsX() + 2):
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
#h_weights.SetMaximum(15)

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
