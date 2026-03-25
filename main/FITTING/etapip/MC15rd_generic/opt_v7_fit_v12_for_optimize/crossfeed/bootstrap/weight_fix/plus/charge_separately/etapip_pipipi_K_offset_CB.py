import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory
from ROOT.RooFit import Extended, FitOptions, Save, PrintEvalErrors, PrintLevel, Bins, FitGauss,    NumCPU, Strategy, Offset
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

#ROOT.RooRandom.randomGenerator().SetSeed(12345)


parser = argparse.ArgumentParser(description="Process Dp_CMS_sign argument")
parser.add_argument("-s","--sign", choices=["plus", "minus","all"], required=True,
                    help="Specify 'plus' or 'minus'")
parser.add_argument("-t","--train", required=True,
                    help="Specify train version")
#parser.add_argument("-b","--bdt", required=True,
#                    help="Specify BDT cut")

args = parser.parse_args()
print(f"Dp_CMS_sign is set to: {args.sign}")

#BDT_cut = str(args.bdt)
BDT_cut = "0.77"

def sample_param(mu, sigma):
  seed = int(time.time_ns())  # current time in nanoseconds
  rng = np.random.default_rng(seed)
  sample_value = rng.normal(mu, sigma)
  return sample_value

if args.sign == "plus":
	Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>0"
	N_scale = 0.64
elif args.sign == "minus":
	Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta<0"
	N_scale = 0.43
elif args.sign == "all":
	Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>-10"
	N_scale = 1

suffix = "sumw2fixed"
file_name_Dall = f"/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/crossfeed/bootstrap_sys_MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv12_bdt_{args.train}_Dall_CMS_{args.sign}_{BDT_cut}_{suffix}_weighted_Dall"
dir_path = os.path.dirname(file_name_Dall)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto"
cm_elements = ["15rd_jae_e7_18_4S_v3", "15rd_jae_e20_b26_v1", "15rd_jae_e20_e26_4S_v2", "15rd_jae_e21_5S_scan_v1", "15rd_jae_mori_off_v1"]

tree_name = "etapip_pipipi_K"
file_list = []
for element in cm_elements:
    pattern = f"{base_path}/{element}/{tree_name}/min_unc_search/{BDT_cut}/weighted/*BDT.root"
    file_list += glob.glob(pattern)

print(file_list)
mychain = ROOT.TChain(tree_name)
for i in file_list:
    mychain.Add(i)
print(file_list)
print(f"Numer of files: {len(file_list)}")

# Define variable and its range
fit_variable = "Dp_M"
fit_var_name = "M(#eta_{#pi#pi#pi}K^{+}) [GeV/c^{2}]"
fit_range = (1.75, 2.045)
#fit_range = (1.755, 2.045)
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
Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane = ROOT.RooRealVar("Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane", "Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane'", -1,1)
#etapip_Eta_Easym = ROOT.RooRealVar("etapip_Eta_Easym", "etapip_Eta_Easym", 0, 1)
Dp_cosHelicityAngleMomentum = ROOT.RooRealVar("Dp_cosHelicityAngleMomentum", "Dp_cosHelicityAngleMomentum", -1, 1)
Dp_CMS_p = ROOT.RooRealVar("Dp_CMS_p", "Dp_CMS_p", 0, 100)
ds_weight = ROOT.RooRealVar("ds_weight", "ds_weight", -1000, 1000)
rank_Dp_chiProb = ROOT.RooRealVar("rank_Dp_chiProb", "rank_Dp_chiProb", 0, 1000)
Pip_genMotherID = ROOT.RooRealVar("Pip_genMotherID", "Pip_genMotherID", -1E9, 1E9)
etapip_Eta_genMotherID = ROOT.RooRealVar("etapip_Eta_genMotherID", "etapip_Eta_genMotherID", -1E9, 1E9)
etapip_Eta_genMotherPDG = ROOT.RooRealVar("etapip_Eta_genMotherPDG", "etapip_Eta_genMotherPDG", -1E9, 1E9)
Pip_mcPDG = ROOT.RooRealVar("Pip_mcPDG", "Pip_mcPDG", -1E9, 1E9)
etapip_Eta_isSignal = ROOT.RooRealVar("etapip_Eta_isSignal", "etapip_Eta_isSignal", -1E9, 1E9)

