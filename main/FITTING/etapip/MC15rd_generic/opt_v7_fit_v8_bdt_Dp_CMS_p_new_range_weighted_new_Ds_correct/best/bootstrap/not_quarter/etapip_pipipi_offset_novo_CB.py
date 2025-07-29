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

parser = argparse.ArgumentParser(description="Process Dp_CMS_sign argument")
parser.add_argument("-s","--sign", choices=["plus", "minus","all"], required=True,
                    help="Specify 'plus' or 'minus'")
parser.add_argument("-t","--train", required=True,
                    help="Specify train version")
#parser.add_argument("-b","--bdt", required=True,
#                    help="Specify BDT cut")

args = parser.parse_args()
print(f"Dp_CMS_sign is set to: {args.sign}")

#BDT_cut = args.bdt
BDT_cut = 0.74

def sample_param(mu, sigma):
  seed = int(time.time_ns())  # current time in nanoseconds
  rng = np.random.default_rng(seed)
  sample_value = rng.normal(mu, sigma)
  return sample_value

if args.sign == "plus":
	Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>0"
	N_scale = 0.6
elif args.sign == "minus":
	Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta<0"
	N_scale = 0.4
elif args.sign == "all":
	Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>-10"
	N_scale = 1

suffix = "new_Ds_correct_only_success"
file_name_Dall = f"/share/storage/jykim/plots/MC15rd/etapip/pipipi/generic/bootstrap_sys_MC15rd_etapip_pipipi_loose_v7_fitv8_bdt_{args.train}_{args.sign}_{BDT_cut}_{suffix}_weighted_Dall"
fitresult_name = f"/share/storage/jykim/plots/MC15rd/etapip/pipipi/generic/fitresult/bootstrap_sys_MC15rd_etapip_pipipi_loose_v7_fitv8_bdt_{args.train}_{args.sign}_{BDT_cut}_{suffix}_weighted.root"
fitresult_text = f"/share/storage/jykim/plots/MC15rd/etapip/pipipi/generic/fitresult/bootstrap_sys_MC15rd_etapip_pipipi_loose_v7_fitv8_bdt_{args.train}_{args.sign}_{BDT_cut}_{suffix}_weighted.txt"
dir_path = os.path.dirname(file_name_Dall)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)
dir_path = os.path.dirname(fitresult_name)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/etapip_eteeta/MC15rd_etaetapip_loose_v7_250122_skimhad_if_true_Dp_CMS_p_v3"
cm_elements = ["15rd_eta_e7_18_4S_v3", "15rd_eta_e20_b26_v1", "15rd_eta_e20_e26_4S_v2", "15rd_eta_e21_5S_scan_v1", "15rd_eta_mori_off_v1"]

tree_name = "etapip_pipipi"
file_list = []
for element in cm_elements:
    pattern = f"{base_path}/{element}/{tree_name}/min_unc_search/{BDT_cut}/weighted/*.BCS.root"
    file_list += glob.glob(pattern)

print(file_list)
mychain = ROOT.TChain(tree_name)
for i in file_list:
    mychain.Add(i)
print(file_list)
print(f"Numer of files: {len(file_list)}")

fit_variable = "Dp_M"
fit_var_name = "M(#eta_{#pi#pi#pi}#pi^{+}) [GeV/c^{2}]"
fit_range = (1.71, 2.06)
truth_var = "Dp_isSignal"
charge_var = "Pip_charge"

cuts_Dp = charge_var + "==1"
cuts_Dm = charge_var + "==-1"

cuts_Dp += " && " + Dp_CMS_cosTheta_cut
cuts_Dm += " && " + Dp_CMS_cosTheta_cut

