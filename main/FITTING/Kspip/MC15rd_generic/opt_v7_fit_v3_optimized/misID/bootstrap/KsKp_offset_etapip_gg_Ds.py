import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory, RooStats, TFile
from ROOT.RooFit import Extended, FitOptions, Save, PrintEvalErrors, PrintLevel, Bins, FitGauss,    NumCPU, Strategy, Offset, SumW2Error, Range
import glob
import ctypes
import os
import argparse
import numpy as np
import gc
import time
import random
import uproot
import awkward as ak

parser = argparse.ArgumentParser(description="Process Dp_CMS_sign argument")
parser.add_argument("-s","--sign", choices=["plus", "minus","all"], required=True,
                    help="Specify 'plus' or 'minus'")
parser.add_argument("-t","--train", required=True,
                    help="Specify train version")
#parser.add_argument("-b","--bdt", required=True,
#                    help="Specify BDT value")

args = parser.parse_args()
print(f"Dp_CMS_sign is set to: {args.sign}")


#BDT_cut = str(args.bdt)
BDT_cut = "0.86"

if args.sign == "plus":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>0"
    N_scale = 0.64
elif args.sign == "minus":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta<0"
    N_scale = 0.43
elif args.sign == "all":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>-10"
    N_scale = 1

BDT_cut="0.86"
suffix = "sumw2fixed_weighted_misID_study"

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/Kspip/MC15rd_Kspip_loose_v7_1_260109"
cm_elements = ["MC_KsHp_e7_18_4S_v3", "MC_KsHp_e20_b26_v1", "MC_KsHp_e20_e26_4S_v2", "MC_KsHp_e21_5Sscan_v1", "MC_KsHp_mori_off_v1"]

ref_tree = "etapip_gg_K"
file_list = []
tree_name = "Ks_K"
for element in cm_elements:
    pattern = f"{base_path}/{element}/{ref_tree}/{tree_name}/{BDT_cut}/weighted/*BDT.root"
    file_list += glob.glob(pattern)
print(file_list)
print(f"Number of files: {len(file_list)}")

mychain = ROOT.TChain(tree_name)
for i in file_list:
    mychain.Add(i)

# Define variable and its range
fit_variable = "Dp_M"
fit_var_name = "M(D^{+}) [GeV/c^{2}]"
#fit_range = (1.66, 2.06)
fit_range = (1.7, 2.06)
fit_range = (1.9, 2.03)
#fit_range = (1.82, 1.92)
truth_var = "Dp_isSignal"
charge_var = "Pip_charge"
cuts_Dp = charge_var + "==1 && rank_Dp_chiProb==1"
cuts_Dm = charge_var + "==-1 && rank_Dp_chiProb==1"
cuts_Dp += " && " + Dp_CMS_cosTheta_cut
cuts_Dm += " && " + Dp_CMS_cosTheta_cut


x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
#x.setBins(200)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)
Dp_CMS_cosTheta = ROOT.RooRealVar("Dp_CMS_cosTheta", "Dp_CMS_cosTheta", -1, 1)
BDT = ROOT.RooRealVar("BDT", "BDT", 0, 1)
Pip_dr = ROOT.RooRealVar("Pip_dr", "Pip_dr", -10000, 10000)
Dp_dz = ROOT.RooRealVar("Dp_dz", "Dp_dz", -10000, 10000)
Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane = ROOT.RooRealVar("Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane",                                 "Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane'", -1,1)
Dp_cosHelicityAngleMomentum = ROOT.RooRealVar("Dp_cosHelicityAngleMomentum", "Dp_cosHelicityAngleMomentum", -1, 1)
Dp_CMS_p = ROOT.RooRealVar("Dp_CMS_p", "Dp_CMS_p", 0, 100)
rank_Dp_chiProb = ROOT.RooRealVar("rank_Dp_chiProb", "rank_Dp_chiProb", 0, 1000)
etapip_Eta_Easym = ROOT.RooRealVar("etapip_Eta_Easym", "etapip_Eta_Easym", 0, 1)
ds_weight = ROOT.RooRealVar("ds_weight", "ds_weight", 0, 1000)

