import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory, RooStats, TFile
from ROOT.RooFit import Extended, FitOptions, Save, PrintEvalErrors, PrintLevel, Bins, FitGauss,    NumCPU, Strategy, Offset
import glob
import ctypes
import os
import argparse
import random
import numpy as np
import uproot
import awkward as ak

parser = argparse.ArgumentParser(description="Process Dp_CMS_sign argument")
parser.add_argument("-s","--sign", choices=["plus", "minus","all"], required=True,
                    help="Specify 'plus' or 'minus'")

args = parser.parse_args()
print(f"Dp_CMS_sign is set to: {args.sign}")

if args.sign == "plus":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>0"
elif args.sign == "minus":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta<0"
elif args.sign == "all":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>-10"

BDT_cut = 0.74
suffix = f"{BDT_cut}_new_Ds_correct"

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/Kspip//MC15rd_Kspip_loose_v7_1_250228_Dp_CMS_p_v3"
cm_elements = ["MCrd_Ks_e7_18_4S_v3", "MCrd_Ks_e20_b26_v1", "MCrd_Ks_e20_e26_4S_v2", "MCrd_Ks_e21_5S_scan_v1", "MCrd_Ks_mori_off_v1"]

ref_tree = "etapip_pipipi"
file_list = []
tree_name = "Ks"
for element in cm_elements:
    pattern = f"{base_path}/{element}/{ref_tree}/{tree_name}/{BDT_cut}/bdtg_Ds/*.BCS.bdtg.root"
    file_list += glob.glob(pattern)
print(file_list)
print(f"Number of files: {len(file_list)}")

mychain = ROOT.TChain(tree_name)
for i in file_list:
    mychain.Add(i)

fit_variable = "Dp_M"
fit_var_name = "M(D^{+}) [GeV/c^{2}]"
fit_range = (1.80, 1.93)
truth_var = "Dp_isSignal"
charge_var = "Pip_charge"

cuts_Dp = charge_var + "==1"
cuts_Dm = charge_var + "==-1"

cuts_Dp += " && " + Dp_CMS_cosTheta_cut
cuts_Dm += " && " + Dp_CMS_cosTheta_cut

x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
#x.setBins(200)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)
Dp_CMS_cosTheta = ROOT.RooRealVar("Dp_CMS_cosTheta", "Dp_CMS_cosTheta", -1, 1)
bdtg_norm = ROOT.RooRealVar("bdtg_norm", "bdtg_norm", 0, 2)

full_var_set = ROOT.RooArgSet(x, Pip_charge, Dp_CMS_cosTheta,bdtg_norm)

before_data = ROOT.RooDataSet("data", "", mychain, full_var_set, cuts_Dp)

scale = 1
#scale = 1/4
w_scaled = ROOT.RooFormulaVar("w_scaled", "Scaled Weight", f"{scale}*bdtg_norm", ROOT.RooArgList(bdtg_norm))

before_data.addColumn(w_scaled)
before_data.get().Print("v")

print("Before weighting:", before_data.numEntries())
print("Before weighting sum:", before_data.sumEntries())

data = ROOT.RooDataSet("data_weighted", "Weighted Data", before_data, before_data.get(), "", "w_scaled")
print("After weighting:", data.numEntries())
print("After weighting sum:", data.sumEntries())

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