x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
x.setBins(200)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)
Dp_CMS_cosTheta = ROOT.RooRealVar("Dp_CMS_cosTheta", "Dp_CMS_cosTheta", -1, 1)
BDT = ROOT.RooRealVar("BDT", "BDT", 0, 1)
Pip_dr = ROOT.RooRealVar("Pip_dr", "Pip_dr", -10000, 10000)
Dp_dz = ROOT.RooRealVar("Dp_dz", "Dp_dz", -10000, 10000)
Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane = ROOT.RooRealVar("Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane", "Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane'", -1,1)
Dp_cosHelicityAngleMomentum = ROOT.RooRealVar("Dp_cosHelicityAngleMomentum", "Dp_cosHelicityAngleMomentum", -1, 1)
Dp_CMS_p = ROOT.RooRealVar("Dp_CMS_p", "Dp_CMS_p", 0, 100)
ds_weight = ROOT.RooRealVar("ds_weight", "ds_weight", -1000, 1000)

full_var_set = ROOT.RooArgSet(x, Pip_charge, Dp_CMS_cosTheta, BDT, Pip_dr, Dp_dz,
                              Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane,
                              Dp_cosHelicityAngleMomentum,
                              Dp_CMS_p, ds_weight)


before_data = ROOT.RooDataSet("data", "", mychain, full_var_set, cuts_Dp)

w_1 = ROOT.RooRealVar('w_1', 'w', 0,1)
scale = 1
weight_scale = 1
w_scaled = ROOT.RooFormulaVar("w_scaled", "Scaled Weight", f"{weight_scale}*ds_weight", ROOT.RooArgList(ds_weight))
before_data.addColumn(w_scaled)

data = ROOT.RooDataSet("data_weighted", "Weighted Data", before_data, before_data.get(), "", "w_scaled")

Num_total = data.sumEntries()
print(Num_total)

mychain_cc = ROOT.TChain(tree_name)
for i in file_list:
    mychain_cc.Add(i)
before_data_cc = ROOT.RooDataSet("data", "", mychain_cc, full_var_set, cuts_Dm)
before_data_cc.addColumn(w_scaled)
data_cc = ROOT.RooDataSet("data_weighted_cc", "Weighted Data", before_data_cc, before_data_cc.get(), "", "w_scaled")

Num_total_cc = data_cc.sumEntries()
print(Num_total_cc)

N_total = RooRealVar("N_total", "N_total (N_D+ + N_D-)", 60000*scale*N_scale,  30000*scale*N_scale, 400000*scale*N_scale)  # N_total = N_D+ + N_D-
Acp = RooRealVar("Acp", "Acp", 0, -0.2, 0.2)  # A_Cp as a fit parameter
Nsig_D_plus = RooFormulaVar("Nsig_D_plus",
    "0.5 * N_total * (1 + Acp)",
    RooArgList(N_total, Acp))

Nsig_D_minus = RooFormulaVar("Nsig_D_minus",
    "0.5 * N_total * (1 - Acp)",
    RooArgList(N_total, Acp))
