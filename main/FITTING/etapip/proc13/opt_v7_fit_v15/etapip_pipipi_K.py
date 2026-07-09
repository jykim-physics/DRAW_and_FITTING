import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory
from ROOT.RooFit import Extended, FitOptions, Save, PrintEvalErrors, PrintLevel, Bins, FitGauss,    NumCPU, Strategy, Offset
import glob
import ctypes
import os
import argparse

#ROOT.RooRandom.randomGenerator().SetSeed(12345)


parser = argparse.ArgumentParser(description="Process Dp_CMS_sign argument")
parser.add_argument("-s","--sign", choices=["plus", "minus","all"], required=True,
                    help="Specify 'plus' or 'minus'")
parser.add_argument("-t","--train", required=True,
                    help="Specify train version")
parser.add_argument("-b","--bdt", required=True,
                    help="Specify BDT cut")

args = parser.parse_args()
print(f"Dp_CMS_sign is set to: {args.sign}")

BDT_cut = str(args.bdt)
#BDT_cut = 0.92

if args.sign == "plus":
	Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>0"
	N_scale = 0.64
elif args.sign == "minus":
	Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta<0"
	N_scale = 0.43
elif args.sign == "all":
	Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>-10"
	N_scale = 1

suffix = "KDE_fixed_2nd_cheby_unblind"
file_name_Dp = f"/share/storage/jykim/plots/proc_all/etaKp/pipipi/generic/proc13_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_{args.train}_Dp_CMS_{args.sign}_{BDT_cut}_{suffix}_weighted.png"
file_name_Dm = f"/share/storage/jykim/plots/proc_all/etaKp/pipipi/generic/proc13_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_{args.train}_Dm_CMS_{args.sign}_{BDT_cut}_{suffix}_weighted.png"
file_name_Dall = f"/share/storage/jykim/plots/proc_all/etaKp/pipipi/generic/proc13_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_{args.train}_Dall_CMS_{args.sign}_{BDT_cut}_{suffix}_weighted.pdf"
fitresult_name = f"/share/storage/jykim/plots/proc_all/etaKp/pipipi/generic/fitresult/proc13_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_{args.train}_{args.sign}_{BDT_cut}_{suffix}_weighted.root"
fitresult_text = f"/share/storage/jykim/plots/proc_all/etaKp/pipipi/generic/fitresult/proc13_etaKp_pipipi_fit_opt_loose_v7_fitv15_bdt_{args.train}_{args.sign}_{BDT_cut}_{suffix}_weighted.txt"
dir_path = os.path.dirname(file_name_Dp)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)
dir_path = os.path.dirname(fitresult_name)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)
print(fitresult_text)

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/proc13/proc13_EtaHp_loose_v7"
cm_elements = ["jae_13_had_4S_off_v1", "jae_13_had_4S_v3", "jae_23_had_4S_off_v1", "jae_23_had_4S_v1", \
               "jae_23_had_5Sscan_10657_v1", "jae_23_had_5Sscan_10706_v1", "jae_23_had_5Sscan_10751_v1", "jae_23_had_5Sscan_10810_v1"]

tree_name = "etapip_pipipi_K"
file_list = []
for element in cm_elements:
    pattern = f"{base_path}/{element}/{tree_name}/unblind/{BDT_cut}/*BDT.root"
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
#rank_Dp_chiProb = ROOT.RooRealVar("rank_Dp_chiProb", "rank_Dp_chiProb", 0, 1000)
rank_Dp_chiProb = ROOT.RooRealVar("rank_Dp_chiProb", "rank_Dp_chiProb", -100000, 1000000)

full_var_set = ROOT.RooArgSet(x, Pip_charge, Dp_CMS_cosTheta, BDT, Pip_dr, Dp_dz,
                              Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane,
                              Dp_cosHelicityAngleMomentum,
                              Dp_CMS_p,rank_Dp_chiProb)

scale = 1
data = ROOT.RooDataSet("data", "", mychain, full_var_set, cuts_Dp)
print(f"Charge Plus events: {data.sumEntries()}")

mychain_cc = ROOT.TChain(tree_name)
for i in file_list:
    mychain_cc.Add(i)