full_var_set = ROOT.RooArgSet(x, Pip_charge, Dp_CMS_cosTheta, BDT, Pip_dr, Dp_dz,
                              Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane,
                              Dp_cosHelicityAngleMomentum,etapip_Eta_Easym,
                              Dp_CMS_p, rank_Dp_chiProb, ds_weight)

before_data = ROOT.RooDataSet("before_data","Data before weighting",full_var_set,ROOT.RooFit.Import(mychain),ROOT.RooFit.Cut(cuts_Dp))
scale = 1
w_scaled = ROOT.RooFormulaVar("w_scaled", "Scaled Weight", f"{scale}*ds_weight", ROOT.RooArgList(ds_weight))
before_data.addColumn(w_scaled)
data = ROOT.RooDataSet("data_weighted","Weighted Data",before_data,before_data.get(),"","w_scaled")
# Verify the weight is applied
print(f"Unweighted events: {before_data.sumEntries()}")
print(f"Weighted events: {data.sumEntries()}")

mychain_cc = ROOT.TChain(tree_name)
for i in file_list:
    mychain_cc.Add(i)
before_data_cc = ROOT.RooDataSet("before_data_cc","Data CC before weighting",full_var_set,ROOT.RooFit.Import(mychain_cc),ROOT.RooFit.Cut(cuts_Dm))
before_data_cc.addColumn(w_scaled)
data_cc = ROOT.RooDataSet("data_weighted_cc","Weighted Data CC",before_data_cc,before_data_cc.get(),"","w_scaled")
# Verify the weight is applied
print(f"Unweighted events: {before_data_cc.sumEntries()}")
print(f"Weighted events: {data_cc.sumEntries()}")

N_total = RooRealVar("N_total", "N_total (N_D+ + N_D-)", 300000*scale, 20000*scale, 1500000*scale)  # N_total = N_D+ + N_D-
Acp = RooRealVar("Acp", "Acp", 0, -1, 1)
Nsig_D_plus = RooFormulaVar("Nsig_D_plus",
    "0.5 * N_total * (1 + Acp)",
    RooArgList(N_total, Acp))
Nsig_D_minus = RooFormulaVar("Nsig_D_minus",
    "0.5 * N_total * (1 - Acp)",
    RooArgList(N_total, Acp))
