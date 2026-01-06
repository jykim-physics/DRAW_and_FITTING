import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgSet, TChain, TCanvas, TLegend
import glob
import os
import argparse

# ==============================================================================
# 1. Setup & Arguments
# ==============================================================================
parser = argparse.ArgumentParser(description="Process Dp_CMS_sign argument")
parser.add_argument("-s","--sign", choices=["plus", "minus","all"], required=True,
                    help="Specify 'plus' or 'minus'")
#parser.add_argument("-t","--train", required=True,
#                    help="Specify train version")

args = parser.parse_args()
print(f"Dp_CMS_sign is set to: {args.sign}")

# Set CosTheta Cuts based on args
if args.sign == "plus":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>0"
elif args.sign == "minus":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta<0"
elif args.sign == "all":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>-10" # effectively no cut

# Load Belle2 Style
ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

# Shared Variables Definition
# We define these once to ensure consistency, though ranges might differ slightly per usage
fit_variable = "Dp_M"
fit_var_name = "M(D^{+}) [GeV/c^{2}]"

# RooRealVars
x = ROOT.RooRealVar(fit_variable, fit_var_name, 1.76, 1.96)
Pip_charge = ROOT.RooRealVar("Pip_charge", "Pip_charge", -1, 1)
Dp_CMS_cosTheta = ROOT.RooRealVar("Dp_CMS_cosTheta", "Dp_CMS_cosTheta", -1, 1)
Dp_isSignal = ROOT.RooRealVar("Dp_isSignal", "Dp_isSignal", 0, 1) # Added for the cut
etapip_Eta_Easym = ROOT.RooRealVar("etapip_Eta_Easym", "etapip_Eta_Easym", 0, 1) # Variable to plot

skimhad = ROOT.RooRealVar("skimhad", "skimhad", 0, 2)
Pip_p = ROOT.RooRealVar("Pip_p", "Pip_p", 0, 100)
etapip_Eta_daughterDiffOfPhi_0_1 = ROOT.RooRealVar("etapip_Eta_daughterDiffOfPhi_0_1", "DiffOfPhi", -10, 10)
etapip_Eta_daughterAngle_0_1 = ROOT.RooRealVar("etapip_Eta_daughterAngle_0_1", "Angle", -10, 10)

# Other variables needed for reading the trees
BDT = ROOT.RooRealVar("BDT", "BDT", 0, 1)
Pip_dr = ROOT.RooRealVar("Pip_dr", "Pip_dr", -10000, 10000)
Dp_dz = ROOT.RooRealVar("Dp_dz", "Dp_dz", -10000, 10000)
Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane = ROOT.RooRealVar("Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane", "Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane'", -1,1)
Dp_cosHelicityAngleMomentum = ROOT.RooRealVar("Dp_cosHelicityAngleMomentum", "Dp_cosHelicityAngleMomentum", -1, 1)
Dp_CMS_p = ROOT.RooRealVar("Dp_CMS_p", "Dp_CMS_p", 0, 100)
chiProb_rank = ROOT.RooRealVar("etapip_gg_rank", "etapip_gg_rank", 0, 30)

additional_cuts = " && skimhad==1 && Pip_p>0.4 && abs(etapip_Eta_daughterDiffOfPhi_0_1)<1.8 && etapip_Eta_daughterAngle_0_1<1.6"

# ==============================================================================
# 2. Process Generic MC (Input 1)
# ==============================================================================
print("\n--- Processing Generic MC ---")
base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/Kspip/MC15rd_Kspip_loose_v7_1_250228_Dp_CMS_p_v3"
cm_elements = ["MCrd_Ks_e7_18_4S_v3", "MCrd_Ks_e20_b26_v1", "MCrd_Ks_e20_e26_4S_v2", "MCrd_Ks_e21_5S_scan_v1", "MCrd_Ks_mori_off_v1"]
#cm_elements = ["MCrd_Ks_e20_b26_v1"]
ref_tree = "etapip_gg"
tree_name_generic = "Ks"

file_list_generic = []
for element in cm_elements:
    pattern = f"{base_path}/{element}/ccbar.root"
    file_list_generic += glob.glob(pattern)
print(f"Generic MC Files: {len(file_list_generic)}")

# Define Cuts for Generic MC (Added Dp_isSignal==1)
cuts_Dp_gen = "Pip_charge==1 && " + Dp_CMS_cosTheta_cut + " && Dp_isSignal==1" + additional_cuts
cuts_Dm_gen = "Pip_charge==-1 && " + Dp_CMS_cosTheta_cut + " && Dp_isSignal==1" + additional_cuts

# Chain and Dataset
chain_gen = ROOT.TChain(tree_name_generic)
for i in file_list_generic:
    chain_gen.Add(i)

chain_gen_cc = ROOT.TChain(tree_name_generic)
for i in file_list_generic:
    chain_gen_cc.Add(i)

# ArgSet must include Dp_isSignal to apply the cut
argset_gen = ROOT.RooArgSet(x, Pip_charge, Dp_CMS_cosTheta, Dp_isSignal, etapip_Eta_Easym,
                            Pip_dr, Dp_dz, Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane,
                            Dp_cosHelicityAngleMomentum, Dp_CMS_p,
                            skimhad, Pip_p, etapip_Eta_daughterDiffOfPhi_0_1, etapip_Eta_daughterAngle_0_1)

# Load D+
ds_gen_temp = ROOT.RooDataSet("ds_gen_temp", "", chain_gen, argset_gen, cuts_Dp_gen)
# Load D-
ds_gen_cc_temp = ROOT.RooDataSet("ds_gen_cc_temp", "", chain_gen_cc, argset_gen, cuts_Dm_gen)

