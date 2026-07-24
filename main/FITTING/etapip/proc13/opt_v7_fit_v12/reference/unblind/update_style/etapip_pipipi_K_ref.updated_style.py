import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory, RooStats, TFile
from ROOT.RooFit import Extended, FitOptions, Save, PrintEvalErrors, PrintLevel, Bins, FitGauss,    NumCPU, Strategy, Offset
import glob
import ctypes
import os
import argparse
import random

parser = argparse.ArgumentParser(description="Process Dp_CMS_sign argument")
parser.add_argument("-s","--sign", choices=["plus", "minus","all"], required=True,
                    help="Specify 'plus' or 'minus'")
parser.add_argument("-t","--train", required=True,
                    help="Specify train version")
#parser.add_argument("-b","--bdt", required=True,
#                    help="Specify BDT value")

args = parser.parse_args()
print(f"Dp_CMS_sign is set to: {args.sign}")


#BDT_cut = args.bdt
BDT_cut = "0.77"

if args.sign == "plus":
	Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>0"
	N_scale = 0.64
elif args.sign == "minus":
	Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta<0"
	N_scale = 0.43
elif args.sign == "all":
	Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>-10"
	N_scale = 1

suffix = "sumw2fixed_unblind_updated_style"
file_name_Dall = f"/share/storage/jykim/plots/proc_all/etapip/pipipi/generic/proc13_etapip_pipipi_ref_fit_opt_loose_v7_fitv12_bdt_{args.train}_Dall_CMS_{args.sign}_{BDT_cut}_{suffix}.pdf"
fitresult_name = f"/share/storage/jykim/plots/proc_all/etapip/pipipi/generic/fitresult/proc13_etapip_pipipi_ref_fit_opt_loose_v7_fitv12_bdt_{args.train}_{args.sign}_{BDT_cut}_{suffix}.root"
fitresult_text = f"/share/storage/jykim/plots/proc_all/etapip/pipipi/generic/fitresult/proc13_etapip_pipipi_ref_fit_opt_loose_v7_fitv12_bdt_{args.train}_{args.sign}_{BDT_cut}_{suffix}.txt"

dir_path = os.path.dirname(fitresult_name)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/proc13/proc13_EtaHp_loose_v7"
cm_elements = ["jae_13_had_4S_off_v1", "jae_13_had_4S_v3", "jae_23_had_4S_off_v1", "jae_23_had_4S_v1", \
               "jae_23_had_5Sscan_10657_v1", "jae_23_had_5Sscan_10706_v1", "jae_23_had_5Sscan_10751_v1", "jae_23_had_5Sscan_10810_v1"]

tree_name = "etapip_pipipi"
file_list = []
for element in cm_elements:
    pattern = f"{base_path}/{element}/{tree_name}/ref/{BDT_cut}/*BDT.root"
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
#fit_range = (1.75, 2.06)
#fit_range = (1.755, 2.045)
truth_var = "Dp_isSignal"
charge_var = "Pip_charge"

cuts_Dp = charge_var + "==1 && rank_Dp_chiProb==1"
cuts_Dm = charge_var + "==-1 && rank_Dp_chiProb==1"

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
ds_weight = ROOT.RooRealVar("ds_weight", "ds_weight", 1)
rank_Dp_chiProb = ROOT.RooRealVar("rank_Dp_chiProb", "rank_Dp_chiProb", 0, 1000)

full_var_set = ROOT.RooArgSet(x, Pip_charge, Dp_CMS_cosTheta, BDT, Pip_dr, Dp_dz,
                              Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane,
                              Dp_cosHelicityAngleMomentum,
                              Dp_CMS_p, rank_Dp_chiProb)

#before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,Pip_charge,Dp_CMS_cosTheta), cuts_Dp)
data = ROOT.RooDataSet("data", "", mychain, full_var_set, cuts_Dp)
#before_data = ROOT.RooDataSet("data", "", mychain, full_var_set, cuts_Dp)

