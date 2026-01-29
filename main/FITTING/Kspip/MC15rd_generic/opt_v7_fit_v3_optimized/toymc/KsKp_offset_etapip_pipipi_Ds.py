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

args = parser.parse_args()
print(f"Dp_CMS_sign is set to: {args.sign}")

if args.sign == "plus":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>0"
elif args.sign == "minus":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta<0"
elif args.sign == "all":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>-10"

BDT_cut="0.77"

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/Kspip/MC15rd_Kspip_loose_v7_1_260109"
cm_elements = ["MC_KsHp_e7_18_4S_v3", "MC_KsHp_e20_b26_v1", "MC_KsHp_e20_e26_4S_v2", "MC_KsHp_e21_5Sscan_v1", "MC_KsHp_mori_off_v1"]

ref_tree = "etapip_pipipi_K"
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
Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane = ROOT.RooRealVar("Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane", "Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane'", -1,1)
Dp_cosHelicityAngleMomentum = ROOT.RooRealVar("Dp_cosHelicityAngleMomentum", "Dp_cosHelicityAngleMomentum", -1, 1)
Dp_CMS_p = ROOT.RooRealVar("Dp_CMS_p", "Dp_CMS_p", 0, 100)
rank_Dp_chiProb = ROOT.RooRealVar("rank_Dp_chiProb", "rank_Dp_chiProb", 0, 1000)
ds_weight = ROOT.RooRealVar("ds_weight", "ds_weight", 0, 1000)

full_var_set = ROOT.RooArgSet(x, Pip_charge, Dp_CMS_cosTheta, BDT, Pip_dr, Dp_dz,
                              Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane,
                              Dp_cosHelicityAngleMomentum,
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

f = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/KsKp/pipipi/generic/fitresult/MC15rd_Kspip_pipipi_K_fit_opt_loose_v7_fitv3_Ds_train_Dp_CMS_p_Dp_CMS_{args.sign}_sumw2fixed_weighted.root")
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
Nbkg_total = fit_args.find("Nbkg_total")
Acp_bkg = fit_args.find("Acp_bkg")
Nbkg_D_plus = RooFormulaVar("Nbkg_D_plus",
    "0.5 * Nbkg_total * (1 + Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))
Nbkg_D_minus = RooFormulaVar("Nbkg_D_minus",
    "0.5 * Nbkg_total * (1 - Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))

mean   = fit_args.find("mean")
sigma  = fit_args.find("sigma")
gamma  = fit_args.find("gamma")
delta  = fit_args.find("delta")
x_bkg1_tau = fit_args.find("x_bkg1_tau")
sigma_gauss = fit_args.find("sigma_gauss")

mean_gauss = const_args.find("mean_gauss")

johnson = ROOT.RooJohnson("johnson", "double-sided Crystal Ball using Johnson SU", x,  mean, sigma, gamma, delta)
gauss = ROOT.RooGaussian("gauss", "Gaussian PDF", x, mean_gauss, sigma_gauss)
sig_model = ROOT.RooFFTConvPdf("sig_model", "Convolution of Johnson SU and Gaussian", x, johnson, gauss)

model_bkg = ROOT.RooExponential("model_bkg", "x_bkg1", x, x_bkg1_tau)
model_D_plus = ROOT.RooAddPdf("model_D_plus", "D+ model",
                              ROOT.RooArgList(sig_model,  model_bkg),
                              ROOT.RooArgList(Nsig_D_plus,  Nbkg_D_plus))
model_D_minus = ROOT.RooAddPdf("model_D_minus", "D- model",
                              ROOT.RooArgList(sig_model,  model_bkg),
                              ROOT.RooArgList(Nsig_D_minus,  Nbkg_D_minus))
cat = RooCategory("sample", "sample")
cat.defineType("D_plus")
cat.defineType("D_minus")
sim_model = RooSimultaneous("sim_model", "Simultaneous model", cat)
sim_model.addPdf(model_D_plus, "D_plus")
sim_model.addPdf(model_D_minus, "D_minus")

data_combined = RooDataSet("data_combined", "Combined data", full_var_set, RooFit.Index(cat),
                           RooFit.Import("D_plus", data),
                           RooFit.Import("D_minus", data_cc),
                           RooFit.WeightVar('w_scaled'))

ToyMC_all = ROOT.RooMCStudy(sim_model, {x,cat}, Extended(True), SumW2Error(True), FitOptions(Save(True),PrintEvalErrors(0),PrintLevel(1), NumCPU(8), Offset("initial")))
ToyMC_all.generateAndFit(1000)

toyMC_frame_Acp = ToyMC_all.plotPull(Acp, Bins(50), Range(-6, 6), FitGauss(True))
toyMC_frame_N_total = ToyMC_all.plotPull(N_total, Bins(50), Range(-6, 6), FitGauss(True))

common_title = "Pull"
toyMC_frame_Acp.GetXaxis().SetTitle("A_{CP}(D^{#pm}_{s})" +  f" {common_title}")
toyMC_frame_N_total.GetXaxis().SetTitle("N_{sig}(D^{#pm}_{s})" +  f" {common_title}")


toyMC_canvas = ROOT.TCanvas("toyMC_canvas", "D+ fit", 800, 600)
toyMC_frame_Acp.Draw()
toyMC_canvas.SaveAs(f"toy_Acp_{ref_tree}_{tree_name}_{args.sign}.png")

toyMC_canvas_N_total = ROOT.TCanvas("toyMC_canvas_N_total", "D+ fit", 800, 600)
toyMC_frame_N_total.Draw()
toyMC_canvas_N_total.SaveAs(f"toy_N_total_{ref_tree}_{tree_name}_{args.sign}.png")