Nbkg_total = ROOT.RooRealVar("Nbkg_total", "Number of background events for D+",  300000*scale,500*scale,3000000*scale)
Acp_bkg = RooRealVar("Acp_bkg", "Acp", 0, -1, 1)
Nbkg_D_plus = RooFormulaVar("Nbkg_D_plus",
    "0.5 * Nbkg_total * (1 + Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))
Nbkg_D_minus = RooFormulaVar("Nbkg_D_minus",
    "0.5 * Nbkg_total * (1 - Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))

#KDE_fit_result = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/KsKp/gg/KDE_MC15rd_KsKp_gg_kaon_misID_Dp_M_v3_result_true_extended_train_Dp_CMS_p.0.  86.{args.sign}.root")
#KDE_result_object = ROOT.gDirectory.Get("jykim")
#KDE_fit_result.Close()
#KDE_fit_args = KDE_result_object.floatParsFinal()
#N_peak_bkg_total_RooRealVar = KDE_fit_args.find("N_signal")
#N_peak_bkg_total = ROOT.RooRealVar("N_peak_bkg_total", "Number of background events",0.25 * N_peak_bkg_total_RooRealVar.getVal())
#print("N_peak_bkg_total  =", N_peak_bkg_total)

#Acp_peak_bkg = RooRealVar("Acp_peak_bkg", "Acp", 0, -1, 1)  # A_Cp as a fit parameter
#N_peak_bkg_D_plus = RooFormulaVar("N_peak_bkg_D_plus",
#    "0.5 * N_peak_bkg_total * (1 + Acp_peak_bkg)",
#    RooArgList(N_peak_bkg_total, Acp_peak_bkg))
#N_peak_bkg_D_minus = RooFormulaVar("N_peak_bkg_D_minus",
#    "0.5 * N_peak_bkg_total * (1 - Acp_peak_bkg)",
#    RooArgList(N_peak_bkg_total, Acp_peak_bkg))

#f_in = ROOT.TFile(f"/share/storage/jykim/plots/MC15rd/KsKp/gg/KDE_MC15rd_KsKp_gg_kaon_misID_Dp_M_v3_result_true_extended_train_Dp_CMS_p.0.86.{args.        sign}_workspace.root", "READ")
#ws = f_in.Get("ws_kde")
#kde_model = ws.pdf("model")
#kde_model.SetName("kde_model")

# Create a category to distinguish between D+ and D-
cat = RooCategory("sample", "sample")
cat.defineType("D_plus")
cat.defineType("D_minus")

def nominal_fit_extract_Acp(data_Dp, data_Dm):
  mean = ROOT.RooRealVar("mean", "mean", 1.97, 1.95, 1.98)  # Central value
  sigma = ROOT.RooRealVar("sigma", "sigma", 0.002, 0.0001, 0.01)  # Width parameter
  gamma = ROOT.RooRealVar("gamma", "gamma", 0.01, -2.0, 2.0)  # Skewness parameter
  delta = ROOT.RooRealVar("delta", "delta", 0.6, 0.001, 3.0)  # Shape parameter

  johnson = ROOT.RooJohnson("johnson", "double-sided Crystal Ball using Johnson SU", x,  mean, sigma, gamma, delta)

  mean_gauss = ROOT.RooRealVar("mean_gauss", "Gaussian mean", 0.0)  # Convolution will   center the Gaussian at zero
  sigma_gauss = ROOT.RooRealVar("sigma_gauss", "Gaussian width", 0.002, 0.00001, 0.01)

# Create the Gaussian PDF
  gauss = ROOT.RooGaussian("gauss", "Gaussian PDF", x, mean_gauss, sigma_gauss)

# Perform the convolution
  sig_model = ROOT.RooFFTConvPdf("sig_model", "Convolution of Johnson SU and Gaussian", x, johnson, gauss)

  x_bkg1_tau = ROOT.RooRealVar("x_bkg1_tau", "c0",-0.5, -20, 10)
  model_bkg = ROOT.RooExponential("model_bkg", "x_bkg1", x, x_bkg1_tau)

# Define extended PDFs for D+ and D-
  model_D_plus = ROOT.RooAddPdf("model_D_plus", "D+ model",
                                ROOT.RooArgList(sig_model,  model_bkg),
                                ROOT.RooArgList(Nsig_D_plus,  Nbkg_D_plus))
  model_D_minus = ROOT.RooAddPdf("model_D_minus", "D- model",
                                ROOT.RooArgList(sig_model,  model_bkg),
                                ROOT.RooArgList(Nsig_D_minus,  Nbkg_D_minus))

# Create a simultaneous PDF using the category
  sim_model = RooSimultaneous("sim_model", "Simultaneous model", cat)
  sim_model.addPdf(model_D_plus, "D_plus")
  sim_model.addPdf(model_D_minus, "D_minus")
  data_combined = RooDataSet("data_combined", "Combined", full_var_set, RooFit.Index(cat),
                                RooFit.Import("D_plus", data_Dp),
                                RooFit.Import("D_minus", data_Dm),
                                RooFit.WeightVar("w_scaled"))
  fit_result_temp = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4), RooFit.Strategy(1), ROOT.RooFit.Offset(True), ROOT.RooFit.Silence(True), ROOT.RooFit.PrintLevel(-1), ROOT.RooFit.Verbose(False))
  # 1. Get MIGRAD status
  # 0 means success. Anything else (1, 4, etc.) indicates issues.
  status_migrad = fit_result_temp.status()

  # 2. Get HESSE status (Covariance Matrix Quality)
  # 3 = Full, accurate covariance matrix (Success)
  # 2 = Full matrix, but forced positive-definite
  # 1 = Approximate matrix
  # 0 = Not calculated or failed
  status_hesse = fit_result_temp.covQual()

  return Acp.getVal(), status_migrad, status_hesse, N_total.getVal(), Acp.getError()