#w_1 = ROOT.RooRealVar('w_1', 'w', 0,1)
#scale = 427.87/1000
#scale = 1/4
#scale = (1/4)*(427.87+54.3)/427.87
#w_1.setVal(scale)
#before_data.addColumn(w_1)
#data = ROOT.RooDataSet(before_data.GetName(), before_data.GetTitle(),before_data, before_data.get(), '' ,  'w_1')


scale = 1/4
data_scale = 1
#w_scaled = ROOT.RooFormulaVar("w_scaled", "Scaled Weight", f"{data_scale}*ds_weight", ROOT.RooArgList(ds_weight))
#before_data.addColumn(w_scaled)

#data = ROOT.RooDataSet("data_weighted", "Weighted Data", before_data, before_data.get(), "", "w_scaled")
Num_total = data.sumEntries()
print(Num_total)

mychain_cc = ROOT.TChain(tree_name)
for i in file_list:
    mychain_cc.Add(i)
#before_data_cc = ROOT.RooDataSet("data","", mychain_cc, ROOT.RooArgSet(x,Pip_charge,Dp_CMS_cosTheta), cuts_Dm)
#before_data_cc.addColumn(w_1)
#data_cc = ROOT.RooDataSet(before_data_cc.GetName(), before_data_cc.GetTitle(),before_data_cc, before_data_cc.get(), '' ,  'w_1')

data_cc = ROOT.RooDataSet("data", "", mychain_cc, full_var_set, cuts_Dm)
#before_data_cc = ROOT.RooDataSet("data", "", mychain_cc, full_var_set, cuts_Dm)
#before_data_cc.addColumn(w_scaled)
#data_cc = ROOT.RooDataSet("data_weighted_cc", "Weighted Data", before_data_cc, before_data_cc.get(), "", "w_scaled")

#data.append(data_cc)
Num_total_cc = data_cc.sumEntries()
print(Num_total_cc)

N_total = RooRealVar("N_total", "N_total (N_D+ + N_D-)", 60000*scale*N_scale,  30000*scale*N_scale, 300000*scale*N_scale)  # N_total = N_D+ + N_D-
Acp = RooRealVar("Acp", "Acp", 0, -1, 1)

# Use Acp and N_total to define the expected signal yields for D+ and D-
Nsig_D_plus = RooFormulaVar("Nsig_D_plus",
    "0.5 * N_total * (1 + Acp)",
    RooArgList(N_total, Acp))

Nsig_D_minus = RooFormulaVar("Nsig_D_minus",
    "0.5 * N_total * (1 - Acp)",
    RooArgList(N_total, Acp))

N_total_Ds = RooRealVar("N_total_Ds", "N_total (N_Ds+ + N_Ds-)", 120000*scale*N_scale,  50000*scale*N_scale,700000*scale*N_scale)  # N_total = N_D+ + N_D-
Acp_Ds = RooRealVar("Acp_Ds", "Acp", 0, -1, 1)

# Use Acp and N_total to define the expected signal yields for D+ and D-
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


f_sig = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/etaKp/pipipi/MC15rd_6M_etapip_pipipi_K_ref_Dp_M_v12_CB_conv_result_extended_train_Dp_CMS_p.0.77.root")
result_object_sig = ROOT.gDirectory.Get("jykim")
f_sig.Close()
#result_object_sig.Print("v")
fit_args_sig = result_object_sig.floatParsFinal()
#const_args_sig = result_object_sig.constPars()

f_sig_Ds = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/etapip/pipipi/MC15rd_6M_etapip_pipipi_ref_Dp_M_v12_CB_conv_result_extended_train_Dp_CMS_p_Ds_p.0.77.Ds_weighted.root")
result_object_sig_Ds = ROOT.gDirectory.Get("jykim")
f_sig_Ds.Close()
#result_object_sig_Ds.Print("v")
fit_args_sig_Ds = result_object_sig_Ds.floatParsFinal()