data_cc = ROOT.RooDataSet("data", "", mychain_cc, full_var_set, cuts_Dm)
print(f"Charge Minus events: {data_cc.sumEntries()}")

N_total = RooRealVar("N_total", "N_total (N_D+ + N_D-)", 1200*scale*N_scale, 0*scale*N_scale, 20000*scale*N_scale)  # N_total = N_D+ + N_D-
#N_total = RooRealVar("N_total", "N_total (N_D+ + N_D-)", 1000*scale*N_scale, 0*scale*N_scale, 10000*scale*N_scale)  # N_total = N_D+ + N_D-
#N_total = RooRealVar("N_total", "N_total (N_D+ + N_D-)", 2400*scale*N_scale, 0*scale*N_scale, 50000*scale*N_scale)  # N_total = N_D+ + N_D-
Acp = RooRealVar("Acp", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

# Use Acp and N_total to define the expected signal yields for D+ and D-
Nsig_D_plus = RooFormulaVar("Nsig_D_plus",
    "0.5 * N_total * (1 + Acp)",
    RooArgList(N_total, Acp))

Nsig_D_minus = RooFormulaVar("Nsig_D_minus",
    "0.5 * N_total * (1 - Acp)",
    RooArgList(N_total, Acp))

#N_total_Ds = RooRealVar("N_total_Ds", "N_total (N_Ds+ + N_Ds-)", 8000*scale*N_scale, 0*scale*N_scale,100000*scale*N_scale)  # N_total = N_D+ + N_D-
N_total_Ds = RooRealVar("N_total_Ds", "N_total (N_Ds+ + N_Ds-)", 2000*scale*N_scale, 0*scale*N_scale,20000*scale*N_scale)  # N_total = N_D+ + N_D-
#N_total_Ds = RooRealVar("N_total_Ds", "N_total (N_Ds+ + N_Ds-)", 16000*scale*N_scale, 0*scale*N_scale,100000*scale*N_scale)  # N_total = N_D+ + N_D-
Acp_Ds = RooRealVar("Acp_Ds", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

# Use Acp and N_total to define the expected signal yields for D+ and D-
Nsig_Ds_plus = RooFormulaVar("Nsig_Ds_plus",
    "0.5 * N_total_Ds * (1 + Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))

Nsig_Ds_minus = RooFormulaVar("Nsig_Ds_minus",
    "0.5 * N_total_Ds * (1 - Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))


#Nbkg_total = ROOT.RooRealVar("Nbkg_total", "Number of background events for D+", 30000*scale*N_scale, 0*scale*N_scale,100000*scale*N_scale)
Nbkg_total = ROOT.RooRealVar("Nbkg_total", "Number of background events for D+", 15000*scale*N_scale, 0*scale*N_scale,50000*scale*N_scale)

#Nbkg_total = ROOT.RooRealVar("Nbkg_total", "Number of background events for D+", 6000*scale*N_scale, 0*scale*N_scale,100000*scale*N_scale)
#Nbkg_total = ROOT.RooRealVar("Nbkg_total", "Number of background events for D+", 12000*scale*N_scale, 0*scale*N_scale,100000*scale*N_scale)
Acp_bkg = RooRealVar("Acp_bkg", "Acp", 0, -1, 1)  # A_Cp as a fit parameter
Nbkg_D_plus = RooFormulaVar("Nbkg_D_plus",
    "0.5 * Nbkg_total * (1 + Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))

Nbkg_D_minus = RooFormulaVar("Nbkg_D_minus",
    "0.5 * Nbkg_total * (1 - Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))

#if args.sign == "plus":
#    N_peak_bkg_total = ROOT.RooRealVar("N_peak_bkg_total", "Number of background events", 407.00289048147624)
#elif args.sign == "minus":
#    N_peak_bkg_total = ROOT.RooRealVar("N_peak_bkg_total", "Number of background events", 163.00227368775506)
#elif args.sign == "all":
#    N_peak_bkg_total = ROOT.RooRealVar("N_peak_bkg_total", "Number of background events", 569.9998807723211)
KDE_fit_result = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv12_bdt_train_Dp_CMS_p_{args.sign}_0.77_only_true_KDE_weighted.root")
KDE_result_object = ROOT.gDirectory.Get("jykim")
KDE_fit_result.Close()
KDE_fit_args = KDE_result_object.floatParsFinal()
N_peak_bkg_total_RooRealVar = KDE_fit_args.find("N_total")
N_peak_bkg_total = ROOT.RooRealVar("N_peak_bkg_total", "Number of background events",  0.25*1.221*N_peak_bkg_total_RooRealVar.getVal())
#N_peak_bkg_total = ROOT.RooRealVar("N_peak_bkg_total", "Number of background events", 0)
print("N_peak_bkg_total  =", N_peak_bkg_total)

#Acp_peak_bkg = RooRealVar("Acp_peak_bkg", "Acp", 0, -1, 1)  # A_Cp as a fit parameter
Acp_peak_bkg = RooRealVar("Acp_peak_bkg", "Acp", 0)  # A_Cp as a fit parameter
N_peak_bkg_D_plus = RooFormulaVar("N_peak_bkg_D_plus",
    "0.5 * N_peak_bkg_total * (1 + Acp_peak_bkg)",
    RooArgList(N_peak_bkg_total, Acp_peak_bkg))

N_peak_bkg_D_minus = RooFormulaVar("N_peak_bkg_D_minus",
    "0.5 * N_peak_bkg_total * (1 - Acp_peak_bkg)",
    RooArgList(N_peak_bkg_total, Acp_peak_bkg))

f_in = ROOT.TFile("/share/storage/jykim/plots/MC15rd/etaKp/pipipi/MC15re_6M_etapip_pipipi_Dp_M_v12_result_true_extended_train_Dp_CMS_p.0.77_workspace.root", "READ")
ws = f_in.Get("ws_kde")
kde_model = ws.pdf("model")
kde_model.SetName("kde_model")

f_sig = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/etaKp/pipipi/MC15re_6M_etapip_pipipi_K_Dp_M_v12_CB_conv_result_extended_train_Dp_CMS_p.0.77.root")
result_object_sig = ROOT.gDirectory.Get("jykim")
f_sig.Close()
#result_object_sig.Print("v")
fit_args_sig = result_object_sig.floatParsFinal()
#const_args_sig = result_object_sig.constPars()

f_sig_Ds = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/etaKp/pipipi/MC15rd_6M_etapip_pipipi_K_Dp_M_v12_CB_conv_result_extended_train_Dp_CMS_p_Ds.0.77.weighted.root")
result_object_sig_Ds = ROOT.gDirectory.Get("jykim")
f_sig_Ds.Close()
#result_object_sig_Ds.Print("v")
fit_args_sig_Ds = result_object_sig_Ds.floatParsFinal()

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

fit_sigma_gaussian = fit_args_sig.find("sigma_gaussian")
fit_Ds_sigma_gaussian = fit_args_sig_Ds.find("sigma_gaussian")



mean = ROOT.RooRealVar("mean", "mean", 1.87, 1.85, 1.89)
sigmaL = ROOT.RooRealVar("sigmaL", "sigma",  fit_sigmaL.getVal())
sigmaR = ROOT.RooRealVar("sigmaR", "sigma",  fit_sigmaR.getVal())
alphaL = ROOT.RooRealVar("alphaL", "alphaL", fit_alphaL.getVal())
nL = ROOT.RooRealVar("nL", "nL",  fit_nL.getVal())
alphaR = ROOT.RooRealVar("alphaR", "alphaR", fit_alphaR.getVal())
nR = ROOT.RooRealVar("nR", "nR", fit_nR.getVal())
sigma_gaussian = ROOT.RooRealVar("sigma_gaussian", "sigma of Gaussian",  fit_sigma_gaussian.getVal())


# Create double-sided Crystal Ball PDF
CB = ROOT.RooCrystalBall("CB", "CB_left", x, mean, sigmaL, sigmaR, alphaL, nL, alphaR, nR)

mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0)

scale_factor = ROOT.RooRealVar("scale_factor", "sigma of Gaussian", 1,0,2)
scaled_sigma_gaussian = RooFormulaVar("scaled_sigma_gaussian",
    "sigma_gaussian * scale_factor",
    RooArgList(sigma_gaussian, scale_factor))

gaussian = ROOT.RooGaussian("gaussian", "Gaussian PDF", x, mean_gaussian, scaled_sigma_gaussian)
sig_model = ROOT.RooFFTConvPdf("sig_model", "Convolution of Johnson and Gaussian", x, CB, gaussian)

Ds_mean = ROOT.RooRealVar("Ds_mean", "mean", 1.97, 1.95, 1.99)

Ds_sigmaL = ROOT.RooRealVar("Ds_sigmaL", "sigma", fit_Ds_sigmaL.getVal())
Ds_sigmaR = ROOT.RooRealVar("Ds_sigmaR", "sigma", fit_Ds_sigmaR.getVal())
Ds_alphaL = ROOT.RooRealVar("Ds_alphaL", "alphaL", fit_Ds_alphaL.getVal())
Ds_nL = ROOT.RooRealVar("Ds_nL", "nL", fit_Ds_nL.getVal() )
Ds_alphaR = ROOT.RooRealVar("Ds_alphaR", "alphaR", fit_Ds_alphaR.getVal() )
Ds_nR = ROOT.RooRealVar("Ds_nR", "nR", fit_Ds_nR.getVal())
Ds_sigma_gaussian = ROOT.RooRealVar("Ds_sigma_gaussian", "sigma of Gaussian", fit_Ds_sigma_gaussian.getVal())

# Create double-sided Crystal Ball PDF
Ds_CB = ROOT.RooCrystalBall("Ds_CB", "CB_left", x, Ds_mean, Ds_sigmaL,  Ds_sigmaR, Ds_alphaL, Ds_nL, Ds_alphaR, Ds_nR)

Ds_mean_gaussian = ROOT.RooRealVar("Ds_mean_gaussian", "mean of Gaussian", 0)

scaled_Ds_sigma_gaussian = RooFormulaVar("Ds_scaled_sigma_gaussian",
    "Ds_sigma_gaussian * scale_factor",
    RooArgList(Ds_sigma_gaussian, scale_factor))
# Create a Gaussian distribution
#Ds_gaussian = ROOT.RooGaussian("Ds_gaussian", "Gaussian PDF", x, Ds_mean_gaussian, Ds_sigma_gaussian)
Ds_gaussian = ROOT.RooGaussian("Ds_gaussian", "Gaussian PDF", x, Ds_mean_gaussian, scaled_Ds_sigma_gaussian)

# Convolute the Johnson distribution with Gaussian
Ds_model = ROOT.RooFFTConvPdf("Ds_model", "Convolution of Johnson and Gaussian", x, Ds_CB, Ds_gaussian)


x_bkg1_c1_plus = ROOT.RooRealVar("x_bkg1_c1_plus", "c1",0.1, -1.0, 1.0)
x_bkg1_c1_minus = ROOT.RooRealVar("x_bkg1_c1_minus", "c1",0.1, -1.0, 1.0)
x_bkg1_c2 = ROOT.RooRealVar("x_bkg1_c2", "c2",0.1, -1.0, 1.0)

model_bkg_plus = ROOT.RooChebychev("model_bkg_plus", "x_bkg1", x, ROOT.RooArgList(x_bkg1_c1_plus, x_bkg1_c2))
model_bkg_minus = ROOT.RooChebychev("model_bkg_minus", "x_bkg1", x, ROOT.RooArgList(x_bkg1_c1_minus, x_bkg1_c2))


# Define extended PDFs for D+ and D-
model_D_plus = ROOT.RooAddPdf("model_D_plus", "D+ model",
                              ROOT.RooArgList(sig_model, Ds_model, model_bkg_plus, kde_model),
                              ROOT.RooArgList(Nsig_D_plus, Nsig_Ds_plus, Nbkg_D_plus, N_peak_bkg_D_plus))
model_D_minus = ROOT.RooAddPdf("model_D_minus", "D- model",
                              ROOT.RooArgList(sig_model, Ds_model, model_bkg_minus, kde_model),
                              ROOT.RooArgList(Nsig_D_minus, Nsig_Ds_minus, Nbkg_D_minus, N_peak_bkg_D_minus))

# Create a category to distinguish between D+ and D-
cat = RooCategory("sample", "sample")
cat.defineType("D_plus")
cat.defineType("D_minus")

# Create a simultaneous PDF using the category
sim_model = RooSimultaneous("sim_model", "Simultaneous model", cat)
sim_model.addPdf(model_D_plus, "D_plus")
sim_model.addPdf(model_D_minus, "D_minus")

#data_combined = RooDataSet("data_combined", "Combined data", RooArgList(x, w_1), RooFit.Index(cat),
data_combined = RooDataSet("data_combined", "Combined data", full_var_set,RooFit.Index(cat),
                           RooFit.Import("D_plus", data),
                           RooFit.Import("D_minus", data_cc))

# Fit the model to the combined data
#fit_result = sim_model.fitTo(data_combined, RooFit.Save())
#fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4), RooFit.Strategy(2), RooFit.Minos(0), RooFit.Hesse(1))
#fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4), RooFit.Strategy(0), RooFit.Minos(0), RooFit.Hesse(1))
#fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(8), RooFit.Strategy(1))
#fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(8), RooFit.Strategy(2))
fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True),  ROOT.RooFit.NumCPU(8), RooFit.Strategy(2), ROOT.RooFit.Offset(True))
#fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(8), RooFit.Strategy(2), ROOT.RooFit.Offset(True))
#fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(8))

# Print fit results
fit_result.Print()

# Output the Acp value and its error
Acp_value = Acp.getVal()
Acp_error = Acp.getError()

print(f"Acp = {Acp_value:.3f} ± {Acp_error:.3f}")

# Output N_total
N_total_value = N_total.getVal()
N_total_error = N_total.getError()

print(f"N_total = {N_total_value:.0f} ± {N_total_error:.3f}")

def add_lumi_prelim(canvas, lumi_fb=428, is_preliminary=True):
    canvas.cd(1)
    pos_x = 0.78
    top_y = 0.90
    line_spacing = 0.05

    header = "#font[62]{Belle II}"
    if is_preliminary:
        left_text = f"#splitline{{{header}}}{{#font[52]{{Preliminary}}}}"
        lumi_y = top_y - (line_spacing * 2.2)
    else:
        left_text = header
        lumi_y = top_y - (line_spacing * 1.2)

    latex_left = ROOT.TLatex()
    latex_left.SetNDC(True)
    latex_left.SetTextSize(0.042)
    latex_left.SetTextAlign(13)
    latex_left.DrawLatex(pos_x, top_y, left_text)

    latex_right = ROOT.TLatex()
    latex_right.SetNDC(True)
    latex_right.SetTextSize(0.042)
    latex_right.SetTextAlign(13)
    latex_right.DrawLatex(pos_x, lumi_y, f"#int L dt = {lumi_fb} fb^{{-1}}")

    if not hasattr(canvas, "_labels"):
        canvas._labels = []
    canvas._labels.extend([latex_left, latex_right])

# Create plots for D+ and D-
canvas_D_plus = ROOT.TCanvas("canvas_D_plus", "D+ fit", 800, 600)
xlow = ctypes.c_double()
ylow = ctypes.c_double()
xup = ctypes.c_double()
yup = ctypes.c_double()
canvas_D_plus.GetPad(0).GetPadPar(xlow, ylow, xup, yup)
canvas_D_plus.Divide(1,2)

xlow = xlow.value
ylow = ylow.value
xup = xup.value
yup = yup.value

upPad = canvas_D_plus.GetPad(1)
upPad.SetPad(xlow, ylow+0.25*(yup-ylow),xup,yup)

dwPad = canvas_D_plus.GetPad(2)
dwPad.SetPad(xlow, ylow,xup,ylow+0.25*(yup-ylow))

canvas_D_plus.cd(1)
frame_D_plus = x.frame(ROOT.RooFit.Title("D+ fit"))
#simPdf.plotOn(frame1, Slice(sample, "plus"), Components("bkg"), ProjWData(sample, combData), LineStyle(kDashed));
#simPdf.plotOn(frame1, Slice(sample, "plus"), ProjWData(sample, combData));
slicedData_Dp = data_combined.reduce(Cut="sample==sample::D_plus")
slicedData_Dp.plotOn(frame_D_plus, Name="data")
sim_model.plotOn(
    frame_D_plus,
    Name="Combinatorial",
    Components="model_bkg_plus",
    ProjWData=(cat, slicedData_Dp),
    LineColor=ROOT.kGray,
    FillColor=ROOT.kGray,
    DrawOption="F",
    MoveToBack=True)
#sim_model.plotOn(frame_D_plus, Name="Background", Components="model_bkg", ProjWData=(cat, slicedData_Dp),LineColor=ROOT.kGreen+2)
sim_model.plotOn(frame_D_plus, Name="DpEtaPip", Components="kde_model", ProjWData=(cat, slicedData_Dp),LineColor=ROOT.kMagenta+1)
sim_model.plotOn(frame_D_plus, Name="Fitting",ProjWData=(cat, slicedData_Dp))
frame_D_plus.Draw("PE")
frame_D_plus.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.2, 0.65, 0.4, 0.90)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)
leg1.AddEntry("data", "#scale[1.33]{#font[42]{Data}}", "PE")
leg1.AddEntry("Fitting", "#scale[1.33]{#font[42]{Fit}}", "l")
leg1.AddEntry("DpEtaPip", "#scale[1.33]{#font[42]{D^{+} #rightarrow #eta #pi^{+}}}", "l")
leg1.AddEntry("Combinatorial", "#scale[1.33]{#font[42]{Combinatorial}}", "f")
leg1.SetBorderSize(0)
leg1.Draw()

hpull = frame_D_plus.pullHist()
hpull.SetFillStyle(1001)
hpull.SetFillColor(1);
for i in range(0,hpull.GetN()):#(int i=0;i<hpull.GetN();++i):
    hpull.SetPointError(i,0.0,0.0,0.0,0.0)
pullplot = x.frame()
pullplot.SetTitle("")
pullplot.addPlotable(hpull,"BE")
    # pullplot.addPlotable(hpull,"PE")

pullplot.SetYTitle("Pull")
pullplot.GetXaxis().SetTitleSize(0)
pullplot.GetYaxis().SetTitleSize(0.22)
pullplot.GetYaxis().CenterTitle(True)
pullplot.GetYaxis().SetTitleOffset(0.2)
pullplot.SetMinimum(-5.)
pullplot.SetMaximum(5.)
pullplot.GetXaxis().SetLabelSize(0.15)
pullplot.GetYaxis().SetLabelSize(0.105)
canvas_D_plus.cd(2)
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

canvas_D_plus.Update()
canvas_D_plus.SaveAs(file_name_Dp)

canvas_D_minus = ROOT.TCanvas("canvas_D_minus", "D- fit", 800, 600)
xlow = ctypes.c_double()
ylow = ctypes.c_double()
xup = ctypes.c_double()
yup = ctypes.c_double()
canvas_D_minus.GetPad(0).GetPadPar(xlow, ylow, xup, yup)
canvas_D_minus.Divide(1,2)

xlow = xlow.value
ylow = ylow.value
xup = xup.value
yup = yup.value

upPad = canvas_D_minus.GetPad(1)
upPad.SetPad(xlow, ylow+0.25*(yup-ylow),xup,yup)

dwPad = canvas_D_minus.GetPad(2)
dwPad.SetPad(xlow, ylow,xup,ylow+0.25*(yup-ylow))

plot_x_range = (1.75, 2.05)
canvas_D_minus.cd(1)
frame_D_minus = x.frame(ROOT.RooFit.Title("D+ fit"))
slicedData_Dm = data_combined.reduce(Cut="sample==sample::D_minus")
slicedData_Dm.plotOn(frame_D_minus, Name="data")
sim_model.plotOn(
    frame_D_minus,
    Name="Combinatorial",
    Components="model_bkg_minus",
    ProjWData=(cat, slicedData_Dm),
    LineColor=ROOT.kGray,
    FillColor=ROOT.kGray,
    DrawOption="F",
    MoveToBack=True)
#sim_model.plotOn(frame_D_minus, Name="Background", Components="model_bkg", ProjWData=(cat, slicedData_Dm),LineColor=ROOT.kGreen+2)
sim_model.plotOn(frame_D_minus, Name="DpEtaPip", Components="kde_model", ProjWData=(cat, slicedData_Dm),LineColor=ROOT.kMagenta+2)
sim_model.plotOn(frame_D_minus, Name="Fitting",ProjWData=(cat, slicedData_Dm))
frame_D_minus.Draw("PE")
frame_D_minus.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.2, 0.65, 0.4, 0.90)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)
leg1.AddEntry("data", "#scale[1.33]{#font[42]{Data}}", "PE")
leg1.AddEntry("Fitting", "#scale[1.33]{#font[42]{Fit}}", "l")
leg1.AddEntry("DpEtaPip", "#scale[1.33]{#font[42]{D^{+} #rightarrow #eta #pi^{+}}}", "l")
leg1.AddEntry("Combinatorial", "#scale[1.33]{#font[42]{Combinatorial}}", "f")
leg1.SetBorderSize(0)
leg1.Draw()