N_total_var = RooRealVar("N_total_var", "N_total (N_D+ + N_D-)", 300000*scale, 20000*scale, 1500000*scale)  # N_total = N_D+ + N_D-
Acp_var = RooRealVar("Acp_var", "Acp", 0, -1, 1)
Nsig_D_plus_var = RooFormulaVar("Nsig_D_plus_var",
    "0.5 * N_total_var * (1 + Acp_var)",
    RooArgList(N_total_var, Acp_var))
Nsig_D_minus_var = RooFormulaVar("Nsig_D_minus_var",
    "0.5 * N_total_var * (1 - Acp_var)",
    RooArgList(N_total_var, Acp_var))
Nbkg_total_var = ROOT.RooRealVar("Nbkg_total_var", "Number of background events for D+",  300000*scale,500*scale,3000000*scale)
Acp_bkg_var = RooRealVar("Acp_bkg_var", "Acp", 0, -1, 1)
Nbkg_D_plus_var = RooFormulaVar("Nbkg_D_plus_var",
    "0.5 * Nbkg_total_var * (1 + Acp_bkg_var)",
    RooArgList(Nbkg_total_var, Acp_bkg_var))
Nbkg_D_minus_var = RooFormulaVar("Nbkg_D_minus_var",
    "0.5 * Nbkg_total_var * (1 - Acp_bkg_var)",
    RooArgList(Nbkg_total_var, Acp_bkg_var))

KDE_fit_result_var = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/KsKp/gg/KDE_MC15rd_KsKp_gg_kaon_misID_Dp_M_v3_result_true_extended_train_Dp_CMS_p.0.86.{args.sign}.root")
KDE_result_object_var = ROOT.gDirectory.Get("jykim")
KDE_fit_result_var.Close()
KDE_fit_args_var = KDE_result_object_var.floatParsFinal()
N_peak_bkg_total_RooRealVar_var = KDE_fit_args_var.find("N_signal")
N_peak_bkg_total_var = ROOT.RooRealVar("N_peak_bkg_total_var", "Number of background events",0.25 * N_peak_bkg_total_RooRealVar_var.getVal())
print("N_peak_bkg_total_var  =", N_peak_bkg_total_var)

Acp_peak_bkg_var = RooRealVar("Acp_peak_bkg_var", "Acp", 0, -1, 1)  # A_Cp as a fit parameter
N_peak_bkg_D_plus_var = RooFormulaVar("N_peak_bkg_D_plus_var",
    "0.5 * N_peak_bkg_total_var * (1 + Acp_peak_bkg_var)",
    RooArgList(N_peak_bkg_total_var, Acp_peak_bkg_var))
N_peak_bkg_D_minus_var = RooFormulaVar("N_peak_bkg_D_minus_var",
    "0.5 * N_peak_bkg_total_var * (1 - Acp_peak_bkg_var)",
    RooArgList(N_peak_bkg_total_var, Acp_peak_bkg_var))

