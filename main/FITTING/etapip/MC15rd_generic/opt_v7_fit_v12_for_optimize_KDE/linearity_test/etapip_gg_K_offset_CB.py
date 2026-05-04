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

suffix = "KDE"
file_name_Dall = f"/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/bootstrap/bootstrap_sys_MC15rd_etaKp_gg_fit_opt_loose_v7_fitv12_bdt_{args.train}_Dall_CMS_{args.sign}_{BDT_cut}_{suffix}_weighted_Dall"
dir_path = os.path.dirname(file_name_Dall)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto"
cm_elements = ["15rd_jae_e7_18_4S_v3", "15rd_jae_e20_b26_v1", "15rd_jae_e20_e26_4S_v2", "15rd_jae_e21_5S_scan_v1", "15rd_jae_mori_off_v1"]

tree_name = "etapip_gg_K"
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
fit_var_name = "M(#eta_{#gamma#gamma}K^{+}) [GeV/c^{2}]"
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
etapip_Eta_Easym = ROOT.RooRealVar("etapip_Eta_Easym", "etapip_Eta_Easym", 0, 1)
Dp_cosHelicityAngleMomentum = ROOT.RooRealVar("Dp_cosHelicityAngleMomentum", "Dp_cosHelicityAngleMomentum", -1, 1)
Dp_CMS_p = ROOT.RooRealVar("Dp_CMS_p", "Dp_CMS_p", 0, 100)
ds_weight = ROOT.RooRealVar("ds_weight", "ds_weight", -1000, 1000)
rank_Dp_chiProb = ROOT.RooRealVar("rank_Dp_chiProb", "rank_Dp_chiProb", 0, 1000)