def fit_and_extract_acp(data_Dp, data_Dm, full_var_set, isAfter_or_Before):
    N_total = RooRealVar("N_total", "N_total (N_D+ + N_D-)", 100000, 1000, 1000000)
    Acp = RooRealVar("Acp", "Acp", 0, -1, 1)

    Nsig_D_plus = RooFormulaVar("Nsig_D_plus", "0.5 * N_total * (1 + Acp)", ROOT.RooArgList(N_total, Acp))
    Nsig_D_minus = RooFormulaVar("Nsig_D_minus", "0.5 * N_total * (1 - Acp)", ROOT.RooArgList(N_total, Acp))

    Nbkg_total = RooRealVar("Nbkg_total", "Nbkg_total", 100000, 0, 1000000)
    Acp_bkg = RooRealVar("Acp_bkg", "Acp_bkg", 0, -0.2, 0.2)
    Nbkg_D_plus = RooFormulaVar("Nbkg_D_plus", "0.5 * Nbkg_total * (1 + Acp_bkg)", ROOT.RooArgList(Nbkg_total, Acp_bkg))
    Nbkg_D_minus = RooFormulaVar("Nbkg_D_minus", "0.5 * Nbkg_total * (1 - Acp_bkg)", ROOT.RooArgList(Nbkg_total, Acp_bkg))

    mean = ROOT.RooRealVar("mean", "mean", 1.86, 1.84, 1.88)  # Central value
    sigma = ROOT.RooRealVar("sigma", "sigma", 0.002, 0.0001, 0.01)  # Width parameter
    gamma = ROOT.RooRealVar("gamma", "gamma", 0.01, -2.0, 2.0)  # Skewness parameter
    delta = ROOT.RooRealVar("delta", "delta", 0.6, 0.001, 3.0)  # Shape parameter

    johnson = ROOT.RooJohnson("johnson", "double-sided Crystal Ball using Johnson SU", x,  mean, sigma, gamma, delta)

    mean_gauss = ROOT.RooRealVar("mean_gauss", "Gaussian mean", 0.0)  # Convolution will   center the Gaussian at zero
    sigma_gauss = ROOT.RooRealVar("sigma_gauss", "Gaussian width", 0.002, 0.00001, 0.01)

    gauss = ROOT.RooGaussian("gauss", "Gaussian PDF", x, mean_gauss, sigma_gauss)
    # Perform the convolution
    sig_model = ROOT.RooFFTConvPdf("sig_model", "Convolution of Johnson SU and Gaussian", x, johnson, gauss)
    x_bkg1_Cheby_c0 = ROOT.RooRealVar("x_bkg1_Cheby_c0", "c0",0.0, -1.0, 1.0)
    x_bkg1_Cheby_c1 = ROOT.RooRealVar("x_bkg1_Cheby_c1", "c0",0.0, -1.0, 1.0)
    x_bkg1_Cheby_c2 = ROOT.RooRealVar("x_bkg1_Cheby_c2", "c0",0.0, -1.0, 1.0)
    x_bkg1_tau = ROOT.RooRealVar("x_bkg1_tau", "c0",-0.5, -20, 10)
    #model_bkg = ROOT.RooPolynomial("model_bkg", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1, x_bkg1_Cheby_c2))
    model_bkg = ROOT.RooExponential("model_bkg", "x_bkg1", x, x_bkg1_tau)
    #bkg_frac = ROOT.RooRealVar("bkg_frac", "fraction of Gaussian in BKG", 0.25, 0.1, 1)
    #model_bkg = ROOT.RooAddPdf("model_bkg", "Gaus + Exp", RooArgList(rhopeta, bkg_comb), bkg_frac)

    model_D_plus = RooAddPdf("model_D_plus", "D+ model", ROOT.RooArgList(sig_model, model_bkg), ROOT.RooArgList(Nsig_D_plus, Nbkg_D_plus))
    model_D_minus = RooAddPdf("model_D_minus", "D- model", ROOT.RooArgList(sig_model, model_bkg), ROOT.RooArgList(Nsig_D_minus, Nbkg_D_minus))

    cat = RooCategory("sample", "sample")
    cat.defineType("D_plus")
    cat.defineType("D_minus")

    sim_model = RooSimultaneous("sim_model", "Simultaneous model", cat)
    sim_model.addPdf(model_D_plus, "D_plus")
    sim_model.addPdf(model_D_minus, "D_minus")

    if isAfter_or_Before == 'after':
        data_combined = RooDataSet("data_combined", "Combined", full_var_set, RooFit.Index(cat),
                                  RooFit.Import("D_plus", data_Dp),
                                  RooFit.Import("D_minus", data_Dm),
                                  RooFit.WeightVar("w_scaled"))
    elif isAfter_or_Before == 'before':
        data_combined = RooDataSet("data_combined", "Combined", full_var_set, RooFit.Index(cat),
                                  RooFit.Import("D_plus", data_Dp),
                                  RooFit.Import("D_minus", data_Dm),
                                  )

    nll = sim_model.createNLL(data_combined, RooFit.Extended(True), ROOT.RooFit.NumCPU(4),   ROOT.RooFit.Offset("initial"))
    minimizer = ROOT.RooMinimizer(nll)
    minimizer.setStrategy(2)
    minimizer.setPrintLevel(0)
    status_migrad = minimizer.migrad()
    if status_migrad != 0:
        print(f"Migrad failed with status: {status_migrad}")
    status_hesse = minimizer.hesse()
    if status_hesse != 0:
        print(f"Hesse failed with status: {status_hesse}")


    return Acp.getVal(), status_migrad, status_hesse

