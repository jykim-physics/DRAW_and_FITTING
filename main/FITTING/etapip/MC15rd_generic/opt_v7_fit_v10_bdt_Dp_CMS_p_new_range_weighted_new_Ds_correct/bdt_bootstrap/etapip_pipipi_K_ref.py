import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory
from ROOT.RooFit import Extended, FitOptions, Save, PrintEvalErrors, PrintLevel, Bins, FitGauss,    NumCPU, Strategy, Offset, Range
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
BDT_cut = "0.90"

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
file_name_Dall = f"/share/storage/jykim/plots/MC15rd/etapip/pipipi/generic/ref_bootstrap_sys_MC15rd_etapip_pipipi_loose_v7_fitv10_bdt_{args.train}_{args.sign}_{BDT_cut}_{suffix}_weighted_Dall"
dir_path = os.path.dirname(file_name_Dall)
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
    pattern = f"{base_path}/{element}/{tree_name}/ref/min_unc_search/new_Ds_v2/0.92/weighted/*.BCS.root"
    file_list += glob.glob(pattern)

print(file_list)
mychain = ROOT.TChain(tree_name)
for i in file_list:
    mychain.Add(i)
print(file_list)
print(f"Numer of files: {len(file_list)}")

# Define variable and its range
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
weight_scale = 1
scale = 1/4
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

