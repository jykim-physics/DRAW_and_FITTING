import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory
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

suffix = "KDE_trialv2"
file_name_Dall = f"/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/boostrap/bootstrap_sys_MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv12_bdt_{args.train}_Dall_CMS_{args.sign}_{BDT_cut}_{suffix}_weighted_Dall"
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

full_var_set = ROOT.RooArgSet(x, Pip_charge, Dp_CMS_cosTheta, BDT, Pip_dr, Dp_dz,
                              Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane,
                              Dp_cosHelicityAngleMomentum,
                              Dp_CMS_p,rank_Dp_chiProb,ds_weight)

before_data = ROOT.RooDataSet("before_data","Data before weighting",full_var_set,ROOT.RooFit.Import(mychain),ROOT.RooFit.Cut(cuts_Dp))
scale = 1
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


f = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv12_bdt_train_Dp_CMS_p_{args.sign}_0.77_KDE_weighted.root")
result_object = ROOT.gDirectory.Get("jykim")
f.Close()
#result_object.Print("v")
fit_args = result_object.floatParsFinal()
const_args = result_object.constPars()
N_total = fit_args.find("N_total")
Acp = fit_args.find("Acp")
Nsig_D_plus = RooFormulaVar("Nsig_D_plus",
    "0.5 * N_total * (1 + Acp)",
    RooArgList(N_total, Acp))
Nsig_D_minus = RooFormulaVar("Nsig_D_minus",
    "0.5 * N_total * (1 - Acp)",
    RooArgList(N_total, Acp))