hpull = frame_D_minus.pullHist()
hpull.SetFillStyle(1001)
hpull.SetFillColor(1);
for i in range(0,hpull.GetN()):#(int i=0;i<hpull.GetN();++i):
    hpull.SetPointError(i,0.0,0.0,0.0,0.0)
pullplot = x.frame()
pullplot.SetTitle("")
pullplot.addPlotable(hpull,"BE")
    # pullplot.addPlotable(hpull,"PE")

pullplot.SetYTitle("Pull")
pullplot.GetXaxis().SetTitleSize(0)
pullplot.GetYaxis().SetTitleSize(0.22)
pullplot.GetYaxis().CenterTitle(True)
pullplot.GetYaxis().SetTitleOffset(0.2)
pullplot.SetMinimum(-5.)
pullplot.SetMaximum(5.)
pullplot.GetXaxis().SetLabelSize(0.15)
pullplot.GetYaxis().SetLabelSize(0.105)
canvas_D_minus.cd(2)
pullplot.Draw()

xmin1 = ctypes.c_double(fit_range[0])
xmax1 = ctypes.c_double(fit_range[1])
# xmin1 = ctypes.c_double(plot_x_range[0])
# xmax1 = ctypes.c_double(plot_x_range[1])
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

canvas_D_minus.Update()
canvas_D_minus.SaveAs(file_name_Dm)

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
sim_model.plotOn(
    frame_D_all,
    Name="Combinatorial",
    Components="model_bkg_plus,model_bkg_minus",
    ProjWData=(cat, data_combined),
    LineColor=ROOT.kGray,
    FillColor=ROOT.kGray,
    DrawOption="F",
    MoveToBack=True)