N_total = RooRealVar("N_total", "N_total (N_D+ + N_D-)", 60000*scale*N_scale,  30000*scale*N_scale, 300000*scale*N_scale)  # N_total = N_D+ + N_D-
Acp = RooRealVar("Acp", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

Nsig_D_plus = RooFormulaVar("Nsig_D_plus",
    "0.5 * N_total * (1 + Acp)",
    RooArgList(N_total, Acp))

Nsig_D_minus = RooFormulaVar("Nsig_D_minus",
    "0.5 * N_total * (1 - Acp)",
    RooArgList(N_total, Acp))

N_total_Ds = RooRealVar("N_total_Ds", "N_total (N_Ds+ + N_Ds-)", 120000*scale*N_scale,  50000*scale*N_scale,700000*scale*N_scale)  # N_total = N_D+ + N_D-
Acp_Ds = RooRealVar("Acp_Ds", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

Nsig_Ds_plus = RooFormulaVar("Nsig_Ds_plus",
    "0.5 * N_total_Ds * (1 + Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))

Nsig_Ds_minus = RooFormulaVar("Nsig_Ds_minus",
    "0.5 * N_total_Ds * (1 - Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))


Nbkg_total = ROOT.RooRealVar("Nbkg_total", "Number of background events for D+", 250000*scale*N_scale, 20000*scale*N_scale,800000*scale*N_scale)
Acp_bkg = RooRealVar("Acp_bkg", "Acp", 0, -0.5, 0.5)  # A_Cp as a fit parameter
Nbkg_D_plus = RooFormulaVar("Nbkg_D_plus",
    "0.5 * Nbkg_total * (1 + Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))

Nbkg_D_minus = RooFormulaVar("Nbkg_D_minus",
    "0.5 * Nbkg_total * (1 - Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))

f = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/etapip/pipipi/generic/fitresult/MC15rd_etapip_pipipi_ref_bdt_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_{args.sign}_0.92_weighted.root")
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

# Create a category to distinguish between D+ and D-
cat = RooCategory("sample", "sample")
cat.defineType("D_plus")
cat.defineType("D_minus")

n_bootstrap = 1000
results = {
    "sm_0": [],
    "sm_nominal": [],
    "sm_1": [],
    "sm_2": [],
    "sm_3": [],
    "sh_0": [],
    "sh_nominal": [],
    "sh_1": [],
    "sh_2": [],
    "sh_3": [],
    "NDp_0": [],
    "NDp_nominal": [],
    "NDp_1": [],
    "NDp_2": [],
    "NDp_3": [],
    "NDsp_0": [],
    "NDsp_nominal": [],
    "NDsp_1": [],
    "NDsp_2": [],
    "NDsp_3": [],
    "delta_corr_NDp_0": [],
    "delta_corr_NDp_1": [],
    "delta_corr_NDp_2": [],
    "delta_corr_NDp_3": [],
    "delta_corr_NDsp_0": [],
    "delta_corr_NDsp_1": [],
    "delta_corr_NDsp_2": [],
    "delta_corr_NDsp_3": [],
    "relative_delta_corr_NDp_0": [],
    "relative_delta_corr_NDp_1": [],
    "relative_delta_corr_NDp_2": [],
    "relative_delta_corr_NDp_3": [],
    "relative_delta_corr_NDsp_0": [],
    "relative_delta_corr_NDsp_1": [],
    "relative_delta_corr_NDsp_2": [],
    "relative_delta_corr_NDsp_3": []
}


n_entries_Dp = int(data.numEntries() / 4)
n_entries_Dm = int(data_cc.numEntries() / 4)

success_count = 0
iteration = 0

while success_count < n_bootstrap:
    iteration += 1
    data_boot_Dp_0 = data.emptyClone()
    data_boot_Dm_0 = data_cc.emptyClone()

    for _ in range(n_entries_Dp):
        idx = random.randint(0, n_entries_Dp - 1)
        data_boot_Dp_0.add(data.get(idx), data.weight())

    for _ in range(n_entries_Dm):
        idx = random.randint(0, n_entries_Dm - 1)
        data_boot_Dm_0.add(data_cc.get(idx), data_cc.weight())

    eff_0 = 0.057713
    eff_Ds_0 = 0.045093

    cut_expr_1 = "BDT > 0.91"
    eff_1 = 0.055237
    eff_Ds_1 = 0.042320
    data_boot_Dp_cut_1 = data_boot_Dp_0.reduce(cut_expr_1)
    data_boot_Dm_cut_1 = data_boot_Dm_0.reduce(cut_expr_1)

    cut_expr_nominal = "BDT > 0.92"
    eff_nominal = 0.052408
    eff_Ds_nominal = 0.039159
    data_boot_Dp_cut_nominal = data_boot_Dp_0.reduce(cut_expr_nominal)
    data_boot_Dm_cut_nominal = data_boot_Dm_0.reduce(cut_expr_nominal)

    cut_expr_2 = "BDT > 0.93"
    eff_2 = 0.049122
    eff_Ds_2 = 0.035699
    data_boot_Dp_cut_2 = data_boot_Dp_0.reduce(cut_expr_2)
    data_boot_Dm_cut_2 = data_boot_Dm_0.reduce(cut_expr_2)

    cut_expr_3 = "BDT > 0.94"
    eff_3 = 0.045345
    eff_Ds_3 = 0.031845
    data_boot_Dp_cut_3 = data_boot_Dp_0.reduce(cut_expr_3)
    data_boot_Dm_cut_3 = data_boot_Dm_0.reduce(cut_expr_3)

    fit_outputs_0 = nominal_fit_extract_Acp(data_boot_Dp_0, data_boot_Dm_0)
    fit_outputs_nominal = nominal_fit_extract_Acp(data_boot_Dp_cut_nominal, data_boot_Dm_cut_nominal)
    fit_outputs_1 = nominal_fit_extract_Acp(data_boot_Dp_cut_1, data_boot_Dm_cut_1)
    fit_outputs_2 = nominal_fit_extract_Acp(data_boot_Dp_cut_2, data_boot_Dm_cut_2)
    fit_outputs_3 = nominal_fit_extract_Acp(data_boot_Dp_cut_3, data_boot_Dm_cut_3)

    #fit_outputs_after = var_fit_extract_Acp(data_boot_Dp, data_boot_Dm, iteration)

    sm_0 = fit_outputs_0[1]
    sh_0 = fit_outputs_0[2]
    sm_nominal = fit_outputs_nominal[1]
    sh_nominal = fit_outputs_nominal[2]
    sm_1 = fit_outputs_1[1]
    sh_1 = fit_outputs_1[2]
    sm_2 = fit_outputs_2[1]
    sh_2 = fit_outputs_2[2]
    sm_3 = fit_outputs_3[1]
    sh_3 = fit_outputs_3[2]

    # Check if both fits converged properly
    if sm_0 == 0 and sh_0 == 0 and sm_nominal == 0 and sh_nominal == 0 and sm_1 == 0 and sh_1 == 0 and sm_2 == 0 and sh_2 == 0 and sm_3 == 0 and sh_3 == 0:
        ndp_0 = fit_outputs_0[3]
        ndsp_0 = fit_outputs_0[4]
        ndp_nominal = fit_outputs_nominal[3]
        ndsp_nominal = fit_outputs_nominal[4]
        ndp_1 = fit_outputs_1[3]
        ndsp_1 = fit_outputs_1[4]
        ndp_2 = fit_outputs_2[3]
        ndsp_2 = fit_outputs_2[4]
        ndp_3 = fit_outputs_3[3]
        ndsp_3 = fit_outputs_3[4]


        delta_ndp_0 = ndp_0/eff_0 - ndp_nominal/eff_nominal
        delta_ndp_1 = ndp_1/eff_1 - ndp_nominal/eff_nominal
        delta_ndp_2 = ndp_2/eff_2 - ndp_nominal/eff_nominal
        delta_ndp_3 = ndp_3/eff_3 - ndp_nominal/eff_nominal

        delta_ndsp_0 = ndsp_0/eff_0 - ndsp_nominal/eff_Ds_nominal
        delta_ndsp_1 = ndsp_1/eff_1 - ndsp_nominal/eff_Ds_nominal
        delta_ndsp_2 = ndsp_2/eff_2 - ndsp_nominal/eff_Ds_nominal
        delta_ndsp_3 = ndsp_3/eff_3 - ndsp_nominal/eff_Ds_nominal

        relative_delta_ndp_0 = delta_ndp_0 / (ndp_nominal/eff_nominal)
        relative_delta_ndp_1 = delta_ndp_1 / (ndp_nominal/eff_nominal)
        relative_delta_ndp_2 = delta_ndp_2 / (ndp_nominal/eff_nominal)
        relative_delta_ndp_3 = delta_ndp_3 / (ndp_nominal/eff_nominal)

        relative_delta_ndsp_0 = delta_ndsp_0 / (ndsp_nominal/eff_Ds_nominal)
        relative_delta_ndsp_1 = delta_ndsp_1 / (ndsp_nominal/eff_Ds_nominal)
        relative_delta_ndsp_2 = delta_ndsp_2 / (ndsp_nominal/eff_Ds_nominal)
        relative_delta_ndsp_3 = delta_ndsp_3 / (ndsp_nominal/eff_Ds_nominal)

        results["sm_0"].append(sm_0)
        results["sm_nominal"].append(sm_nominal)
        results["sm_1"].append(sm_1)
        results["sm_2"].append(sm_2)
        results["sm_3"].append(sm_3)
        results["sh_0"].append(sh_0)
        results["sh_nominal"].append(sh_nominal)
        results["sh_1"].append(sh_1)
        results["sh_2"].append(sh_2)
        results["sh_3"].append(sh_3)

        results["NDp_0"].append(ndp_0)
        results["NDp_nominal"].append(ndp_nominal)
        results["NDp_1"].append(ndp_1)
        results["NDp_2"].append(ndp_2)
        results["NDp_3"].append(ndp_3)

        results["NDsp_0"].append(ndsp_0)
        results["NDsp_nominal"].append(ndsp_nominal)
        results["NDsp_1"].append(ndsp_1)
        results["NDsp_2"].append(ndsp_2)
        results["NDsp_3"].append(ndsp_3)

        results["delta_corr_NDp_0"].append(delta_ndp_0)
        results["delta_corr_NDp_1"].append(delta_ndp_1)
        results["delta_corr_NDp_2"].append(delta_ndp_2)
        results["delta_corr_NDp_3"].append(delta_ndp_3)

        results["delta_corr_NDsp_0"].append(delta_ndsp_0)
        results["delta_corr_NDsp_1"].append(delta_ndsp_1)
        results["delta_corr_NDsp_2"].append(delta_ndsp_2)
        results["delta_corr_NDsp_3"].append(delta_ndsp_3)

        results["relative_delta_corr_NDp_0"].append(relative_delta_ndp_0)
        results["relative_delta_corr_NDp_1"].append(relative_delta_ndp_1)
        results["relative_delta_corr_NDp_2"].append(relative_delta_ndp_2)
        results["relative_delta_corr_NDp_3"].append(relative_delta_ndp_3)

        results["relative_delta_corr_NDsp_0"].append(relative_delta_ndsp_0)
        results["relative_delta_corr_NDsp_1"].append(relative_delta_ndsp_1)
        results["relative_delta_corr_NDsp_2"].append(relative_delta_ndsp_2)
        results["relative_delta_corr_NDsp_3"].append(relative_delta_ndsp_3)

        success_count += 1
        print(f"[{success_count}/{n_bootstrap}] successful bootstrap. delta_corr_NDp_0 = {delta_ndp_0:.8f}, relative_delta_corr_NDp_0 = {relative_delta_ndp_0:.8f}")
    else:
        print(f"[{iteration}] Fit did not converge properly. Retrying... (sm_0={sm_0}, sh_0={sh_0}, sm_1={sm_1}, sh_1={sh_1}, sm_2={sm_3}, sh_2={sh_2}, sm_3={sm_3}, sh_3={sh_3}, sm_nominal={sm_nominal}, sh_nominal={sh_nominal},)")

    del data_boot_Dp_0
    del data_boot_Dp_cut_1
    del data_boot_Dp_cut_2
    del data_boot_Dp_cut_3
    del data_boot_Dp_cut_nominal

    del data_boot_Dm_0
    del data_boot_Dm_cut_1
    del data_boot_Dm_cut_2
    del data_boot_Dm_cut_3
    del data_boot_Dm_cut_nominal
    gc.collect()

ak_array = ak.Array(results)
with uproot.recreate(f"bootstrap_results_ref_etapip_pipipi_{args.sign}_converge.root") as f:
    f["tree"] = ak_array

# Final results
relative_delta_corr_NDp_0_array = np.array(results["relative_delta_corr_NDp_0"])

mean_value = np.mean(relative_delta_corr_NDp_0_array)
rms_value = np.std(relative_delta_corr_NDp_0_array, ddof=1)

print(f"ex: Bootstrap results:")
print(f"  Mean in relative_delta_corr_NDp_0 = {mean_value:.8f}")
print(f"  RMS uncertainty     = {rms_value:.8f}")