f_in_var = ROOT.TFile(f"/share/storage/jykim/plots/MC15rd/KsKp/gg/KDE_MC15rd_KsKp_gg_kaon_misID_Dp_M_v3_result_true_extended_train_Dp_CMS_p.0.86.{args.sign}_workspace.root", "READ")
ws_var = f_in_var.Get("ws_kde")
kde_model_var = ws_var.pdf("model")
kde_model_var.SetName("kde_model_var")
def var_fit_extract_Acp(data_Dp, data_Dm, n_bootstrap):
  mean_var = ROOT.RooRealVar("mean_var", "mean", 1.97, 1.95, 1.98)  # Central value
  sigma_var = ROOT.RooRealVar("sigma_var", "sigma", 0.002, 0.0001, 0.01)  # Width parameter
  gamma_var = ROOT.RooRealVar("gamma_var", "gamma", 0.01, -2.0, 2.0)  # Skewness parameter
  delta_var = ROOT.RooRealVar("delta_var", "delta", 0.6, 0.001, 3.0)  # Shape parameter

  johnson_var = ROOT.RooJohnson("johnson_var", "double-sided Crystal Ball using Johnson SU", x,  mean_var, sigma_var, gamma_var, delta_var)

  mean_gauss_var = ROOT.RooRealVar("mean_gauss_var", "Gaussian mean", 0.0)  # Convolution will   center the Gaussian at zero
  sigma_gauss_var = ROOT.RooRealVar("sigma_gauss_var", "Gaussian width", 0.002, 0.00001, 0.01)

# Create the Gaussian PDF
  gauss_var = ROOT.RooGaussian("gauss_var", "Gaussian PDF", x, mean_gauss_var, sigma_gauss_var)

# Perform the convolution
  sig_model_var = ROOT.RooFFTConvPdf("sig_model_var", "Convolution of Johnson SU and Gaussian", x, johnson_var, gauss_var)

  x_bkg1_tau_var = ROOT.RooRealVar("x_bkg1_tau_var", "c0",-0.5, -20, 10)
  model_bkg_var = ROOT.RooExponential("model_bkg_var", "x_bkg1", x, x_bkg1_tau_var)

# Define extended PDFs for D+ and D-
  model_D_plus_var = ROOT.RooAddPdf("model_D_plus_var", "D+ model",
                                ROOT.RooArgList(sig_model_var,  model_bkg_var, kde_model_var),
                                ROOT.RooArgList(Nsig_D_plus_var,  Nbkg_D_plus_var, N_peak_bkg_D_plus_var))
  model_D_minus_var = ROOT.RooAddPdf("model_D_minus_var", "D- model",
                                ROOT.RooArgList(sig_model_var,  model_bkg_var, kde_model_var),
                                ROOT.RooArgList(Nsig_D_minus_var,  Nbkg_D_minus_var, N_peak_bkg_D_minus_var))

# Create a simultaneous PDF using the category
  sim_model_var = RooSimultaneous("sim_model_var", "Simultaneous model", cat)
  sim_model_var.addPdf(model_D_plus_var, "D_plus")
  sim_model_var.addPdf(model_D_minus_var, "D_minus")
  data_combined_var = RooDataSet("data_combined_var", "Combined", full_var_set, RooFit.Index(cat),
                                RooFit.Import("D_plus", data_Dp),
                                RooFit.Import("D_minus", data_Dm),
                                RooFit.WeightVar("w_scaled"))
  fit_result_var = sim_model_var.fitTo(data_combined_var, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4), RooFit.Strategy(1), ROOT.RooFit.Offset(True), ROOT.RooFit.Silence(True), ROOT.RooFit.PrintLevel(-1), ROOT.RooFit.Verbose(False))
  # 1. Get MIGRAD status
  # 0 means success. Anything else (1, 4, etc.) indicates issues.
  status_migrad = fit_result_var.status()

  # 2. Get HESSE status (Covariance Matrix Quality)
  # 3 = Full, accurate covariance matrix (Success)
  # 2 = Full matrix, but forced positive-definite
  # 1 = Approximate matrix
  # 0 = Not calculated or failed
  status_hesse = fit_result_var.covQual()

  return Acp_var.getVal(), status_migrad, status_hesse, N_total_var.getVal(), Acp_var.getError(), Acp_peak_bkg_var.getVal()