full_var_set = ROOT.RooArgSet(x, Pip_charge, Dp_CMS_cosTheta, BDT, Pip_dr, Dp_dz,
                              Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane,
                              Dp_cosHelicityAngleMomentum,
                              Dp_CMS_p,rank_Dp_chiProb,ds_weight, Pip_genMotherID, etapip_Eta_genMotherID, etapip_Eta_genMotherPDG, Pip_mcPDG, etapip_Eta_isSignal)

before_data = ROOT.RooDataSet("before_data","Data before weighting",full_var_set,ROOT.RooFit.Import(mychain),ROOT.RooFit.Cut(cuts_Dp))
scale = 1/4
data_scale = 1
w_scaled = ROOT.RooFormulaVar("w_scaled", "Scaled Weight", f"{data_scale}*ds_weight", ROOT.RooArgList(ds_weight))
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

N_total = RooRealVar("N_total", "N_total (N_D+ + N_D-)", 1600*scale*N_scale, 0*scale*N_scale, 5000*scale*N_scale)  # N_total = N_D+ + N_D-
Acp = RooRealVar("Acp", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

# Use Acp and N_total to define the expected signal yields for D+ and D-
Nsig_D_plus = RooFormulaVar("Nsig_D_plus",
    "0.5 * N_total * (1 + Acp)",
    RooArgList(N_total, Acp))

Nsig_D_minus = RooFormulaVar("Nsig_D_minus",
    "0.5 * N_total * (1 - Acp)",
    RooArgList(N_total, Acp))

N_total_Ds = RooRealVar("N_total_Ds", "N_total (N_Ds+ + N_Ds-)", 10000*scale*N_scale, 0*scale*N_scale,20000*scale*N_scale)  # N_total = N_D+ + N_D-
Acp_Ds = RooRealVar("Acp_Ds", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

# Use Acp and N_total to define the expected signal yields for D+ and D-
Nsig_Ds_plus = RooFormulaVar("Nsig_Ds_plus",
    "0.5 * N_total_Ds * (1 + Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))

Nsig_Ds_minus = RooFormulaVar("Nsig_Ds_minus",
    "0.5 * N_total_Ds * (1 - Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))


Nbkg_total = ROOT.RooRealVar("Nbkg_total", "Number of background events for D+", 40000*scale*N_scale, 0*scale*N_scale,100000*scale*N_scale)
Acp_bkg = RooRealVar("Acp_bkg", "Acp", 0, -1, 1)  # A_Cp as a fit parameter
Nbkg_D_plus = RooFormulaVar("Nbkg_D_plus",
    "0.5 * Nbkg_total * (1 + Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))

Nbkg_D_minus = RooFormulaVar("Nbkg_D_minus",
    "0.5 * Nbkg_total * (1 - Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))

f = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv12_bdt_train_Dp_CMS_p_{args.sign}_0.77_sumw2fixed_weighted.root")
result_object = ROOT.gDirectory.Get("jykim")
f.Close()
#result_object.Print("v")
fit_args = result_object.floatParsFinal()
const_args = result_object.constPars()

mean = fit_args.find("mean")
scale_factor = fit_args.find("scale_factor")
Ds_mean = fit_args.find("Ds_mean")
x_bkg1_c1 = fit_args.find("x_bkg1_c1")
x_bkg1_c2 = fit_args.find("x_bkg1_c2")
#x_bkg1_tau = fit_args.find("x_bkg1_tau")

sigmaL = const_args.find("sigmaL")
sigmaR = const_args.find("sigmaR")
alphaL = const_args.find("alphaL")
nL = const_args.find("nL")
alphaR = const_args.find("alphaR")
nR = const_args.find("nR")


Ds_sigmaL = const_args.find("Ds_sigmaL")
Ds_sigmaR = const_args.find("Ds_sigmaR")
Ds_alphaL = const_args.find("Ds_alphaL")
Ds_nL = const_args.find("Ds_nL")
Ds_alphaR = const_args.find("Ds_alphaR")
Ds_nR = const_args.find("Ds_nR")

sigma_gaussian = const_args.find("sigma_gaussian")
Ds_sigma_gaussian = const_args.find("Ds_sigma_gaussian")

mean_gaussian = const_args.find("mean_gaussian")
Ds_mean_gaussian = const_args.find("Ds_mean_gaussian")

scaled_sigma_gaussian = RooFormulaVar("scaled_sigma_gaussian","sigma_gaussian * scale_factor",RooArgList(sigma_gaussian, scale_factor))
scaled_Ds_sigma_gaussian = RooFormulaVar("Ds_scaled_sigma_gaussian","Ds_sigma_gaussian * scale_factor",RooArgList(Ds_sigma_gaussian, scale_factor))

def nominal_fit_extract_Acp(data_Dp, data_Dm):
  CB = ROOT.RooCrystalBall("CB", "CB_left", x, mean, sigmaL,sigmaR, alphaL, nL, alphaR, nR)
  gaussian = ROOT.RooGaussian("gaussian", "Gaussian PDF", x, mean_gaussian, scaled_sigma_gaussian)
  sig_model = ROOT.RooFFTConvPdf("sig_model", "Convolution of Johnson and Gaussian", x, CB, gaussian)

  Ds_CB = ROOT.RooCrystalBall("Ds_CB", "CB_left", x, Ds_mean, Ds_sigmaL, Ds_sigmaR, Ds_alphaL, Ds_nL, Ds_alphaR, Ds_nR)
  Ds_gaussian = ROOT.RooGaussian("Ds_gaussian", "Gaussian PDF", x, Ds_mean_gaussian, scaled_Ds_sigma_gaussian)
  Ds_model = ROOT.RooFFTConvPdf("Ds_model", "Convolution of Johnson and Gaussian", x, Ds_CB, Ds_gaussian)

  #model_bkg = ROOT.RooExponential("model_bkg", "x_bkg1", x, x_bkg1_tau)
  model_bkg = ROOT.RooPolynomial("model_bkg", "x_bkg1", x, ROOT.RooArgList(x_bkg1_c1, x_bkg1_c2))


  model_D_plus = ROOT.RooAddPdf("model_D_plus", "D+ model",
                                ROOT.RooArgList(sig_model, Ds_model, model_bkg),
                                ROOT.RooArgList(Nsig_D_plus, Nsig_Ds_plus, Nbkg_D_plus))
  model_D_minus = ROOT.RooAddPdf("model_D_minus", "D- model",
                                ROOT.RooArgList(sig_model, Ds_model, model_bkg),
                                ROOT.RooArgList(Nsig_D_minus, Nsig_Ds_minus, Nbkg_D_minus))
# Create a simultaneous PDF using the category
  sim_model = RooSimultaneous("sim_model", "Simultaneous model", cat)
  sim_model.addPdf(model_D_plus, "D_plus")
  sim_model.addPdf(model_D_minus, "D_minus")
  data_combined = RooDataSet("data_combined", "Combined", full_var_set, RooFit.Index(cat),
                                RooFit.Import("D_plus", data_Dp),
                                RooFit.Import("D_minus", data_Dm),
                                RooFit.WeightVar("w_scaled"))
  fit_result_temp = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4), RooFit.Strategy(1), ROOT.RooFit.Offset(True), ROOT.RooFit.           Silence(True), ROOT.RooFit.PrintLevel(-1), ROOT.RooFit.Verbose(False))
  # 1. Get MIGRAD status
  # 0 means success. Anything else (1, 4, etc.) indicates issues.
  status_migrad = fit_result_temp.status()

  # 2. Get HESSE status (Covariance Matrix Quality)
  # 3 = Full, accurate covariance matrix (Success)
  # 2 = Full matrix, but forced positive-definite
  # 1 = Approximate matrix
  # 0 = Not calculated or failed
  status_hesse = fit_result_temp.covQual()

  return Acp.getVal(), status_migrad, status_hesse, N_total.getVal(), N_total_Ds.getVal(), Acp_Ds.getVal()

N_total_var = RooRealVar("N_total_var", "N_total (N_D+ + N_D-)", 1600*scale*N_scale, 0*scale*N_scale, 5000*scale*N_scale)  # N_total = N_D+ + N_D-
Acp_var = RooRealVar("Acp_var", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

Nsig_D_plus_var = RooFormulaVar("Nsig_D_plus_var",
    "0.5 * N_total_var * (1 + Acp_var)",
    RooArgList(N_total_var, Acp_var))

Nsig_D_minus_var = RooFormulaVar("Nsig_D_minus_var",
    "0.5 * N_total_var * (1 - Acp_var)",
    RooArgList(N_total_var, Acp_var))

N_total_Ds_var = RooRealVar("N_total_Ds_var", "N_total (N_Ds+ + N_Ds-)", 10000*scale*N_scale, 0*scale*N_scale,20000*scale*N_scale)  # N_total = N_D+ + N_D-
Acp_Ds_var = RooRealVar("Acp_Ds_var", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

Nsig_Ds_plus_var = RooFormulaVar("Nsig_Ds_plus_var",
    "0.5 * N_total_Ds_var * (1 + Acp_Ds_var)",
    RooArgList(N_total_Ds_var, Acp_Ds_var))

Nsig_Ds_minus_var = RooFormulaVar("Nsig_Ds_minus_var",
    "0.5 * N_total_Ds_var * (1 - Acp_Ds_var)",
    RooArgList(N_total_Ds_var, Acp_Ds_var))


Nbkg_total_var = ROOT.RooRealVar("Nbkg_total_var", "Number of background events for D+", 40000*scale*N_scale, 0*scale*N_scale,100000*scale*N_scale)
Acp_bkg_var= RooRealVar("Acp_bkg_var", "Acp", 0, -1, 1)  # A_Cp as a fit parameter
Nbkg_D_plus_var = RooFormulaVar("Nbkg_D_plus_var",
    "0.5 * Nbkg_total_var * (1 + Acp_bkg_var)",
    RooArgList(Nbkg_total_var, Acp_bkg_var))

Nbkg_D_minus_var = RooFormulaVar("Nbkg_D_minus_var",
    "0.5 * Nbkg_total_var * (1 - Acp_bkg_var)",
    RooArgList(Nbkg_total_var, Acp_bkg_var))

#mean_var = ROOT.RooRealVar("mean_var", "mean_var", 1.87, 1.85, 1.89)
#scale_factor_var = ROOT.RooRealVar("scale_factor_var", "sigma of Gaussian", 1,0,2)
#Ds_mean_var = ROOT.RooRealVar("Ds_mean_var", "mean", 1.97, 1.95, 1.99)
#x_bkg1_c1_var = ROOT.RooRealVar("x_bkg1_c1_var", "c0",0.1, -1.0, 1.0)
#x_bkg1_c2_var = ROOT.RooRealVar("x_bkg1_c2_var", "c0",0.1, -1.0, 1.0)

g = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv12_bdt_train_Dp_CMS_p_{args.sign}_0.77_sumw2fixed_weighted.root")
result_object_var = ROOT.gDirectory.Get("jykim")
g.Close()
fit_args_var = result_object_var.floatParsFinal()
const_args_var = result_object_var.constPars()

mean_var = fit_args_var.find("mean")
scale_factor_var = fit_args_var.find("scale_factor")
Ds_mean_var = fit_args_var.find("Ds_mean")
x_bkg1_c1_var = fit_args_var.find("x_bkg1_c1")
x_bkg1_c2_var = fit_args_var.find("x_bkg1_c2")

sigmaL_var = const_args_var.find("sigmaL")
sigmaR_var = const_args_var.find("sigmaR")
alphaL_var = const_args_var.find("alphaL")
nL_var = const_args_var.find("nL")
alphaR_var = const_args_var.find("alphaR")
nR_var = const_args_var.find("nR")

Ds_sigmaL_var = const_args_var.find("Ds_sigmaL")
Ds_sigmaR_var = const_args_var.find("Ds_sigmaR")
Ds_alphaL_var = const_args_var.find("Ds_alphaL")
Ds_nL_var = const_args_var.find("Ds_nL")
Ds_alphaR_var = const_args_var.find("Ds_alphaR")
Ds_nR_var = const_args_var.find("Ds_nR")

sigma_gaussian_var = const_args_var.find("sigma_gaussian")
Ds_sigma_gaussian_var = const_args_var.find("Ds_sigma_gaussian")

mean_gaussian_var = const_args_var.find("mean_gaussian")
Ds_mean_gaussian_var = const_args_var.find("Ds_mean_gaussian")

scaled_sigma_gaussian_var = RooFormulaVar("scaled_sigma_gaussian_var","@0 * @1",RooArgList(sigma_gaussian_var, scale_factor_var))
scaled_Ds_sigma_gaussian_var = RooFormulaVar("Ds_scaled_sigma_gaussian_var","@0 * @1",RooArgList(Ds_sigma_gaussian_var, scale_factor_var))

# Create a category to distinguish between D+ and D-
cat = RooCategory("sample", "sample")
cat.defineType("D_plus")
cat.defineType("D_minus")

def nominal_fit_to_non_crossfeed(data_Dp, data_Dm, n_bootstrap):
  CB_var= ROOT.RooCrystalBall("CB_var", "CB_left", x, mean_var, sigmaL_var,sigmaR_var, alphaL_var, nL_var, alphaR_var, nR_var)
  gaussian_var = ROOT.RooGaussian("gaussian_var", "Gaussian PDF", x, mean_gaussian_var, scaled_sigma_gaussian_var)
  sig_model_var = ROOT.RooFFTConvPdf("sig_model_var", "Convolution of Johnson and Gaussian", x, CB_var, gaussian_var)

  Ds_CB_var= ROOT.RooCrystalBall("Ds_CB_var", "CB_left", x, Ds_mean_var, Ds_sigmaL_var, Ds_sigmaR_var, Ds_alphaL_var, Ds_nL_var, Ds_alphaR_var, Ds_nR_var)
  Ds_gaussian_var= ROOT.RooGaussian("Ds_gaussian_var", "Gaussian PDF", x, Ds_mean_gaussian_var, scaled_Ds_sigma_gaussian_var)
  Ds_model_var = ROOT.RooFFTConvPdf("Ds_model_var", "Convolution of Johnson and Gaussian", x, Ds_CB_var, Ds_gaussian_var)

  #model_bkg_var= ROOT.RooExponential("model_bkg_var", "x_bkg1", x, x_bkg1_tau_var)
  model_bkg_var = ROOT.RooPolynomial("model_bkg_var", "x_bkg1", x, ROOT.RooArgList(x_bkg1_c1_var, x_bkg1_c2_var))

  model_D_plus_var= ROOT.RooAddPdf("model_D_plus_var", "D+ model",
                                ROOT.RooArgList(sig_model_var, Ds_model_var, model_bkg_var),
                                ROOT.RooArgList(Nsig_D_plus_var, Nsig_Ds_plus_var, Nbkg_D_plus_var))
  model_D_minus_var= ROOT.RooAddPdf("model_D_minus_var", "D- model",
                                ROOT.RooArgList(sig_model_var, Ds_model_var, model_bkg_var),
                                ROOT.RooArgList(Nsig_D_minus_var, Nsig_Ds_minus_var, Nbkg_D_minus_var))
  sim_model_var = RooSimultaneous("sim_model_var", "Simultaneous model", cat)
  sim_model_var.addPdf(model_D_plus_var, "D_plus")
  sim_model_var.addPdf(model_D_minus_var, "D_minus")
  data_combined_var = RooDataSet("data_combined_var", "Combined", full_var_set, RooFit.Index(cat),
                                RooFit.Import("D_plus", data_Dp),
                                RooFit.Import("D_minus", data_Dm),
                                RooFit.WeightVar("w_scaled"))
  fit_result_var = sim_model_var.fitTo(data_combined_var, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(8), RooFit.Strategy(1), ROOT.RooFit.Offset(True), ROOT.RooFit.    Silence(True), ROOT.RooFit.PrintLevel(-1), ROOT.RooFit.Verbose(False))
  draw_save_result(data_combined_var, sim_model_var, file_name_Dall + f"_{n_bootstrap}.png",  fit_result_var, "model_bkg_var")
  # 1. Get MIGRAD status
  # 0 means success. Anything else (1, 4, etc.) indicates issues.
  status_migrad = fit_result_var.status()

  # 2. Get HESSE status (Covariance Matrix Quality)
  # 3 = Full, accurate covariance matrix (Success)
  # 2 = Full matrix, but forced positive-definite
  # 1 = Approximate matrix
  # 0 = Not calculated or failed
  status_hesse = fit_result_var.covQual()

  return Acp_var.getVal(), status_migrad, status_hesse, N_total_var.getVal(), N_total_Ds_var.getVal(), Acp_Ds_var.getVal()

def draw_save_result(data_combined, sim_model, file_name_Dall, fit_result, model_bkg_name):
  canvas_D_all = ROOT.TCanvas("canvas_D_all", "D+ fit", 800, 600)
  xlow = ctypes.c_double()
  ylow = ctypes.c_double()
  xup = ctypes.c_double()
  yup = ctypes.c_double()
  canvas_D_all.GetPad(0).GetPadPar(xlow, ylow, xup, yup)
  canvas_D_all.Divide(1,2)

  xlow = xlow.value
  ylow = ylow.value
  xup = xup.value
  yup = yup.value

  upPad = canvas_D_all.GetPad(1)
  upPad.SetPad(xlow, ylow+0.25*(yup-ylow),xup,yup)

  dwPad = canvas_D_all.GetPad(2)
  dwPad.SetPad(xlow, ylow,xup,ylow+0.25*(yup-ylow))

  canvas_D_all.cd(1)

  frame_D_all = x.frame(ROOT.RooFit.Title("D+ fit"))
  frame_D_all.GetXaxis().SetTitle("M(#eta_{3#pi}K^{+}) [GeV/c^{2}]")

  data_combined.plotOn(frame_D_all, Name="data")
  sim_model.plotOn(frame_D_all, Name="Background", Components=model_bkg_name, ProjWData=(cat, data_combined),LineColor=ROOT.kGreen+2, LineStyle=ROOT.kDashDotted)
  sim_model.plotOn(frame_D_all, Name="Fitting", ProjWData=(cat, data_combined))


  frame_D_all.Draw("PE")
  frame_D_all.GetXaxis().CenterTitle(True)

  leg1 = ROOT.TLegend(0.2, 0.65, 0.4, 0.90)
  leg1.SetFillColorAlpha(ROOT.kWhite, 0)
  leg1.AddEntry("data", "MC", "PE")
  leg1.AddEntry("Fitting", "Fit", "l")
  leg1.AddEntry("Background", "Bkg", "l")
  leg1.SetBorderSize(0)
  leg1.Draw()

  hpull = frame_D_all.pullHist()
  hpull.SetFillStyle(1001)
  hpull.SetFillColor(1);
  for i in range(0,hpull.GetN()):#(int i=0;i<hpull.GetN();++i):
      hpull.SetPointError(i,0.0,0.0,0.0,0.0)
  pullplot = x.frame()
  pullplot.SetTitle("")
  pullplot.addPlotable(hpull,"BE")
  pullplot.SetYTitle("Pull")
  pullplot.GetXaxis().SetTitleSize(0)
  pullplot.GetYaxis().SetTitleSize(0.22)
  pullplot.GetYaxis().CenterTitle(True)
  pullplot.GetYaxis().SetTitleOffset(0.2)
  pullplot.SetMinimum(-5.)
  pullplot.SetMaximum(5.)
  pullplot.GetXaxis().SetLabelSize(0.15)
  pullplot.GetYaxis().SetLabelSize(0.105)
  canvas_D_all.cd(2)
  pullplot.Draw()

  xmin1 = ctypes.c_double(fit_range[0])
  xmax1 = ctypes.c_double(fit_range[1])
  line = ROOT.TLine(xmin1,0.0,xmax1,0.0)
  line1 = ROOT.TLine(xmin1,3.0,xmax1,3.0)
  line2 = ROOT.TLine(xmin1,-3.0,xmax1,-3.0)

  line.SetLineColor(ROOT.kGray+1)
  line.SetLineWidth(3)
  line1.SetLineColor(ROOT.kBlack)
  line2.SetLineColor(ROOT.kGray+1)
  line1.SetLineStyle(2)
  line2.SetLineStyle(2)
  line.Draw("SAME")
  line1.Draw("SAME")
  line2.Draw("SAME")

  canvas_D_all.Update()
  #canvas_D_all.SaveAs(file_name_Dall)

n_bootstrap = 1000
results = {
    "acp_before": [],
    "acp_after": [],
    "delta_acp": [],
    "acp_Ds_before": [],
    "acp_Ds_after": [],
    "delta_Ds_acp": [],
    "NDp_before": [],
    "NDp_after": [],
    "delta_NDp": [],
    "relative_delta_NDp": [],
    "NDsp_before": [],
    "NDsp_after": [],
    "delta_NDsp": [],
    "relative_delta_NDsp": [],
    "status_migrad_before": [],
    "status_hesse_before": [],
    "status_migrad_after": [],
    "status_hesse_after": []
}

n_entries_Dp = int(data.numEntries()/4)
n_entries_Dm = int(data_cc.numEntries()/4)

success_count = 0
iteration = 0

is_crossfeed_cut_plus = "etapip_Eta_isSignal==1 && Pip_genMotherID==etapip_Eta_genMotherID && etapip_Eta_genMotherPDG==411 && Pip_mcPDG==211"
is_crossfeed_cut_minus = "etapip_Eta_isSignal==1 && Pip_genMotherID==etapip_Eta_genMotherID && etapip_Eta_genMotherPDG==-411 && Pip_mcPDG==-211"
no_crossfeed_cut_plus = "!(etapip_Eta_isSignal==1 && Pip_genMotherID==etapip_Eta_genMotherID && etapip_Eta_genMotherPDG==411 && Pip_mcPDG==211)"
no_crossfeed_cut_minus = "!(etapip_Eta_isSignal==1 && Pip_genMotherID==etapip_Eta_genMotherID && etapip_Eta_genMotherPDG==-411 && Pip_mcPDG==-211)"

n_cf_p = data.reduce(is_crossfeed_cut_plus).sumEntries()
n_cf_m = data_cc.reduce(is_crossfeed_cut_minus).sumEntries()

# Separate Poisson relative uncertainties
rel_unc_p = 1.0 / np.sqrt(n_cf_p) if n_cf_p > 0 else 1.0
rel_unc_m = 1.0 / np.sqrt(n_cf_m) if n_cf_m > 0 else 1.0
print(f"Poisson relative uncertainty for misID, plus charge: {rel_unc_p:.5%}")
print(f"Poisson relative uncertainty for misID, minus charge: {rel_unc_m:.5%}")

sys_multiplier_p = 1 + rel_unc_p
sys_multiplier_m = 1 + rel_unc_m

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

    weight_formula_plus = f"ds_weight * ({no_crossfeed_cut_plus} ? 1.0 : {sys_multiplier_p})"
    weight_formula_minus = f"ds_weight * ({no_crossfeed_cut_minus} ? 1.0 : {sys_multiplier_m})"
    w_sys_plus = ROOT.RooFormulaVar("w_sys_p", "Sys Weight", weight_formula_plus, full_var_set)
    w_sys_minus = ROOT.RooFormulaVar("w_sys_m", "Sys Weight", weight_formula_minus, full_var_set)

    data_boot_Dp.addColumn(w_sys_plus)
    data_boot_Dm.addColumn(w_sys_minus)
    data_sys_Dp = ROOT.RooDataSet("d_sys_p", "Weighted", data_boot_Dp, data_boot_Dp.get(), "", "w_sys_p")
    data_sys_Dm = ROOT.RooDataSet("d_sys_m", "Weighted", data_boot_Dm, data_boot_Dm.get(), "", "w_sys_m")


    fit_outputs_after = nominal_fit_to_non_crossfeed(data_sys_Dp, data_sys_Dm, iteration)

    sm_b = fit_outputs_before[1]
    sh_b = fit_outputs_before[2]
    sm_a = fit_outputs_after[1]
    sh_a = fit_outputs_after[2]

    # Check if both fits converged properly
    if sm_b == 0 and (sh_b == 3 or sh_b == 2) and sm_a == 0 and (sh_a == 3 or sh_b ==2):
        acp_before = fit_outputs_before[0]
        acp_after = fit_outputs_after[0]
        delta_acp = acp_after - acp_before
        acp_ds_before = fit_outputs_before[5]
        acp_ds_after = fit_outputs_after[5]
        delta_ds_acp = acp_ds_after - acp_ds_before

        ndp_before = fit_outputs_before[3]
        ndsp_before = fit_outputs_before[4]
        ndp_after = fit_outputs_after[3]
        ndsp_after = fit_outputs_after[4]

        delta_ndp = ndp_after - ndp_before
        delta_ndsp = ndsp_after - ndsp_before
        relative_delta_ndp = delta_ndp / ndp_before
        relative_delta_ndsp = delta_ndsp / ndsp_before

        results["acp_before"].append(acp_before)
        results["acp_after"].append(acp_after)
        results["delta_acp"].append(delta_acp)
        results["acp_Ds_before"].append(acp_ds_before)
        results["acp_Ds_after"].append(acp_ds_after)
        results["delta_Ds_acp"].append(delta_ds_acp)
        results["status_migrad_before"].append(sm_b)
        results["status_hesse_before"].append(sh_b)
        results["status_migrad_after"].append(sm_a)
        results["status_hesse_after"].append(sh_a)
        results["NDp_before"].append(ndp_before)
        results["NDsp_before"].append(ndsp_before)
        results["NDp_after"].append(ndp_after)
        results["NDsp_after"].append(ndsp_after)
        results["delta_NDp"].append(delta_ndp)
        results["delta_NDsp"].append(delta_ndsp)
        results["relative_delta_NDp"].append(relative_delta_ndp)
        results["relative_delta_NDsp"].append(relative_delta_ndsp)

        success_count += 1
        print(f"[{success_count}/{n_bootstrap}] successful bootstrap. ΔAcp = {delta_acp:.8f}")
    else:
        print(f"[{iteration}] Fit did not converge properly. Retrying... (sm_b={sm_b}, sh_b={sh_b}, sm_a={sm_a}, sh_a={sh_a})")

    del data_boot_Dp
    del data_boot_Dm
    gc.collect()

ak_array = ak.Array(results)
with uproot.recreate(f"bootstrap_acp_results_etapip_pipipi_K_{args.sign}_converge.root") as f:
    f["acp_bootstrap"] = ak_array

# Final results
delta_acp_array = np.array(results["delta_acp"])

mean_shift = np.mean(delta_acp_array)
rms_shift = np.std(delta_acp_array)

print(f"Bootstrap results:")
print(f"  Mean shift in ΔA_CP = {mean_shift:.8f}")
print(f"  RMS uncertainty     = {rms_shift:.8f}")