f_rhopeta = ROOT.TFile.Open(f"/share/storage/jykim/plots/MC15rd/etapip/pipipi/MC15rd_etapip_pipipi_Dp_M_fit_v12_novo_result_rhopeta_Dp_CMS_p_0.72.root")
result_object_rhopeta = ROOT.gDirectory.Get("jykim")
f_rhopeta.Close()
fit_args_rhopeta = result_object_rhopeta.floatParsFinal()

fit_novo_sigma = fit_args_rhopeta.find("sigma")
fit_novo_tail = fit_args_rhopeta.find("tail")

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
sigma_gaussian = ROOT.RooRealVar("sigma_gaussian", "sigma of Gaussian",  fit_sigma_gaussian.getVal(),  0.001, 0.1 )

# Create double-sided Crystal Ball PDF
CB = ROOT.RooCrystalBall("CB", "CB_left", x, mean, sigmaL, sigmaR, alphaL, nL, alphaR, nR)

mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0)

gaussian = ROOT.RooGaussian("gaussian", "Gaussian PDF", x, mean_gaussian, sigma_gaussian)
sig_model = ROOT.RooFFTConvPdf("sig_model", "Convolution of Johnson and Gaussian", x, CB, gaussian)

Ds_mean = ROOT.RooRealVar("Ds_mean", "mean", 1.97, 1.95, 1.99)

Ds_sigmaL = ROOT.RooRealVar("Ds_sigmaL", "sigma", fit_Ds_sigmaL.getVal())
Ds_sigmaR = ROOT.RooRealVar("Ds_sigmaR", "sigma", fit_Ds_sigmaR.getVal())
Ds_alphaL = ROOT.RooRealVar("Ds_alphaL", "alphaL", fit_Ds_alphaL.getVal())
Ds_nL = ROOT.RooRealVar("Ds_nL", "nL", fit_Ds_nL.getVal() )
Ds_alphaR = ROOT.RooRealVar("Ds_alphaR", "alphaR", fit_Ds_alphaR.getVal() )
Ds_nR = ROOT.RooRealVar("Ds_nR", "nR", fit_Ds_nR.getVal())
Ds_sigma_gaussian = ROOT.RooRealVar("Ds_sigma_gaussian", "sigma of Gaussian", fit_Ds_sigma_gaussian.getVal(),  0.001, 0.1 )

# Create double-sided Crystal Ball PDF
Ds_CB = ROOT.RooCrystalBall("Ds_CB", "CB_left", x, Ds_mean, Ds_sigmaL, Ds_sigmaR,  Ds_alphaL, Ds_nL, Ds_alphaR, Ds_nR)

Ds_mean_gaussian = ROOT.RooRealVar("Ds_mean_gaussian", "mean of Gaussian", 0)

# Create a Gaussian distribution
Ds_gaussian = ROOT.RooGaussian("Ds_gaussian", "Gaussian PDF", x, Ds_mean_gaussian, Ds_sigma_gaussian)

# Convolute the Johnson distribution with Gaussian
Ds_model = ROOT.RooFFTConvPdf("Ds_model", "Convolution of Johnson and Gaussian", x, Ds_CB, Ds_gaussian)


novo_mean = ROOT.RooRealVar("novo_mean", "Mean",  1.73, 1.71,1.745)
novo_sigma = ROOT.RooRealVar("novo_sigma", "Sigma", fit_novo_sigma.getVal())
novo_tail = ROOT.RooRealVar("novo_tail", "Tail", fit_novo_tail.getVal())
rhopeta  = ROOT.RooNovosibirsk("rhopeta", "Novosibirsk PDF", x, novo_mean, novo_sigma, novo_tail)