n_bootstrap = 1000
#n_bootstrap = 10
results = {
    "acp_before": [],
    "acp_after": [],
    "delta_acp": [],
    "acp_peak_bkg_after": [],
    "acp_before_unc": [],
    "acp_after_unc": [],
    "N_before": [],
    "N_after": [],
    "delta_N": [],
    "relative_delta_N": [],
    "status_migrad_before": [],
    "status_hesse_before": [],
    "status_migrad_after": [],
    "status_hesse_after": []
}

n_entries_Dp = int(data.numEntries()/4)
n_entries_Dm = int(data_cc.numEntries()/4)

success_count = 0
iteration = 0

while success_count < n_bootstrap:
    iteration += 1
    data_boot_Dp = data.emptyClone()
    data_boot_Dm = data_cc.emptyClone()

    for _ in range(n_entries_Dp):
        idx = random.randint(0, data.numEntries() - 1)
        data_boot_Dp.add(data.get(idx), data.weight())

    for _ in range(n_entries_Dm):
        idx = random.randint(0, data_cc.numEntries() - 1)
        data_boot_Dm.add(data_cc.get(idx), data_cc.weight())

    fit_outputs_before = nominal_fit_extract_Acp(data_boot_Dp, data_boot_Dm)
    fit_outputs_after = var_fit_extract_Acp(data_boot_Dp, data_boot_Dm, iteration)

    sm_b = fit_outputs_before[1]
    sh_b = fit_outputs_before[2]
    sm_a = fit_outputs_after[1]
    sh_a = fit_outputs_after[2]

    # Check if both fits converged properly
    if sm_b == 0 and (sh_b == 3 or sh_b == 2) and sm_a == 0 and (sh_a == 3 or sh_a ==2):
        acp_before = fit_outputs_before[0]
        acp_after = fit_outputs_after[0]
        delta_acp = acp_after - acp_before
        acp_before_unc = fit_outputs_before[4]
        acp_after_unc = fit_outputs_after[4]
        acp_peak_bkg_after = fit_outputs_after[5]

        ndp_before = fit_outputs_before[3]
        ndp_after = fit_outputs_after[3]

        delta_ndp = ndp_after - ndp_before
        relative_delta_ndp = delta_ndp / ndp_before

        results["acp_before"].append(acp_before)
        results["acp_after"].append(acp_after)
        results["delta_acp"].append(delta_acp)
        results["acp_before_unc"].append(acp_before_unc)
        results["acp_after_unc"].append(acp_after_unc)
        results["acp_peak_bkg_after"].append(acp_peak_bkg_after)
        results["status_migrad_before"].append(sm_b)
        results["status_hesse_before"].append(sh_b)
        results["status_migrad_after"].append(sm_a)
        results["status_hesse_after"].append(sh_a)
        results["N_before"].append(ndp_before)
        results["N_after"].append(ndp_after)
        results["delta_N"].append(delta_ndp)
        results["relative_delta_N"].append(relative_delta_ndp)

        success_count += 1
        print(f"[{success_count}/{n_bootstrap}] successful bootstrap. ΔAcp = {delta_acp:.8f}")
    else:
        print(f"[{iteration}] Fit did not converge properly. Retrying... (sm_b={sm_b}, sh_b={sh_b}, sm_a={sm_a}, sh_a={sh_a})")

    del data_boot_Dp
    del data_boot_Dm
    gc.collect()

ak_array = ak.Array(results)
with uproot.recreate(f"bootstrap_acp_results_etapip_gg_K_{args.sign}_converge.root") as f:
    f["acp_bootstrap"] = ak_array

# Final results
delta_acp_array = np.array(results["delta_acp"])

mean_shift = np.mean(delta_acp_array)
rms_shift = np.std(delta_acp_array)

print(f"Bootstrap results:")
print(f"  Mean shift in ΔA_CP = {mean_shift:.8f}")
print(f"  RMS uncertainty     = {rms_shift:.8f}")