# Apply Weights (1/4)
w_gen = ROOT.RooRealVar('w_gen', 'w', 0.25)
ds_gen_temp.addColumn(w_gen)
ds_gen_cc_temp.addColumn(w_gen)

data_generic = ROOT.RooDataSet(ds_gen_temp.GetName(), ds_gen_temp.GetTitle(), ds_gen_temp, ds_gen_temp.get(), '', 'w_gen')
data_generic_cc = ROOT.RooDataSet(ds_gen_cc_temp.GetName(), ds_gen_cc_temp.GetTitle(), ds_gen_cc_temp, ds_gen_cc_temp.get(), '', 'w_gen')

data_generic.append(data_generic_cc)
print(f"Generic MC Total Entries (Weighted): {data_generic.sumEntries()}")

# ==============================================================================
# 3. Process Signal MC (Input 2)
# ==============================================================================
print("\n--- Processing Signal MC ---")
sig_path_Dp = "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_gg/250216_loose_v7/250216*.root"
sig_path_Dm = "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_gg_cc/250216_loose_v7/250216*.root"
#sig_path_Dp = "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_gg/250216_loose_v7/250216_loose_v7_Dptoetapip_gg_exp012_4S_offres_mDST_e012_00.root"
#sig_path_Dm = "/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_gg_cc/250216_loose_v7/250216_loose_v7_Dptoetapip_gg_cc_exp012_4S_offres_mDST_e012_00.root"
tree_name_sig = "etapip_gg"

# Define Cuts for Signal MC (Added Dp_isSignal==1)
# Note: Rank cut was in your snippet, keeping it if variable exists, otherwise simplified to charge & signal
cuts_Dp_sig = "Pip_charge==1 && Dp_isSignal==1" + additional_cuts
cuts_Dm_sig = "Pip_charge==-1 && Dp_isSignal==1" + additional_cuts

# Chain
chain_sig = ROOT.TChain(tree_name_sig)
chain_sig.Add(sig_path_Dp)

chain_sig_cc = ROOT.TChain(tree_name_sig)
chain_sig_cc.Add(sig_path_Dm)

# ArgSet (Must include etapip_Eta_Easym to plot it!)
argset_sig = ROOT.RooArgSet(x, Dp_isSignal, Pip_charge, etapip_Eta_Easym,
                            skimhad, Pip_p, etapip_Eta_daughterDiffOfPhi_0_1, etapip_Eta_daughterAngle_0_1)

# Load D+
ds_sig_temp = ROOT.RooDataSet("ds_sig_temp", "", chain_sig, argset_sig, cuts_Dp_sig)
# Load D-
ds_sig_cc_temp = ROOT.RooDataSet("ds_sig_cc_temp", "", chain_sig_cc, argset_sig, cuts_Dm_sig)

# Apply Weights (1)
w_sig = ROOT.RooRealVar('w_sig', 'w', 1.0)
ds_sig_temp.addColumn(w_sig)
ds_sig_cc_temp.addColumn(w_sig)

data_signal = ROOT.RooDataSet(ds_sig_temp.GetName(), ds_sig_temp.GetTitle(), ds_sig_temp, ds_sig_temp.get(), '', 'w_sig')
data_signal_cc = ROOT.RooDataSet(ds_sig_cc_temp.GetName(), ds_sig_cc_temp.GetTitle(), ds_sig_cc_temp, ds_sig_cc_temp.get(), '', 'w_sig')

data_signal.append(data_signal_cc)
print(f"Signal MC Total Entries: {data_signal.sumEntries()}")

# ==============================================================================
# 4. Plotting: Normalized Comparison of etapip_Eta_Easym
# ==============================================================================
print("\n--- Drawing Normalized Plot ---")

# Create Histograms from RooDataSets
# Using createHistogram is convenient for normalization
hist_generic = data_generic.createHistogram("h_generic", etapip_Eta_Easym, RooFit.Binning(50, 0, 1))
hist_signal = data_signal.createHistogram("h_signal", etapip_Eta_Easym, RooFit.Binning(50, 0, 1))

# Normalize Histograms (Area = 1)
if hist_generic.Integral() > 0:
    hist_generic.Scale(1.0 / hist_generic.Integral())
if hist_signal.Integral() > 0:
    hist_signal.Scale(1.0 / hist_signal.Integral())

# Styling
hist_generic.SetLineColor(ROOT.kBlue)
hist_generic.SetLineWidth(3)
hist_generic.SetStats(0)

hist_signal.SetLineColor(ROOT.kRed)
hist_signal.SetLineWidth(3)
hist_signal.SetStats(0)
# Optional: dashed line for signal?
# hist_signal.SetLineStyle(2)

# Canvas setup
c1 = TCanvas("c1", "c1", 800, 600)
c1.cd()

# Determine Y-axis range to fit both
max_y = max(hist_generic.GetMaximum(), hist_signal.GetMaximum())
hist_generic.GetYaxis().SetRangeUser(0, max_y * 1.2) # Add 20% headroom
hist_generic.GetXaxis().SetTitle("Asymmetry of Energy(or momentum)")
hist_generic.GetYaxis().SetTitle("Normalized Entries")

# Draw
hist_generic.Draw("HIST")
hist_signal.Draw("HIST SAME")

# Legend
legend = TLegend(0.2, 0.15, 0.5, 0.3) # x1, y1, x2, y2
legend.SetBorderSize(0)
legend.SetFillColor(0)
legend.AddEntry(hist_generic, "Generic MC", "l")
legend.AddEntry(hist_signal, "Signal MC", "l")
legend.Draw()

# Save
output_plot_path = f"compare_Eta_Easym_{args.sign}.png"
c1.SaveAs(output_plot_path)
print(f"Plot saved to: {output_plot_path}")
