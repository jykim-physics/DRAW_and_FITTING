import ROOT
import sys
import ctypes # Required for ROOT error references in Python

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
cut_value = float(sys.argv[10])

ROOT.gROOT.SetBatch(True)
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
    h_data.Fill(target_value, N_total_sw)

# --- Fill MC ---
print(">>> Filling MC Histogram...")
for i in range(MC_combined.numEntries()):
    entry = MC_combined.get(i)
    target_value = entry.getRealValue(f"{var_name}")
    N_total_sw = entry.getRealValue("N_total_sw")
    h_MC.Fill(target_value, N_total_sw)

# ==============================================================================
#  CALCULATE EFFICIENCY WITH ERRORS
# ==============================================================================

def get_efficiency_and_error(h, cut_val):
    """
    Calculates efficiency and proper error for weighted histograms
    by treating Pass and Fail regions as independent.
    Efficiency = Pass / (Pass + Fail)
    """
    bin_cut = h.FindBin(cut_val)
    n_bins = h.GetNbinsX()

    # Define C-types doubles for ROOT to fill with errors
    err_pass = ctypes.c_double(0.0)
    err_fail = ctypes.c_double(0.0)

    # 1. Integrate Pass Region (Bin 1 to Cut Bin)
    # Note: Assumes integration starts from min_bin.
    # If variable > cut_val is required, switch to (bin_cut, n_bins)
    val_pass = h.IntegralAndError(1, bin_cut, err_pass)

    # 2. Integrate Fail Region (Cut Bin + 1 to End)
    val_fail = h.IntegralAndError(bin_cut + 1, n_bins, err_fail)

    val_total = val_pass + val_fail

    # Retrieve values from ctypes
    sigma_pass = err_pass.value
    sigma_fail = err_fail.value

    if val_total == 0:
        return 0.0, 0.0, 0.0, 0.0

    # Efficiency
    eff = val_pass / val_total

    # Error Propagation for Ratio P / (P + F)
    # sigma_eff = (1 / Total^2) * sqrt( F^2 * sigma_P^2 + P^2 * sigma_F^2 )
    numerator = (val_fail**2 * sigma_pass**2) + (val_pass**2 * sigma_fail**2)
    sigma_eff = (1.0 / (val_total**2)) * (numerator ** 0.5)

    return eff, sigma_eff, val_pass, val_total

# --- Calculate ---
eff_data, err_data, pass_data, tot_data = get_efficiency_and_error(h_data, cut_value)
eff_mc, err_mc, pass_mc, tot_mc = get_efficiency_and_error(h_MC, cut_value)

# --- Ratio & Relative Diff ---
ratio = 0.0
err_ratio = 0.0
rel_diff = 0.0
err_rel_diff = 0.0

if eff_mc > 0:
    # Ratio = Data / MC
    ratio = eff_data / eff_mc

    # Error prop: R * sqrt( (dData/Data)^2 + (dMC/MC)^2 )
    err_ratio = abs(ratio) * ((err_data/eff_data)**2 + (err_mc/eff_mc)**2)**0.5

    # Relative Diff = (Data - MC) / MC = Ratio - 1
    # The error on (Ratio - 1) is the same as the error on Ratio
    rel_diff = (eff_data - eff_mc) / eff_mc
    err_rel_diff = err_ratio

# --- Print Results ---
print("-" * 80)
print(f"EFFICIENCY ANALYSIS for: {var_name}")
print(f"Range: [{min_bin} , {cut_value}]")
print("-" * 80)
print(f"Data: {eff_data:.6f} +/- {err_data:.6f}  (Pass: {pass_data:.1f} / Tot: {tot_data:.1f})")
print(f"MC:   {eff_mc:.6f} +/- {err_mc:.6f}  (Pass: {pass_mc:.1f} / Tot: {tot_mc:.1f})")
print("-" * 80)
if eff_mc > 0:
    print(f"Data/MC Ratio:    {ratio:.6f} +/- {err_ratio:.6f}")
    print(f"(Data-MC)/MC:     {rel_diff:.6f} +/- {err_rel_diff:.6f}")
else:
    print("MC Efficiency is 0, cannot calculate ratios.")
print("-" * 80)


# Normalization for Plotting
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