x_bkg1_Cheby_c0 = ROOT.RooRealVar("x_bkg1_Cheby_c0", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c1 = ROOT.RooRealVar("x_bkg1_Cheby_c1", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c2 = ROOT.RooRealVar("x_bkg1_Cheby_c2", "c0",0.0, -1.0, 1.0)
x_bkg1_tau = ROOT.RooRealVar("x_bkg1_tau", "c0",-3, -8, -0.01)


bkg_comb = ROOT.RooExponential("bkg_comb", "x_bkg1", x, x_bkg1_tau)
#model_bkg = ROOT.RooPolynomial("model_bkg", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1, x_bkg1_Cheby_c2))

bkg_frac = ROOT.RooRealVar("bkg_frac", "fraction of Gaussian in BKG", 0.3, 0.01, 1)

model_bkg = ROOT.RooAddPdf("model_bkg", "Gaus + Exp", RooArgList(rhopeta, bkg_comb), bkg_frac)


# Define extended PDFs for D+ and D-
model_D_plus = ROOT.RooAddPdf("model_D_plus", "D+ model",
                              ROOT.RooArgList(sig_model, Ds_model, model_bkg),
                              ROOT.RooArgList(Nsig_D_plus, Nsig_Ds_plus, Nbkg_D_plus))
model_D_minus = ROOT.RooAddPdf("model_D_minus", "D- model",
                              ROOT.RooArgList(sig_model, Ds_model, model_bkg),
                              ROOT.RooArgList(Nsig_D_minus, Nsig_Ds_minus, Nbkg_D_minus))

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
fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), ROOT.RooFit.NumCPU(8), RooFit.Strategy(1), ROOT.RooFit.Offset(True))

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

    # 1. Define vertical start and spacing
    pos_x = 0.79
    top_y = 0.90
    line_spacing = 0.05  # Adjust this to change the gap between lines

    header = "#font[42]{Belle II}"
    if is_preliminary:
        left_text = f"#splitline{{{header}}}{{#font[42]{{Preliminary}}}}"
        # Push the luminosity further down if splitline is used
        lumi_y = top_y - (line_spacing * 2.2)
    else:
        left_text = header
        # Bring the luminosity closer if it's just a single line
        lumi_y = top_y - (line_spacing * 1.2)

    # 2. Draw Belle II [Preliminary]
    latex_left = ROOT.TLatex()
    latex_left.SetNDC(True)
    latex_left.SetTextFont(TEXT_FONT)
    latex_left.SetTextSize(FONT_SIZE_UP)
    latex_left.SetTextAlign(13)
    latex_left.DrawLatex(pos_x, top_y, left_text)

    # 3. Draw Luminosity with dynamic Y-coordinate
    latex_right = ROOT.TLatex()
    latex_right.SetNDC(True)
    latex_right.SetTextFont(TEXT_FONT)
    latex_right.SetTextSize(FONT_SIZE_UP)
    latex_right.SetTextAlign(13)
    latex_right.DrawLatex(pos_x, lumi_y, f"{lumi_fb} fb^{{-1}}")

    if not hasattr(canvas, "_labels"):
        canvas._labels = []
    canvas._labels.extend([latex_left, latex_right])


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
upPad.SetBottomMargin(0.146)

dwPad = canvas_D_all.GetPad(2)
dwPad.SetPad(xlow, ylow,xup,ylow+0.25*(yup-ylow))

# Match the font and relative sizes used in signAvg.
TEXT_FONT = 42
FONT_SIZE_UP = 0.053
up_height = yup - (ylow + 0.25 * (yup - ylow))
dw_height = (ylow + 0.25 * (yup - ylow)) - ylow
FONT_SIZE_DW = FONT_SIZE_UP * up_height / dw_height

plot_bins = 200
bin_width = (fit_range[1] - fit_range[0]) / plot_bins

canvas_D_all.cd(1)

frame_D_all = x.frame(ROOT.RooFit.Title(""))
frame_D_all.SetTitle("")
frame_D_all = x.frame(ROOT.RooFit.Title(""))
frame_D_all.SetTitle("")
frame_D_all.GetXaxis().SetTitle("M(#eta_{3#pi}#pi^{+}) [GeV/c^{2}]")
frame_D_all.GetYaxis().SetTitle(
    f"Candidates per {1000.0 * bin_width:.2f} MeV/c^{{2}}"
)