#sim_model.plotOn(frame_D_all, Name="Background", Components="model_bkg", ProjWData=(cat, data_combined),LineColor=ROOT.kGreen+2)
sim_model.plotOn(frame_D_all, Name="DpEtaPip", Components="kde_model", ProjWData=(cat, data_combined),LineColor=ROOT.kMagenta+1)
sim_model.plotOn(frame_D_all, Name="Fitting",ProjWData=(cat, data_combined))
frame_D_all.Draw("PE")
frame_D_all.GetXaxis().CenterTitle(True)
#frame_D_all.SetMaximum(600)

leg1 = ROOT.TLegend(0.2, 0.65, 0.4, 0.90)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)
leg1.AddEntry("data", "#scale[1.33]{#font[42]{Data}}", "PE")
leg1.AddEntry("Fitting", "#scale[1.33]{#font[42]{Fit}}", "l")
leg1.AddEntry("DpEtaPip", "#scale[1.33]{#font[42]{D^{+} #rightarrow #eta #pi^{+}}}", "l")
leg1.AddEntry("Combinatorial", "#scale[1.33]{#font[42]{Combinatorial}}", "f")
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
add_lumi_prelim(canvas_D_all, lumi_fb=428)
canvas_D_all.Update()
canvas_D_all.SaveAs(file_name_Dall)