full_var_set = ROOT.RooArgSet(x, Pip_charge, Dp_CMS_cosTheta, BDT, Pip_dr, Dp_dz,
                              Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane,
                              etapip_Eta_Easym, Dp_cosHelicityAngleMomentum,
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

f = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etaKp_gg_fit_opt_loose_v7_fitv12_1_bdt_train_Dp_CMS_p_{args.sign}_0.86_KDE_weighted.root")
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

f_in = ROOT.TFile("/share/storage/jykim/plots/MC15rd/etaKp/gg/MC15re_6M_etapip_gg_Dp_M_v12_result_true_extended_train_Dp_CMS_p.0.86_workspace.root", "READ")
ws = f_in.Get("ws_kde")
kde_model = ws.pdf("model")
kde_model.SetName("kde_model")


mean = fit_args.find("mean")
scale_factor = fit_args.find("scale_factor")
Ds_mean = fit_args.find("Ds_mean")
x_bkg1_tau = fit_args.find("x_bkg1_tau")

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

model_bkg = ROOT.RooExponential("model_bkg", "x_bkg1", x, x_bkg1_tau)


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
#ToyMC_all = ROOT.RooMCStudy(sim_model, {x,cat}, Extended(True), SumW2Error(True), FitOptions(Save(True),PrintEvalErrors(0),PrintLevel(1), NumCPU(4), Offset("initial")))

N_total_value = N_total.getVal()
N_total_error = N_total.getError()

def Linearity_test(sim_model, cat, N_Input=100, N_gen=500, N_total=N_total):
  N_total.setVal(N_Input)
  ToyMC_all = ROOT.RooMCStudy(sim_model, {x,cat}, Extended(True), SumW2Error(True), FitOptions(Save(True),PrintEvalErrors(0),PrintLevel(1), NumCPU(8), Offset(True)))
  ToyMC_all.generateAndFit(N_gen)

  toyMC_frame_N_total_pull = ToyMC_all.plotPull(N_total, Bins(20))
  pullMean = ROOT.RooRealVar("pullMean","",0,-10,10)
  pullSigma = ROOT.RooRealVar("pullSigma","",1,0.1,5)
  pullMean.setPlotLabel("#mu")
  pullSigma.setPlotLabel("#sigma")

  pullGauss = ROOT.RooGaussian("pullGauss", "", toyMC_frame_N_total_pull.getPlotVar() , pullMean, pullSigma)
  r_pull = pullGauss.fitTo(ToyMC_all.fitParDataSet(),NumCPU=6,PrintLevel=-1)

  pullGauss.plotOn(toyMC_frame_N_total_pull)
  pullGauss.paramOn(toyMC_frame_N_total_pull, ROOT.RooFit.Layout(0.60, 0.80, 0.9), ROOT.RooFit.Format("NE",ROOT.RooFit.AutoPrecision(1)))
  toyMC_canvas = ROOT.TCanvas("toyMC_canvas", "D+ fit", 1600, 600)
  toyMC_canvas.Divide(2,1)
  toyMC_canvas.cd(1)
  toyMC_frame_N_total_pull.Draw("PE")

  toyMC_frame_N_total = ToyMC_all.plotParam(N_total, Bins(20))
  Mean = ROOT.RooRealVar("Mean","",N_Input, 0.5*N_Input, 1.5*N_Input)
  Sigma = ROOT.RooRealVar("Sigma","",N_Input**0.5, N_Input**0.5/4, N_Input*0.8)
  Mean.setPlotLabel("#mu")
  Sigma.setPlotLabel("#sigma")

  Gauss = ROOT.RooGaussian("Gauss", "", toyMC_frame_N_total.getPlotVar() , Mean, Sigma)
  r_N_total_pull = Gauss.fitTo(ToyMC_all.fitParDataSet(),NumCPU=6,PrintLevel=-1)

  Gauss.plotOn(toyMC_frame_N_total)
  Gauss.paramOn(toyMC_frame_N_total, ROOT.RooFit.Layout(0.60, 0.80, 0.9), ROOT.RooFit.Format("NE",ROOT.RooFit.AutoPrecision(1)))
  toyMC_canvas.cd(2)
  toyMC_frame_N_total.Draw("PE")
  toyMC_canvas.SaveAs(f"toy_{tree_name}_{N_Input:.3f}.png")

  Nsig_mean = Mean.getVal()
  Nsig_mean_error = Mean.getError()

  return Nsig_mean, Nsig_mean_error

expected_values = np.linspace(N_total_value-N_total_error*3, N_total_value+N_total_error*3, 27)
N_input = list()
N_predict = list()
Fit_error = list()
for i in expected_values:
    N_input.append(i)

    N_fit, temp_fit_error = Linearity_test(sim_model, cat, N_Input=i,N_gen=1000)
    #N_fit, temp_fit_error = Linearity_test(sim_model, cat, N_Input=i,N_gen=1)
    N_predict.append(N_fit)
    Fit_error.append(temp_fit_error)

    print(f'Prediction: {N_fit}, Input: {i}, Error: {temp_fit_error}')


import matplotlib.pyplot as plt
# everything in iminuit is done through the Minuit object, so we import it
import iminuit
from iminuit import Minuit
from iminuit.cost import LeastSquares
print("iminuit version:", iminuit.__version__)
def line(x, c0, c1):
    return c0 + x * c1

least_squares = LeastSquares(N_input, N_predict, Fit_error, line)

m = Minuit(least_squares, c0=0, c1=0)  # starting values for α and β
m.migrad()  # finds minimum of least_squares function
m.hesse()
# # plt.scatter(N_input, N_predict)
plt.errorbar(N_input, N_predict, yerr=Fit_error, fmt="o",label='Data')
# N_input = np.array(N_input)
N_start = N_input[0]
N_end = N_input[-1]
np_N_input = np.linspace(N_start*0.97,N_end*1.03,101)

plt.plot(np_N_input, line(np_N_input, *m.values), label=r"Fit($y=c_0+c_1x$)")
# plt.plot([N_start*0.9,N_end*1.05], line([N_start*0.9,N_end*1.05], *m.values), label=r"Fit($y=c_0+c_1x$)")
# plt.xlim(N_start*0.9,N_end*1.05)
# plt.ylim(N_start*0.9,N_end*1.05)
plt.plot([N_start*0.97,N_end*1.03], [N_start*0.97,N_end*1.03], label='y=x')

fit_info = [
    f"$\\chi^2$/$n_\\mathrm{{dof}}$ = {m.fval:.1f} / {m.ndof:.0f} = {m.fmin.reduced_chi2:.1f}",
]
for p, v, e in zip(m.parameters, m.values, m.errors):
    if p=='c0':
        p = r'$c_0$'
    elif p=='c1':
        p = r'$c_1$'
    fit_info.append(f"{p} = ${v:.3f} \\pm {e:.3f}$")

plt.legend(title="\n".join(fit_info), frameon=False, fontsize=13)

plt.xlabel("Input")
plt.ylabel("Prediction")
plt.xlim(N_start*0.97,N_end*1.03)
plt.ylim(N_start*0.97,N_end*1.03)
# plt.xlim(N_start,N_end)
# plt.ylim(N_start,N_end)
plt.tight_layout()
plt.savefig(f"Linearity_{tree_name}_fit.png")
plt.show();