data_combined.plotOn(
    frame_D_all,
    ROOT.RooFit.Binning(plot_bins),
    Name="data",
    MarkerStyle=20,
    MarkerSize=0.8,
)
sim_model.plotOn(
    frame_D_all,
    Name="COMB",
    Components="bkg_comb",
    ProjWData=(cat, data_combined),
    LineColor=ROOT.kGray,
    FillColor=ROOT.kGray,
    DrawOption="F",
    MoveToBack=True)
sim_model.plotOn(
    frame_D_all,
    Name="RHOETA",
    Components="rhopeta",
    ProjWData=(cat, data_combined),
    LineColor=ROOT.kOrange+4,
    FillColor=ROOT.kOrange+4,
    DrawOption="F",
    AddTo="COMB",
    MoveToBack=True)

sim_model.plotOn(
    frame_D_all,
    Name="Fitting",
    ProjWData=(cat, data_combined),
    LineColor=ROOT.kBlue,
    LineWidth=2,
)

for axis in [frame_D_all.GetXaxis(), frame_D_all.GetYaxis()]:
    axis.SetTitleFont(TEXT_FONT)
    axis.SetLabelFont(TEXT_FONT)
    axis.SetTitleSize(FONT_SIZE_UP)
    axis.SetLabelSize(FONT_SIZE_UP)
    axis.CenterTitle(True)

frame_D_all.GetXaxis().SetTitleOffset(1.3)
frame_D_all.GetYaxis().SetTitleOffset(1.35)

# Set the y range only after all data/model objects have been added.
# Calling GetMaximum() before plotOn/Draw can lead to a spurious 0--1 range.
max_y = frame_D_all.GetMaximum()
if max_y > 0.0:
    frame_D_all.SetMaximum(1.3 * max_y)
frame_D_all.SetMinimum(0.0)

frame_D_all.Draw("PE")

leg1 = ROOT.TLegend(0.2, 0.65, 0.4, 0.90)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)
leg1.SetBorderSize(0)
leg1.SetTextFont(TEXT_FONT)
leg1.SetTextSize(FONT_SIZE_UP)
leg1.AddEntry("data", "#font[42]{Data}", "PE")
leg1.AddEntry("Fitting", "#font[42]{Fit}", "l")
leg1.AddEntry("RHOETA", "#font[42]{D_{s}^{+} #rightarrow #rho^{+} #eta}", "f")
leg1.AddEntry("COMB", "#font[42]{Combinatorial}", "f")
leg1.Draw()
upPad.RedrawAxis()

hpull = frame_D_all.pullHist("data", "Fitting")
hpull.SetFillStyle(1001)
hpull.SetFillColor(ROOT.kBlack)
for i in range(hpull.GetN()):
    hpull.SetPointError(i, 0.0, 0.0, 0.0, 0.0)
pullplot = x.frame()
pullplot.SetTitle("")
pullplot.addPlotable(hpull,"BE")
pullplot.SetYTitle("Pull")
pullplot.SetMinimum(-5.0)
pullplot.SetMaximum(5.0)
for axis in [pullplot.GetXaxis(), pullplot.GetYaxis()]:
    axis.SetTitleFont(TEXT_FONT)
    axis.SetLabelFont(TEXT_FONT)
    axis.SetTitleSize(FONT_SIZE_DW)
    axis.SetLabelSize(FONT_SIZE_DW)
    axis.CenterTitle(True)


pullplot.GetXaxis().SetTitleSize(0)
pullplot.GetXaxis().SetLabelSize(0)
pullplot.GetYaxis().SetTitleOffset(0.43)
pullplot.SetMinimum(-5)
pullplot.SetMaximum(5)
pullplot.GetYaxis().SetNdivisions(2, 5, 0, False)

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

dwPad.RedrawAxis()
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
    #fit_result.Print("v")  # Verbose print (prints more details)

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