f = ROOT.TFile(fitresult_name, "RECREATE")
fit_result.Write("jykim")
f.Close()

# Open a text file in write mode
with open(fitresult_text, "w") as f:

    # Print the full fit result to the file
    f.write("Full fit result summary:\n")
    fit_result.Print("v")  # Verbose print (prints more details)

    # Alternatively, write specific attributes to the file
    f.write("\nSpecific fit result details:\n")
    f.write(f"Status: {fit_result.status()}\n")
    f.write(f"Covariance quality: {fit_result.covQual()}\n")
    f.write(f"EDM (Estimated Distance to Minimum): {fit_result.edm()}\n")
    f.write(f"Min NLL: {fit_result.minNll()}\n")

    # Access and write parameter values and errors to the file
    f.write("\nFitted Parameters:\n")
    params = fit_result.floatParsFinal()  # This returns the final fitted parameters
    for i in range(params.getSize()):
        param = params[i]
        f.write(f"{param.GetName()} = {param.getVal()} ± {param.getError()}\n")

    # Retrieve the values and errors of N_total and Acp
    N_total_val = N_total.getVal()
    N_total_err = N_total.getError()

    Acp_val = Acp.getVal()
    Acp_err = Acp.getError()

    # Calculate Nsig_D_plus and its error
    Nsig_D_plus_val = 0.5 * N_total_val * (1 + Acp_val)
    Nsig_D_plus_err = 0.5 * ((1 + Acp_val) * N_total_err + N_total_val * Acp_err)

    # Calculate Nsig_D_minus and its error
    Nsig_D_minus_val = 0.5 * N_total_val * (1 - Acp_val)
    Nsig_D_minus_err = 0.5 * ((1 - Acp_val) * N_total_err + N_total_val * Acp_err)

    # Retrieve the values and errors of N_total and Acp
    N_total_Ds_val = N_total_Ds.getVal()
    N_total_Ds_err = N_total_Ds.getError()

    Acp_Ds_val = Acp_Ds.getVal()
    Acp_Ds_err = Acp_Ds.getError()

    # Calculate Nsig_D_plus and its error
    Nsig_Ds_plus_val = 0.5 * N_total_Ds_val * (1 + Acp_Ds_val)
    Nsig_Ds_plus_err = 0.5 * ((1 + Acp_Ds_val) * N_total_Ds_err + N_total_Ds_val * Acp_Ds_err)

    # Calculate Nsig_D_minus and its error
    Nsig_Ds_minus_val = 0.5 * N_total_Ds_val * (1 - Acp_Ds_val)
    Nsig_Ds_minus_err = 0.5 * ((1 - Acp_Ds_val) * N_total_Ds_err + N_total_Ds_val * Acp_Ds_err)

    # Print the results
    f.write(f"Nsig_D_plus: Value = {Nsig_D_plus_val}, Error = {Nsig_D_plus_err}\n")
    f.write(f"Nsig_D_minus: Value = {Nsig_D_minus_val}, Error = {Nsig_D_minus_err}\n")


    f.write(f"Nsig_Ds_plus: Value = {Nsig_Ds_plus_val}, Error = {Nsig_Ds_plus_err}\n")
    f.write(f"Nsig_Ds_minus: Value = {Nsig_Ds_minus_val}, Error = {Nsig_Ds_minus_err}\n")

    # Optionally print a completion message
    f.write("\nFit result saved successfully.\n")

# The file is automatically closed after the 'with' block


# mcstudy1 = ROOT.RooMCStudy(sim_model, ROOT.RooArgSet(x), ROOT.RooFit.Extended(True),
#                             ROOT.RooFit.Binned(False), ROOT.RooFit.Silence(),
#                             ROOT.RooFit.FitOptions(ROOT.RooFit.Save(True),
#                                                    ROOT.RooFit.PrintEvalErrors(0),
#                                                    ROOT.RooFit.PrintLevel(-1)))

# # Generate and fit 10 toys
# mcstudy1.generateAndFit(10)