n_bootstrap = 500
results = {
    "acp_before": [],
    "acp_after": [],
    "delta_acp": [],
    "status_migrad_before": [],
    "status_hesse_before": [],
    "status_migrad_after": [],
    "status_hesse_after": []
}

n_entries_Dp = int(data.numEntries()/4)
n_entries_Dm = int(data_cc.numEntries()/4)

for i in range(n_bootstrap):
    data_boot_Dp = data.emptyClone()
    data_boot_Dm = data_cc.emptyClone()
    data_boot_Dp_origin = data.emptyClone()
    data_boot_Dm_origin = data_cc.emptyClone()

    for _ in range(n_entries_Dp):
        idx = random.randint(0, n_entries_Dp - 1)
        data_boot_Dp_origin.add(data.get(idx))
        data_boot_Dp.add(data.get(idx), data.weight())

    for _ in range(n_entries_Dm):
        idx = random.randint(0, n_entries_Dm - 1)
        data_boot_Dm_origin.add(data_cc.get(idx))
        data_boot_Dm.add(data_cc.get(idx), data_cc.weight())

    #for _ in range(n_entries_Dp):
    #    idx = random.randint(0, n_entries_Dp - 1)
    #    data_boot_Dp.add(data.get(idx), data.weight())

    #for _ in range(n_entries_Dm):
    #    idx = random.randint(0, n_entries_Dm - 1)
    #    data_boot_Dm.add(data_cc.get(idx), data_cc.weight())

    data_boot_Dp.Print("v")
    data_boot_Dp_origin.Print("v")
    print("data_boot_Dp.numEntries:", data_boot_Dp.numEntries())
    print("data_boot_Dp.sumEntries:", data_boot_Dp.sumEntries())
    print("data_boot_Dp_origin.numEntries:", data_boot_Dp_origin.numEntries())
    print("data_boot_Dp_origin.sumEntries:", data_boot_Dp_origin.sumEntries())

    fit_outputs_after = fit_and_extract_acp(data_boot_Dp, data_boot_Dm, full_var_set, 'after')
    fit_outputs_before = fit_and_extract_acp(data_boot_Dp_origin, data_boot_Dm_origin, full_var_set, 'before')
    acp_before = fit_outputs_before[0]
    acp_after = fit_outputs_after[0]
    delta_acp = acp_after - acp_before
    sm_b =  fit_outputs_before[1]
    sh_b =  fit_outputs_before[2]
    sm_a =  fit_outputs_after[1]
    sh_a =  fit_outputs_after[2]

    #if max(sm_b, sh_b, sm_a, sh_a) != 0:
        #continue

    print(f"delta_acp = {delta_acp:.8f}")

    results["acp_before"].append(acp_before)
    results["acp_after"].append(acp_after)
    results["delta_acp"].append(delta_acp)
    results["status_migrad_before"].append(sm_b)
    results["status_hesse_before"].append(sh_b)
    results["status_migrad_after"].append(sm_a)
    results["status_hesse_after"].append(sh_a)


ak_array = ak.Array(results)
with uproot.recreate(f"bootstrap_acp_results_Dsp_etapip_pipipi_{args.sign}.root") as f:
    f["acp_bootstrap"] = ak_array

# Final results
delta_acp_array = np.array(results["delta_acp"])

mean_shift = np.mean(delta_acp_array)
rms_shift = np.std(delta_acp_array)

print(f"Bootstrap results:")
print(f"  Mean shift in ΔA_CP = {mean_shift:.8f}")
print(f"  RMS uncertainty     = {rms_shift:.8f}")