N_total_Ds = RooRealVar("N_total_Ds", "N_total (N_Ds+ + N_Ds-)", 140000*scale*N_scale,  50000*scale*N_scale,800000*scale*N_scale)  # N_total = N_D+ + N_D-
Acp_Ds = RooRealVar("Acp_Ds", "Acp", 0, -0.2, 0.2)  # A_Cp as a fit parameter
Nsig_Ds_plus = RooFormulaVar("Nsig_Ds_plus",
    "0.5 * N_total_Ds * (1 + Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))

Nsig_Ds_minus = RooFormulaVar("Nsig_Ds_minus",
    "0.5 * N_total_Ds * (1 - Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))


Nbkg_total = ROOT.RooRealVar("Nbkg_total", "Number of background events for D+", 250000*scale*N_scale, 20000*scale*N_scale,500000*scale*N_scale)
Acp_bkg = RooRealVar("Acp_bkg", "Acp", 0, -0.2, 0.2)  # A_Cp as a fit parameter
Nbkg_D_plus = RooFormulaVar("Nbkg_D_plus",
    "0.5 * Nbkg_total * (1 + Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))

Nbkg_D_minus = RooFormulaVar("Nbkg_D_minus",
    "0.5 * Nbkg_total * (1 - Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))

'''
mean = ROOT.RooRealVar("mean", "mean", 1.87, 1.85, 1.89)
sigmaL = ROOT.RooRealVar("sigmaL", "sigmaL",  0.001670860951426787)
sigmaR = ROOT.RooRealVar("sigmaR", "sigmaR",  0.0022450770284542)
alphaL = ROOT.RooRealVar("alphaL", "alphaL", 0.8288815720543256)
nL = ROOT.RooRealVar("nL", "nL",  2.18098210570152)
alphaR = ROOT.RooRealVar("alphaR", "alphaR", 1.3998884053196745)
nR = ROOT.RooRealVar("nR", "nR", 1.8306892867243558)

CB = ROOT.RooCrystalBall("CB", "CB_left", x, mean, sigmaL,sigmaR, alphaL, nL, alphaR, nR)
mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0)
sigma_gaussian = ROOT.RooRealVar("sigma_gaussian", "sigma of Gaussian", 0.006, 0.001, 0.1)
gaussian = ROOT.RooGaussian("gaussian", "Gaussian PDF", x, mean_gaussian, sigma_gaussian)

sig_model = ROOT.RooFFTConvPdf("sig_model", "Convolution of Johnson and Gaussian", x, CB, gaussian)

Ds_mean = ROOT.RooRealVar("Ds_mean", "mean", 1.97, 1.95, 1.99)
Ds_sigmaL = ROOT.RooRealVar("Ds_sigmaL", "sigma", 0.0023699101004389296)
Ds_sigmaR = ROOT.RooRealVar("Ds_sigmaR", "sigma",  0.0011845650920208712)
Ds_alphaL = ROOT.RooRealVar("Ds_alphaL", "alphaL", 0.9688944011584982)
Ds_nL = ROOT.RooRealVar("Ds_nL", "nL", 2.5040009972282373)
Ds_alphaR = ROOT.RooRealVar("Ds_alphaR", "alphaR", 0.8093768388483458)
Ds_nR = ROOT.RooRealVar("Ds_nR", "nR", 2.191528655057291)

Ds_CB = ROOT.RooCrystalBall("Ds_CB", "CB_left", x, Ds_mean, Ds_sigmaL, Ds_sigmaR, Ds_alphaL, Ds_nL, Ds_alphaR, Ds_nR)
Ds_mean_gaussian = ROOT.RooRealVar("Ds_mean_gaussian", "mean of Gaussian", 0)
Ds_sigma_gaussian = ROOT.RooRealVar("Ds_sigma_gaussian", "sigma of Gaussian", 0.006, 0.001, 0.1)

Ds_gaussian = ROOT.RooGaussian("Ds_gaussian", "Gaussian PDF", x, Ds_mean_gaussian, Ds_sigma_gaussian)
Ds_model = ROOT.RooFFTConvPdf("Ds_model", "Convolution of Johnson and Gaussian", x, Ds_CB, Ds_gaussian)

x_bkg1_Cheby_c0 = ROOT.RooRealVar("x_bkg1_Cheby_c0", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c1 = ROOT.RooRealVar("x_bkg1_Cheby_c1", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c2 = ROOT.RooRealVar("x_bkg1_Cheby_c2", "c0",0.0, -1.0, 1.0)
#x_bkg1_tau = ROOT.RooRealVar("x_bkg1_tau", "c0",-3, -8, -0.001)
x_bkg1_tau = ROOT.RooRealVar("x_bkg1_tau", "c0",-5, -8, -0.1)

novo_mean = ROOT.RooRealVar("novo_mean", "Mean",  1.73, 1.71,1.745)
novo_sigma = ROOT.RooRealVar("novo_sigma", "Sigma", 0.05550506651984597)
novo_tail = ROOT.RooRealVar("novo_tail", "Tail", 0.26384751697571546 )
rhopeta  = ROOT.RooNovosibirsk("rhopeta", "Novosibirsk PDF", x, novo_mean, novo_sigma, novo_tail)

bkg_comb = ROOT.RooExponential("bkg_comb", "x_bkg1", x, x_bkg1_tau)

bkg_frac = ROOT.RooRealVar("bkg_frac", "fraction of Gaussian in BKG", 0.3, 0.01, 1)

model_bkg = ROOT.RooAddPdf("model_bkg", "Gaus + Exp", RooArgList(rhopeta, bkg_comb), bkg_frac)
'''
f = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/etapip/pipipi/generic/fitresult/MC15rd_etapip_pipipi_fit_opt_loose_v7_fitv8_bdt_train_Dp_CMS_p_{args.sign}_0.74_new_Ds_correct_weighted.root")
result_object = ROOT.gDirectory.Get("jykim")
f.Close()
#result_object.Print("v")
fit_args = result_object.floatParsFinal()
const_args = result_object.constPars()

mean = fit_args.find("mean")
Ds_mean = fit_args.find("Ds_mean")
x_bkg1_tau = fit_args.find("x_bkg1_tau")
novo_mean = fit_args.find("novo_mean")
bkg_frac = fit_args.find("bkg_frac")

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

novo_sigma = const_args.find("novo_sigma")
novo_tail = const_args.find("novo_tail")

sigma_gaussian = fit_args.find("sigma_gaussian")
Ds_sigma_gaussian = fit_args.find("Ds_sigma_gaussian")

mean_gaussian = const_args.find("mean_gaussian")
Ds_mean_gaussian = const_args.find("Ds_mean_gaussian")

def nominal_fit_extract_Acp(data_Dp, data_Dm):
  CB = ROOT.RooCrystalBall("CB", "CB_left", x, mean, sigmaL,sigmaR, alphaL, nL, alphaR, nR)
  gaussian = ROOT.RooGaussian("gaussian", "Gaussian PDF", x, mean_gaussian, sigma_gaussian)
  sig_model = ROOT.RooFFTConvPdf("sig_model", "Convolution of Johnson and Gaussian", x, CB, gaussian)

  Ds_CB = ROOT.RooCrystalBall("Ds_CB", "CB_left", x, Ds_mean, Ds_sigmaL, Ds_sigmaR, Ds_alphaL, Ds_nL, Ds_alphaR, Ds_nR)
  Ds_gaussian = ROOT.RooGaussian("Ds_gaussian", "Gaussian PDF", x, Ds_mean_gaussian, Ds_sigma_gaussian)
  Ds_model = ROOT.RooFFTConvPdf("Ds_model", "Convolution of Johnson and Gaussian", x, Ds_CB, Ds_gaussian)

  rhopeta  = ROOT.RooNovosibirsk("rhopeta", "Novosibirsk PDF", x, novo_mean, novo_sigma, novo_tail)
  bkg_comb = ROOT.RooExponential("bkg_comb", "x_bkg1", x, x_bkg1_tau)
  model_bkg = ROOT.RooAddPdf("model_bkg", "Gaus + Exp", RooArgList(rhopeta, bkg_comb), bkg_frac)

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
  nll = sim_model.createNLL(data_combined, RooFit.Extended(True), ROOT.RooFit.NumCPU(1),   ROOT.RooFit.Offset("initial"))
  minimizer = ROOT.RooMinimizer(nll)
  minimizer.setStrategy(2)
  minimizer.setPrintLevel(-1)
  status_migrad = minimizer.migrad()
  if status_migrad != 0:
    print(f"Migrad failed with status: {status_migrad}")
  status_hesse = minimizer.hesse()
  if status_hesse != 0:
     print(f"Hesse failed with status: {status_hesse}")
  return Acp.getVal(), status_migrad, status_hesse, N_total.getVal(), N_total_Ds.getVal(), Acp_Ds.getVal()


N_total_var = RooRealVar("N_total_var", "N_total (N_D+ + N_D-)",  60000*scale*N_scale,  30000*scale*N_scale, 400000*scale*N_scale)  # N_total = N_D+ + N_D-
Acp_var = RooRealVar("Acp_var", "Acp", 0, -0.2, 0.2)  # A_Cp as a fit parameter

Nsig_D_plus_var = RooFormulaVar("Nsig_D_plus_var",
    "0.5 * N_total_var * (1 + Acp_var)",
    RooArgList(N_total_var, Acp_var))

Nsig_D_minus_var = RooFormulaVar("Nsig_D_minus_var",
    "0.5 * N_total_var * (1 - Acp_var)",
    RooArgList(N_total_var, Acp_var))

N_total_Ds_var = RooRealVar("N_total_Ds_var", "N_total (N_Ds+ + N_Ds-)", 140000*scale*N_scale,  50000*scale*N_scale,800000*scale*N_scale)  # N_total = N_D+ + N_D-
Acp_Ds_var = RooRealVar("Acp_Ds_var", "Acp", 0, -0.2, 0.2)  # A_Cp as a fit parameter

Nsig_Ds_plus_var = RooFormulaVar("Nsig_Ds_plus_var",
    "0.5 * N_total_Ds_var * (1 + Acp_Ds_var)",
    RooArgList(N_total_Ds_var, Acp_Ds_var))

Nsig_Ds_minus_var = RooFormulaVar("Nsig_Ds_minus_var",
    "0.5 * N_total_Ds_var * (1 - Acp_Ds_var)",
    RooArgList(N_total_Ds_var, Acp_Ds_var))


Nbkg_total_var = ROOT.RooRealVar("Nbkg_total_var", "Number of background events for D+", 250000*scale*N_scale, 20000*scale*N_scale,500000*scale*N_scale)
Acp_bkg_var= RooRealVar("Acp_bkg_var", "Acp", 0, -0.2, 0.2)  # A_Cp as a fit parameter
Nbkg_D_plus_var = RooFormulaVar("Nbkg_D_plus_var",
    "0.5 * Nbkg_total_var * (1 + Acp_bkg_var)",
    RooArgList(Nbkg_total_var, Acp_bkg_var))

Nbkg_D_minus_var = RooFormulaVar("Nbkg_D_minus_var",
    "0.5 * Nbkg_total_var * (1 - Acp_bkg_var)",
    RooArgList(Nbkg_total_var, Acp_bkg_var))


mean_var = ROOT.RooRealVar("mean_var", "mean_var", 1.87, 1.85, 1.89)
Ds_mean_var = ROOT.RooRealVar("Ds_mean_var", "mean", 1.97, 1.95, 1.99)
x_bkg1_tau_var = ROOT.RooRealVar("x_bkg1_tau_var", "c0",-5, -8, -0.1)
novo_mean_var = ROOT.RooRealVar("novo_mean_var", "novo_mean",1.73, 1.71,1.745)
bkg_frac_var = ROOT.RooRealVar("bkg_frac_var", "bkg_frac",0.3, 0.01, 1)
sigma_gaussian_var = ROOT.RooRealVar("sigma_gaussian_var", "sigma of Gaussian", 0.006, 0.001, 0.1)
Ds_sigma_gaussian_var = ROOT.RooRealVar("Ds_sigma_gaussian_var", "sigma of Gaussian", 0.006, 0.001, 0.1)

f_sig = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/etapip/pipipi/MC15rd_6M_etapip_pipipi_Dp_M_opt_v7_CB_conv_result_extended_train_Dp_CMS_p.0.74_new_Ds_correct.root")
result_object_sig = ROOT.gDirectory.Get("jykim")
f_sig.Close()
#result_object_sig.Print("v")
fit_args_sig = result_object_sig.floatParsFinal()
#const_args_sig = result_object_sig.constPars()

f_sig_Ds = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/etapip/pipipi/MC15rd_6M_etapip_pipipi_Dp_M_opt_v7_CB_conv_result_extended_train_Dp_CMS_p_Ds_p.0.74.weighted.new_Ds_correct.root")
result_object_sig_Ds = ROOT.gDirectory.Get("jykim")
f_sig_Ds.Close()
#result_object_sig_Ds.Print("v")
fit_args_sig_Ds = result_object_sig_Ds.floatParsFinal()

f_rhopeta = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/etapip/pipipi/MC15rd_etapip_pipipi_Dp_M_opt_v7_novo_result_rhopeta_Dp_CMS_p_0.74_new_Ds_correct.root")
result_object_rhopeta = ROOT.gDirectory.Get("jykim")
f_rhopeta.Close()
fit_args_rhopeta = result_object_rhopeta.floatParsFinal()

fit_sigmaL = fit_args_sig.find("sigmaL")
fit_sigmaR = fit_args_sig.find("sigmaR")
fit_alphaL = fit_args_sig.find("alphaL")
fit_nL = fit_args_sig.find("nL")
fit_alphaR = fit_args_sig.find("alphaR")
fit_nR = fit_args_sig.find("nR")

fit_Ds_sigmaL = fit_args_sig_Ds.find("sigmaL")
fit_Ds_sigmaR = fit_args_sig_Ds.find("sigmaR")
fit_Ds_alphaL = fit_args_sig_Ds.find("alphaL")
fit_Ds_nL = fit_args_sig_Ds.find("nL")
fit_Ds_alphaR = fit_args_sig_Ds.find("alphaR")
fit_Ds_nR = fit_args_sig_Ds.find("nR")

fit_rhopeta_novo_sigma = fit_args_rhopeta.find("sigma")
fit_rhopeta_novo_tail = fit_args_rhopeta.find("tail")

def var_fit_extract_Acp(data_Dp, data_Dm, n_bootstrap):
  sigmaL_var= ROOT.RooRealVar("sigmaL_var", "sigmaL_var", sample_param( fit_sigmaL.getVal(), fit_sigmaL.getError()))
  sigmaR_var= ROOT.RooRealVar("sigmaR_var", "sigmaR_var", sample_param( fit_sigmaR.getVal(), fit_sigmaR.getError()))
  alphaL_var= ROOT.RooRealVar("alphaL_var", "alphaL_var", sample_param( fit_alphaL.getVal(), fit_alphaL.getError()))
  nL_var = ROOT.RooRealVar("nL_var", "nL_var", sample_param( fit_nL.getVal(), fit_nL.getError()))
  alphaR_var = ROOT.RooRealVar("alphaR_var", "alphaR_var", sample_param( fit_alphaR.getVal(), fit_alphaR.getError()))
  nR_var = ROOT.RooRealVar("nR_var", "nR_var", sample_param( fit_nR.getVal(),fit_nR.getError()))

  Ds_sigmaL_var = ROOT.RooRealVar("Ds_sigmaL_var", "sigma_var", sample_param( fit_Ds_sigmaL.getVal(), fit_Ds_sigmaL.getError()))
  Ds_sigmaR_var = ROOT.RooRealVar("Ds_sigmaR_var", "sigma_var",  sample_param( fit_Ds_sigmaR.getVal(),fit_Ds_sigmaR.getError()))
  Ds_alphaL_var = ROOT.RooRealVar("Ds_alphaL_var", "alphaL_var", sample_param( fit_Ds_alphaL.getVal(),fit_Ds_alphaL.getError()))
  Ds_nL_var = ROOT.RooRealVar("Ds_nL_var", "nL_var", sample_param( fit_Ds_nL.getVal(),fit_Ds_nL.getError()))
  Ds_alphaR_var = ROOT.RooRealVar("Ds_alphaR_var", "alphaR_var", sample_param( fit_Ds_alphaR.getVal(), fit_Ds_alphaR.getError()))
  Ds_nR_var = ROOT.RooRealVar("Ds_nR_var", "nR_var",  sample_param( fit_Ds_nR.getVal(),fit_Ds_nR.getError()))

  novo_sigma_var = ROOT.RooRealVar("novo_sigma_var", "novo_sigma_var",  sample_param( fit_rhopeta_novo_sigma.getVal(),fit_rhopeta_novo_sigma.getError()))
  novo_tail_var = ROOT.RooRealVar("novo_tail_var", "novo_tail_var",  sample_param( fit_rhopeta_novo_tail.getVal(),fit_rhopeta_novo_tail.getError()))

  mean_gaussian_var = ROOT.RooRealVar("mean_gaussian_var", "mean of Gaussian", 0)
  Ds_mean_gaussian_var = ROOT.RooRealVar("Ds_mean_gaussian_var", "mean of Gaussian", 0)

  CB_var= ROOT.RooCrystalBall("CB_var", "CB_left", x, mean_var, sigmaL_var,sigmaR_var, alphaL_var, nL_var, alphaR_var, nR_var)
  gaussian_var = ROOT.RooGaussian("gaussian_var", "Gaussian PDF", x, mean_gaussian_var, sigma_gaussian_var)
  sig_model_var = ROOT.RooFFTConvPdf("sig_model_var", "Convolution of Johnson and Gaussian", x, CB_var, gaussian_var)

  Ds_CB_var= ROOT.RooCrystalBall("Ds_CB_var", "CB_left", x, Ds_mean_var, Ds_sigmaL_var, Ds_sigmaR_var, Ds_alphaL_var, Ds_nL_var, Ds_alphaR_var, Ds_nR_var)
  Ds_gaussian_var= ROOT.RooGaussian("Ds_gaussian_var", "Gaussian PDF", x, Ds_mean_gaussian_var, Ds_sigma_gaussian_var)
  Ds_model_var = ROOT.RooFFTConvPdf("Ds_model_var", "Convolution of Johnson and Gaussian", x, Ds_CB_var, Ds_gaussian_var)

  rhopeta_var = ROOT.RooNovosibirsk("rhopeta_var", "Novosibirsk PDF", x, novo_mean_var, novo_sigma_var, novo_tail_var)
  bkg_comb_var = ROOT.RooExponential("bkg_comb_var", "x_bkg1", x, x_bkg1_tau_var)
  model_bkg_var = ROOT.RooAddPdf("model_bkg_var", "Gaus + Exp", RooArgList(rhopeta_var, bkg_comb_var), bkg_frac_var)

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
  nll = sim_model_var.createNLL(data_combined_var, RooFit.Extended(True), ROOT.RooFit.NumCPU(1),   ROOT.RooFit.Offset("initial"))
  minimizer = ROOT.RooMinimizer(nll)
  minimizer.setStrategy(2)
  minimizer.setPrintLevel(-1)
  status_migrad = minimizer.migrad()
  if status_migrad != 0:
    print(f"Migrad failed with status: {status_migrad}")
  status_hesse = minimizer.hesse()
  if status_hesse != 0:
     print(f"Hesse failed with status: {status_hesse}")
  fit_result  = minimizer.save()
  draw_save_result(data_combined_var, sim_model_var, file_name_Dall + f"_{n_bootstrap}.png", fitresult_name, fitresult_text, fit_result, "model_bkg_var")

  return Acp_var.getVal(), status_migrad, status_hesse, N_total_var.getVal(), N_total_Ds_var.getVal(), Acp_Ds_var.getVal()


# Create a category to distinguish between D+ and D-
cat = RooCategory("sample", "sample")
cat.defineType("D_plus")
cat.defineType("D_minus")


def draw_save_result(data_combined, sim_model, file_name_Dall, fitresult_name, fitresult_text, fit_result, model_bkg_name):
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
  frame_D_all.GetXaxis().SetTitle("M(#eta_{#pi#pi#pi}#pi^{+}) [GeV/c^{2}]")

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
  canvas_D_all.SaveAs(file_name_Dall)


  f = ROOT.TFile(fitresult_name, "RECREATE")
  fit_result.Write("jykim")
  f.Close()
  with open(fitresult_text, "w") as f:
      f.write("Full fit result summary:\n")
      #fit_result.Print("v")  # Verbose print (prints more details)

      f.write("\nSpecific fit result details:\n")
      f.write(f"Status: {fit_result.status()}\n")
      f.write(f"Covariance quality: {fit_result.covQual()}\n")
      f.write(f"EDM (Estimated Distance to Minimum): {fit_result.edm()}\n")
      f.write(f"Min NLL: {fit_result.minNll()}\n")

      f.write("\nFitted Parameters:\n")
      params = fit_result.floatParsFinal()  # This returns the final fitted parameters
      for i in range(params.getSize()):
          param = params[i]
          f.write(f"{param.GetName()} = {param.getVal()} ± {param.getError()}\n")

      N_total_val = N_total.getVal()
      N_total_err = N_total.getError()
      Acp_val = Acp.getVal()
      Acp_err = Acp.getError()
      Nsig_D_plus_val = 0.5 * N_total_val * (1 + Acp_val)
      Nsig_D_plus_err = 0.5 * ((1 + Acp_val) * N_total_err + N_total_val * Acp_err)
      Nsig_D_minus_val = 0.5 * N_total_val * (1 - Acp_val)
      Nsig_D_minus_err = 0.5 * ((1 - Acp_val) * N_total_err + N_total_val * Acp_err)
      N_total_Ds_val = N_total_Ds.getVal()
      N_total_Ds_err = N_total_Ds.getError()
      Acp_Ds_val = Acp_Ds.getVal()
      Acp_Ds_err = Acp_Ds.getError()
      Nsig_Ds_plus_val = 0.5 * N_total_Ds_val * (1 + Acp_Ds_val)
      Nsig_Ds_plus_err = 0.5 * ((1 + Acp_Ds_val) * N_total_Ds_err + N_total_Ds_val * Acp_Ds_err)
      Nsig_Ds_minus_val = 0.5 * N_total_Ds_val * (1 - Acp_Ds_val)
      Nsig_Ds_minus_err = 0.5 * ((1 - Acp_Ds_val) * N_total_Ds_err + N_total_Ds_val * Acp_Ds_err)

      f.write(f"Nsig_D_plus: Value = {Nsig_D_plus_val}, Error = {Nsig_D_plus_err}\n")
      f.write(f"Nsig_D_minus: Value = {Nsig_D_minus_val}, Error = {Nsig_D_minus_err}\n")
      f.write(f"Nsig_Ds_plus: Value = {Nsig_Ds_plus_val}, Error = {Nsig_Ds_plus_err}\n")
      f.write(f"Nsig_Ds_minus: Value = {Nsig_Ds_minus_val}, Error = {Nsig_Ds_minus_err}\n")
      f.write("\nFit result saved successfully.\n")


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

n_entries_Dp = int(data.numEntries() )
n_entries_Dm = int(data_cc.numEntries() )

success_count = 0
iteration = 0

while success_count < n_bootstrap:
    iteration += 1
    data_boot_Dp = data.emptyClone()
    data_boot_Dm = data_cc.emptyClone()

    for _ in range(n_entries_Dp):
        idx = random.randint(0, n_entries_Dp - 1)
        data_boot_Dp.add(data.get(idx), data.weight())

    for _ in range(n_entries_Dm):
        idx = random.randint(0, n_entries_Dm - 1)
        data_boot_Dm.add(data_cc.get(idx), data_cc.weight())

    fit_outputs_after = nominal_fit_extract_Acp(data_boot_Dp, data_boot_Dm)
    fit_outputs_before = var_fit_extract_Acp(data_boot_Dp, data_boot_Dm, iteration)

    sm_b = fit_outputs_before[1]
    sh_b = fit_outputs_before[2]
    sm_a = fit_outputs_after[1]
    sh_a = fit_outputs_after[2]

    # Check if both fits converged properly
    if sm_b == 0 and sh_b == 0 and sm_a == 0 and sh_a == 0:
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
with uproot.recreate(f"bootstrap_acp_results_etapip_pipipi_{args.sign}_converge_not_quarter.root") as f:
    f["acp_bootstrap"] = ak_array

# Final results
delta_acp_array = np.array(results["delta_acp"])

mean_shift = np.mean(delta_acp_array)
rms_shift = np.std(delta_acp_array)

print(f"Bootstrap results:")
print(f"  Mean shift in ΔA_CP = {mean_shift:.8f}")
print(f"  RMS uncertainty     = {rms_shift:.8f}")