N_total_Ds = fit_args.find("N_total_Ds")
Acp_Ds = fit_args.find("Acp_Ds")
Nsig_Ds_plus = RooFormulaVar("Nsig_Ds_plus",
    "0.5 * N_total_Ds * (1 + Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))
Nsig_Ds_minus = RooFormulaVar("Nsig_Ds_minus",
    "0.5 * N_total_Ds * (1 - Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))
Nbkg_total = fit_args.find("Nbkg_total")
Acp_bkg = fit_args.find("Acp_bkg")
Nbkg_D_plus = RooFormulaVar("Nbkg_D_plus",
    "0.5 * Nbkg_total * (1 + Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))
Nbkg_D_minus = RooFormulaVar("Nbkg_D_minus",
    "0.5 * Nbkg_total * (1 - Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))

N_peak_bkg_total = const_args.find("N_peak_bkg_total")
Acp_peak_bkg = fit_args.find("Acp_peak_bkg")
N_peak_bkg_D_plus = RooFormulaVar("N_peak_bkg_D_plus",
    "0.5 * N_peak_bkg_total * (1 + Acp_peak_bkg)",
    RooArgList(N_peak_bkg_total, Acp_peak_bkg))

N_peak_bkg_D_minus = RooFormulaVar("N_peak_bkg_D_minus",
    "0.5 * N_peak_bkg_total * (1 - Acp_peak_bkg)",
    RooArgList(N_peak_bkg_total, Acp_peak_bkg))
print("N_peak_bkg_total =", N_peak_bkg_total.getVal())
print("Acp_peak_bkg =", Acp_peak_bkg.getVal())

f_in = ROOT.TFile("/share/storage/jykim/plots/MC15rd/etaKp/pipipi/MC15re_6M_etapip_pipipi_Dp_M_v12_result_true_extended_train_Dp_CMS_p.0.77_workspace.root", "READ")
ws = f_in.Get("ws_kde")
kde_model = ws.pdf("model")
kde_model.SetName("kde_model")

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

CB = ROOT.RooCrystalBall("CB", "CB_left", x, mean, sigmaL,sigmaR, alphaL, nL, alphaR, nR)
gaussian = ROOT.RooGaussian("gaussian", "Gaussian PDF", x, mean_gaussian, scaled_sigma_gaussian)
sig_model = ROOT.RooFFTConvPdf("sig_model", "Convolution of Johnson and Gaussian", x, CB, gaussian)

Ds_CB = ROOT.RooCrystalBall("Ds_CB", "CB_left", x, Ds_mean, Ds_sigmaL, Ds_sigmaR, Ds_alphaL, Ds_nL, Ds_alphaR, Ds_nR)
Ds_gaussian = ROOT.RooGaussian("Ds_gaussian", "Gaussian PDF", x, Ds_mean_gaussian, scaled_Ds_sigma_gaussian)
Ds_model = ROOT.RooFFTConvPdf("Ds_model", "Convolution of Johnson and Gaussian", x, Ds_CB, Ds_gaussian)

model_bkg = ROOT.RooPolynomial("model_bkg", "x_bkg1", x, ROOT.RooArgList(x_bkg1_c1, x_bkg1_c2))


model_D_plus = ROOT.RooAddPdf("model_D_plus", "D+ model",
                              ROOT.RooArgList(sig_model, Ds_model, model_bkg, kde_model),
                              ROOT.RooArgList(Nsig_D_plus, Nsig_Ds_plus, Nbkg_D_plus, N_peak_bkg_D_plus))
model_D_minus = ROOT.RooAddPdf("model_D_minus", "D- model",
                              ROOT.RooArgList(sig_model, Ds_model, model_bkg, kde_model),
                              ROOT.RooArgList(Nsig_D_minus, Nsig_Ds_minus, Nbkg_D_minus, N_peak_bkg_D_minus))
# Create a category to distinguish between D+ and D-
cat = RooCategory("sample", "sample")
cat.defineType("D_plus")
cat.defineType("D_minus")
# Create a simultaneous PDF using the category
sim_model = RooSimultaneous("sim_model", "Simultaneous model", cat)
sim_model.addPdf(model_D_plus, "D_plus")
sim_model.addPdf(model_D_minus, "D_minus")
data_combined = RooDataSet("data_combined", "Combined", full_var_set, RooFit.Index(cat),
                              RooFit.Import("D_plus", data),
                              RooFit.Import("D_minus", data_cc),
                              RooFit.WeightVar("w_scaled"))
# fixed seed for reproducibility
seed = 202605
ROOT.RooRandom.randomGenerator().SetSeed(seed)
print(f"ToyMC random seed = {seed}")

ToyMC_all = ROOT.RooMCStudy(sim_model, {x,cat}, Extended(True), SumW2Error(True), FitOptions(Save(True),PrintEvalErrors(0),PrintLevel(1), NumCPU(4), Offset(True)))
ToyMC_all.generateAndFit(1000)
#ToyMC_all.generateAndFit(100)

toyMC_frame_Acp = ToyMC_all.plotPull(Acp, Bins(50), Range(-6, 6), FitGauss(True))
toyMC_frame_Acp_Ds = ToyMC_all.plotPull(Acp_Ds, Bins(50), Range(-6, 6), FitGauss(True))
toyMC_frame_N_total = ToyMC_all.plotPull(N_total, Bins(50), Range(-6, 6), FitGauss(True))
toyMC_frame_N_total_Ds = ToyMC_all.plotPull(N_total_Ds, Bins(50), Range(-6, 6), FitGauss(True))

toyMC_frame_Acp_peak_bkg = ToyMC_all.plotPull(Acp_peak_bkg, Bins(50), Range(-6, 6), FitGauss(True))

#toyMC_frame_Acp = ToyMC_all.plotPull(Acp,  FitGauss(True))
#toyMC_frame_Acp_Ds = ToyMC_all.plotPull(Acp_Ds,  FitGauss(True))
#toyMC_frame_N_total = ToyMC_all.plotPull(N_total,  FitGauss(True))
#toyMC_frame_N_total_Ds = ToyMC_all.plotPull(N_total_Ds,  FitGauss(True))

common_title = "Pull"
toyMC_frame_Acp.GetXaxis().SetTitle("A_{CP}(D^{#pm})" +  f" {common_title}")
toyMC_frame_Acp_Ds.GetXaxis().SetTitle("A_{CP}(D^{#pm}_{s})" +  f" {common_title}")
toyMC_frame_N_total.GetXaxis().SetTitle("N_{sig}(D^{+}+D^{-})" +  f" {common_title}")
toyMC_frame_N_total_Ds.GetXaxis().SetTitle("N_{sig}(D^{+}_{s}+D^{-}_{s})" +  f" {common_title}")

toyMC_frame_Acp_peak_bkg.GetXaxis().SetTitle("A_{CP}(misID)" +  f" {common_title}")

toyMC_canvas = ROOT.TCanvas("toyMC_canvas", "D+ fit", 800, 600)
toyMC_frame_Acp.Draw()
toyMC_canvas.SaveAs(f"toy_Acp_{tree_name}_{args.sign}.png")

toyMC_canvas_Ds = ROOT.TCanvas("toyMC_canvas_Ds", "D+ fit", 800, 600)
toyMC_frame_Acp_Ds.Draw()
toyMC_canvas_Ds.SaveAs(f"toy_Acp_Ds_{tree_name}_{args.sign}.png")

toyMC_canvas_N_total = ROOT.TCanvas("toyMC_canvas_N_total", "D+ fit", 800, 600)
toyMC_frame_N_total.Draw()
toyMC_canvas_N_total.SaveAs(f"toy_N_total_{tree_name}_{args.sign}.png")

toyMC_canvas_N_total_Ds = ROOT.TCanvas("toyMC_canvas_N_total_Ds", "D+ fit", 800, 600)
toyMC_frame_N_total_Ds.Draw()
toyMC_canvas_N_total_Ds.SaveAs(f"toy_N_total_Ds_{tree_name}_{args.sign}.png")

toyMC_canvas_peak_bkg = ROOT.TCanvas("toyMC_canvas_peak_bkg", "D+ fit", 800, 600)
toyMC_frame_Acp_peak_bkg.Draw()
toyMC_canvas_peak_bkg.SaveAs(f"toy_Acp_peak_bkg_{tree_name}_{args.sign}.png")
