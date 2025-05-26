import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory, TFile, RooArgSet, RooStats
from ROOT.RooFit import Extended, FitOptions, Save, PrintEvalErrors, PrintLevel, Bins, FitGauss,    NumCPU, Strategy, Offset
import glob
import ctypes
import os
import argparse

parser = argparse.ArgumentParser(description="Process Dp_CMS_sign argument")
parser.add_argument("-s","--sign", choices=["plus", "minus","all"], required=True,
                    help="Specify 'plus' or 'minus'")
parser.add_argument("-t","--train", required=True,
                    help="Specify train version")

args = parser.parse_args()
print(f"Dp_CMS_sign is set to: {args.sign}")

if args.sign == "plus":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>0"
    CMS_scale = 9/14
elif args.sign == "minus":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta<0"
    CMS_scale = 6/14
elif args.sign == "all":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>-10"
    CMS_scale = 1

suffix = "no_bdt_new_Ds_correct"
file_name_Dp = f"/share/storage/jykim/plots/proc13/Kspip/gg/generic/proc13_Kspip_gg_fit_opt_loose_v7_fitv1_Dp_{args.train}_Dp_CMS_{args.sign}_{suffix}.png"
file_name_Dm = f"/share/storage/jykim/plots/proc13/Kspip/gg/generic/proc13_Kspip_gg_fit_opt_loose_v7_fitv1_Dm_{args.train}_Dp_CMS_{args.sign}_{suffix}.png"
file_name_Dall = f"/share/storage/jykim/plots/proc13/Kspip/gg/generic/proc13_Kspip_gg_fit_opt_loose_v7_fitv1_Dall_{args.train}_Dp_CMS_{args.sign}_{suffix}.png"
fitresult_name = f"/share/storage/jykim/plots/proc13/Kspip/gg/generic/fitresult/proc13_1ab_Kspip_gg_fit_opt_loose_v7_fitv1_{args.train}_Dp_CMS_{args.sign}_{suffix}.root"
fitresult_text = f"/share/storage/jykim/plots/proc13/Kspip/gg/generic/fitresult/proc13_1ab_Kspip_gg_fit_opt_loose_v7_fitv1_{args.train}_Dp_CMS_{args.sign}_{suffix}.txt"
file_sweight = f"/share/storage/jykim/sweight/proc13/Kspip/gg/proc13_Kspip_gg_fit_opt_loose_v7_fitv1_Dp_{suffix}.root"

dir_path = os.path.dirname(file_name_Dp)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)
dir_path = os.path.dirname(fitresult_name)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)
dir_path = os.path.dirname(file_sweight)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/proc13/proc13_Kspip_loose_v7_250228_v3"
cm_elements = ["Kshp_13_had_4S_off_v1", "Kshp_13_had_4S_v3", "Kshp_23_had_4S_off_v1", "Kshp_23_had_4S_v1", "Kshp_23_had_5Sscan_10657_v1", "Kshp_23_had_5Sscan_10706_v1", "Kshp_23_had_5Sscan_10751_v1", "Kshp_23_had_5Sscan_10810_v1"]
#cm_elements = ["Kshp_13_had_4S_off_v1", "Kshp_13_had_4S_v3"]

ref_tree = "etapip_gg"
file_list = []
tree_name = "Ks"
for element in cm_elements:
    #pattern = f"{base_path}/{element}/{ref_tree}/{tree_name}/*.BCS.root"
    pattern = f"{base_path}/{element}/{ref_tree}/{tree_name}/no_bdt/*.BCS.root"
    file_list += glob.glob(pattern)
print(file_list)
print(f"Number of files: {len(file_list)}")

mychain = ROOT.TChain(tree_name)
for i in file_list:
    mychain.Add(i)

# Define variable and its range
fit_variable = "Dp_M"
fit_var_name = "M(K^{0}_{S}#pi^{+}) [GeV/c^{2}]"
#fit_range = (1.66, 2.06)
fit_range = (1.7, 2.06)
fit_range = (1.82, 1.92)
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
BDT = ROOT.RooRealVar("BDT", "BDT", 0, 1)
Pip_dr = ROOT.RooRealVar("Pip_dr", "Pip_dr", -10000, 10000)
Dp_dz = ROOT.RooRealVar("Dp_dz", "Dp_dz", -10000, 10000)
Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane = ROOT.RooRealVar("Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane", "Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane'", -1,1)
etapip_Eta_Easym = ROOT.RooRealVar("etapip_Eta_Easym", "etapip_Eta_Easym", 0, 1)
Dp_cosHelicityAngleMomentum = ROOT.RooRealVar("Dp_cosHelicityAngleMomentum", "Dp_cosHelicityAngleMomentum", -1, 1)
Dp_CMS_p = ROOT.RooRealVar("Dp_CMS_p", "Dp_CMS_p", 0, 100)

before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,Pip_charge, Dp_CMS_cosTheta, BDT, Pip_dr, Dp_dz, Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane, etapip_Eta_Easym, Dp_cosHelicityAngleMomentum, Dp_CMS_p), cuts_Dp)

w_1 = ROOT.RooRealVar('w_1', 'w', 0,1)
#scale = 1
#scale = 427.87/1000
scale = 1/4
w_1.setVal(1)
before_data.addColumn(w_1)
data = ROOT.RooDataSet(before_data.GetName(), before_data.GetTitle(),before_data, before_data.get(), '' ,  'w_1')
Num_total = data.sumEntries()
print(Num_total)

mychain_cc = ROOT.TChain(tree_name)
for i in file_list:
    mychain_cc.Add(i)
before_data_cc = ROOT.RooDataSet("data","", mychain_cc, ROOT.RooArgSet(x,Pip_charge, Dp_CMS_cosTheta, BDT, Pip_dr, Dp_dz, Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane, etapip_Eta_Easym, Dp_cosHelicityAngleMomentum, Dp_CMS_p), cuts_Dm)
before_data_cc.addColumn(w_1)
data_cc = ROOT.RooDataSet(before_data_cc.GetName(), before_data_cc.GetTitle(),before_data_cc, before_data_cc.get(), '' ,  'w_1')

#data.append(data_cc)
Num_total_cc = data_cc.sumEntries()
print(Num_total_cc)

N_total = RooRealVar("N_total", "N_total (N_D+ + N_D-)", 6000000*scale*CMS_scale, 500000*scale*CMS_scale, 20000000*scale*CMS_scale)  # N_total = N_D+ + N_D-
Acp = RooRealVar("Acp", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

# Use Acp and N_total to define the expected signal yields for D+ and D-
Nsig_D_plus = RooFormulaVar("Nsig_D_plus",
    "0.5 * N_total * (1 + Acp)",
    RooArgList(N_total, Acp))

Nsig_D_minus = RooFormulaVar("Nsig_D_minus",
    "0.5 * N_total * (1 - Acp)",
    RooArgList(N_total, Acp))

Nbkg_total = ROOT.RooRealVar("Nbkg_total", "Number of background events for D+", 5000000*scale*CMS_scale,50000*scale*CMS_scale,10000000*scale*CMS_scale)
Acp_bkg = RooRealVar("Acp_bkg", "Acp", 0, -1, 1)  # A_Cp as a fit parameter
Nbkg_D_plus = RooFormulaVar("Nbkg_D_plus",
    "0.5 * Nbkg_total * (1 + Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))

Nbkg_D_minus = RooFormulaVar("Nbkg_D_minus",
    "0.5 * Nbkg_total * (1 - Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))

mean = ROOT.RooRealVar("mean", "mean", 1.86, 1.84, 1.88)  # Central value
sigma = ROOT.RooRealVar("sigma", "sigma", 0.002, 0.0001, 0.01)  # Width parameter
gamma = ROOT.RooRealVar("gamma", "gamma", 0.01, -2.0, 2.0)  # Skewness parameter
delta = ROOT.RooRealVar("delta", "delta", 0.6, 0.001, 3.0)  # Shape parameter

# Create the RooJohnson PDF
johnson = ROOT.RooJohnson("johnson", "double-sided Crystal Ball using Johnson SU", x, mean, sigma, gamma, delta)

mean_gauss = ROOT.RooRealVar("mean_gauss", "Gaussian mean", 0.0)  # Convolution will center the Gaussian at zero
sigma_gauss = ROOT.RooRealVar("sigma_gauss", "Gaussian width", 0.002, 0.00001, 0.01)

# Create the Gaussian PDF
gauss = ROOT.RooGaussian("gauss", "Gaussian PDF", x, mean_gauss, sigma_gauss)

# Perform the convolution
sig_model = ROOT.RooFFTConvPdf("sig_model", "Convolution of Johnson SU and Gaussian", x, johnson, gauss)


x_bkg1_Cheby_c0 = ROOT.RooRealVar("x_bkg1_Cheby_c0", "c0",0.1, -1.0, 1.0)
x_bkg1_Cheby_c1 = ROOT.RooRealVar("x_bkg1_Cheby_c1", "c0",0.2, -1.0, 1.0)
x_bkg1_Cheby_c2 = ROOT.RooRealVar("x_bkg1_Cheby_c2", "c0",0.3, -1.0, 1.0)
x_bkg1_tau = ROOT.RooRealVar("x_bkg1_tau", "c0",-0.5, -20, 20)

#bkg_comb = ROOT.RooExponential("bkg_comb", "x_bkg1", x, x_bkg1_tau)
model_bkg = ROOT.RooExponential("model_bkg", "x_bkg1", x, x_bkg1_tau)
#model_bkg = ROOT.RooPolynomial("model_bkg", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1, x_bkg1_Cheby_c2))
#bkg_comb = ROOT.RooPolynomial("bkg_comb", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1))
#model_bkg = ROOT.RooPolynomial("model_bkg", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1))
#model_bkg = ROOT.RooPolynomial("model_bkg", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0))

#bkg_frac = ROOT.RooRealVar("bkg_frac", "fraction of Gaussian in BKG", 0.3, 0.0, 1.0)

#model_bkg = ROOT.RooAddPdf("model_bkg", "Gaus + Exp", RooArgList(retrieved_pdf, bkg_comb), bkg_frac)




# Define extended PDFs for D+ and D-
model_D_plus = ROOT.RooAddPdf("model_D_plus", "D+ model",
                              ROOT.RooArgList(sig_model,  model_bkg),
                              ROOT.RooArgList(Nsig_D_plus,  Nbkg_D_plus))
model_D_minus = ROOT.RooAddPdf("model_D_minus", "D- model",
                              ROOT.RooArgList(sig_model,  model_bkg),
                              ROOT.RooArgList(Nsig_D_minus,  Nbkg_D_minus))

# Create a category to distinguish between D+ and D-
cat = RooCategory("sample", "sample")
cat.defineType("D_plus")
cat.defineType("D_minus")

# Create a simultaneous PDF using the category
sim_model = RooSimultaneous("sim_model", "Simultaneous model", cat)
sim_model.addPdf(model_D_plus, "D_plus")
sim_model.addPdf(model_D_minus, "D_minus")

data_combined = RooDataSet("data_combined", "Combined data", RooArgList(x, w_1, BDT, Pip_dr, Dp_dz, Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane, etapip_Eta_Easym, Dp_cosHelicityAngleMomentum, Dp_CMS_p), RooFit.Index(cat),
                           RooFit.Import("D_plus", data),
                           RooFit.Import("D_minus", data_cc),
                           RooFit.WeightVar('w_1'))

# Fit the model to the combined data
#fit_result = sim_model.fitTo(data_combined, RooFit.Save())
#fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4), RooFit.Strategy(2), RooFit.Minos(0), RooFit.Hesse(1))
#fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4), RooFit.Strategy(0), RooFit.Minos(0), RooFit.Hesse(1))
nll = sim_model.createNLL(data_combined, ROOT.RooFit.Extended(True), ROOT.RooFit.NumCPU(15), RooFit.SumW2Error(True),  ROOT.RooFit.Offset("initial"))

# Step 2: Perform the Migrad minimization
minimizer = ROOT.RooMinimizer(nll)
minimizer.setStrategy(2)
#minimizer.setStrategy(0)
minimizer.setPrintLevel(1)
status = minimizer.migrad()

# Check the status of Migrad
if status != 0:
    print(f"Migrad failed with status: {status}")

# Step 3: Perform the Hesse minimization
status = minimizer.hesse()

# Check the status of Hesse
if status != 0:
    print(f"Hesse failed with status: {status}")

# Save the fit result
fit_result  = minimizer.save()
#r.Print("v")

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
frame_D_plus.GetXaxis().SetTitle("M(K_{S}^{0}#pi^{+}) [GeV/c^{2}]")
#simPdf.plotOn(frame1, Slice(sample, "plus"), Components("bkg"), ProjWData(sample, combData), LineStyle(kDashed));
#simPdf.plotOn(frame1, Slice(sample, "plus"), ProjWData(sample, combData));
slicedData_Dp = data_combined.reduce(Cut="sample==sample::D_plus")
slicedData_Dp.plotOn(frame_D_plus, Name="data")
sim_model.plotOn(frame_D_plus, Name="Background", Components="model_bkg", ProjWData=(cat, slicedData_Dp),LineColor=ROOT.kGreen+2, LineStyle=ROOT.kDashDotted)
#sim_model.plotOn(frame_D_plus, Name="D+",Components="sig_model", ProjWData=(cat, slicedData_Dp),LineColor=ROOT.kRed, LineStyle=ROOT.kDashDotted)
#sim_model.plotOn(frame_D_plus, Name="Ds+",Components="Ds_model", ProjWData=(cat, slicedData_Dp),LineColor=ROOT.kBlue+2, LineStyle=ROOT.kDashDotted)
sim_model.plotOn(frame_D_plus, Name="Fitting",ProjWData=(cat, slicedData_Dp))
frame_D_plus.Draw("PE")
frame_D_plus.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.2, 0.65, 0.4, 0.90)
# leg1.SetFillColor(ROOT.kWhite)
#leg1.SetFillColor(0)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)

    # leg1.SetHeader("The Legend title","C")
leg1.AddEntry("data", "Data", "PE")
leg1.AddEntry("Fitting", "Fit", "l")
#leg1.AddEntry("D+", "D^{+}", "l")
#leg1.AddEntry("Ds+", "D_{s}^{+}", "l")
leg1.AddEntry("Background", "Bkg", "l")

# leg1.SetTextSize(0.05)
# leg1.SetTextAlign(13)

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
frame_D_minus.GetXaxis().SetTitle("M(K_{S}^{0}#pi^{-}) [GeV/c^{2}]")
slicedData_Dm = data_combined.reduce(Cut="sample==sample::D_minus")
slicedData_Dm.plotOn(frame_D_minus, Name="data")
sim_model.plotOn(frame_D_minus, Name="Background", Components="model_bkg", ProjWData=(cat, slicedData_Dm),LineColor=ROOT.kGreen+2, LineStyle=ROOT.kDashDotted)
#sim_model.plotOn(frame_D_minus, Name="D+",Components="sig_model", ProjWData=(cat, slicedData_Dm),LineColor=ROOT.kRed, LineStyle=ROOT.kDashDotted)
#sim_model.plotOn(frame_D_minus, Name="Ds+",Components="Ds_model", ProjWData=(cat, slicedData_Dm),LineColor=ROOT.kBlue+2, LineStyle=ROOT.kDashDotted)
sim_model.plotOn(frame_D_minus, Name="Fitting",ProjWData=(cat, slicedData_Dm))
frame_D_minus.Draw("PE")
# frame_D_minus.GetXaxis().SetRangeUser(plot_x_range[0], plot_x_range[1])

frame_D_minus.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.2, 0.65, 0.4, 0.90)
# leg1.SetFillColor(ROOT.kWhite)
#leg1.SetFillColor(0)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)

    # leg1.SetHeader("The Legend title","C")
leg1.AddEntry("data", "Data", "PE")
leg1.AddEntry("Fitting", "Fit", "l")
#leg1.AddEntry("D+", "D^{+}", "l")
#leg1.AddEntry("Ds+", "D_{s}^{+}", "l")
leg1.AddEntry("Background", "Bkg", "l")

# leg1.SetTextSize(0.05)
# leg1.SetTextAlign(13)

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
frame_D_all.GetXaxis().SetTitle("M(K_{S}^{0}#pi^{+}) [GeV/c^{2}]")

data_combined.plotOn(frame_D_all, Name="data")
sim_model.plotOn(frame_D_all, Name="Background", Components="model_bkg", ProjWData=(cat, data_combined),LineColor=ROOT.kGreen+2, LineStyle=ROOT.kDashDotted)
sim_model.plotOn(frame_D_all, Name="Fitting", ProjWData=(cat, data_combined))


frame_D_all.Draw("PE")
frame_D_all.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.2, 0.65, 0.4, 0.90)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)
leg1.AddEntry("data", "Data", "PE")
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

    # Print the results
    f.write(f"Nsig_D_plus: Value = {Nsig_D_plus_val}, Error = {Nsig_D_plus_err}\n")
    f.write(f"Nsig_D_minus: Value = {Nsig_D_minus_val}, Error = {Nsig_D_minus_err}\n")


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

# Define the range
fit_range_name = "fit_region"
x.setRange(fit_range_name, fit_range[0], fit_range[1])

# Calculate the integral of the PDF for D_plus over the fitting range
integral_D_plus = model_D_plus.createIntegral(
    ROOT.RooArgSet(x),  # Fit variable
    ROOT.RooFit.NormSet(ROOT.RooArgSet(x))  # Normalization range
).getVal()

# Expected yield for D_plus
expected_yield_D_plus = integral_D_plus * (Nsig_D_plus.getVal() + Nbkg_D_plus.getVal())

print(f"Integral (D_plus): {integral_D_plus}")
print(f"Expected Yield (D_plus): {expected_yield_D_plus}")


# Calculate the integral of the PDF for D_minus over the fitting range
integral_D_minus = model_D_minus.createIntegral(
    ROOT.RooArgSet(x),  # Fit variable
    ROOT.RooFit.NormSet(ROOT.RooArgSet(x))  # Normalization range
).getVal()

# Expected yield for D_minus
expected_yield_D_minus = integral_D_minus * (Nsig_D_minus.getVal() + Nbkg_D_minus.getVal())

print(f"Integral (D_minus): {integral_D_minus}")
print(f"Expected Yield (D_minus): {expected_yield_D_minus}")


# Data entries for D_plus
slicedData_Dp = data_combined.reduce(Cut=f"sample==sample::D_plus && {x.GetName()} > {fit_range[0]} && {x.GetName()} < {fit_range[1]}")
#data_entries_D_plus = slicedData_Dp.sumEntries(f"{x.GetName()} > {fit_range[0]} && {x.GetName()} < {fit_range[1]}")
data_entries_D_plus = slicedData_Dp.sumEntries()

# Data entries for D_minus
slicedData_Dm = data_combined.reduce(Cut=f"sample==sample::D_minus && {x.GetName()} > {fit_range[0]} && {x.GetName()} < {fit_range[1]}")
#data_entries_D_minus = slicedData_Dm.sumEntries(f"{x.GetName()} > {fit_range[0]} && {x.GetName()} < {fit_range[1]}")
data_entries_D_minus = slicedData_Dm.sumEntries()

print(f"Data Entries (D_plus): {data_entries_D_plus}")
print(f"Data Entries (D_minus): {data_entries_D_minus}")

# Define the additional range
additional_range_name = "additional_region"
x.setRange(additional_range_name, 1.84, 1.90)

# Set the category to D_plus for the additional range
#slicedData_Dp = data_combined.reduce(Cut="sample==sample::D_plus")
data_entries_D_plus_additional = slicedData_Dp.sumEntries(
  f"{x.GetName()} > 1.84 && {x.GetName()} < 1.90 "
)
print(f"Data Entries (D_plus) in additional range: {data_entries_D_plus_additional}")

# Set the category to D_minus for the additional range
#slicedData_Dm = data_combined.reduce(Cut="sample==sample::D_minus")
data_entries_D_minus_additional = slicedData_Dm.sumEntries(
  f"{x.GetName()} > 1.84 && {x.GetName()} < 1.90"
)
print(f"Data Entries (D_minus) in additional range: {data_entries_D_minus_additional}")



# Calculate the integral of the PDF for D_plus over the additional range
integral_D_plus_additional = model_D_plus.createIntegral(
    ROOT.RooArgSet(x),
    ROOT.RooFit.NormSet(ROOT.RooArgSet(x)),
    ROOT.RooFit.Range(additional_range_name)
).getVal()

# Expected yield for D_plus in the additional range
expected_yield_D_plus_additional = integral_D_plus_additional * (Nsig_D_plus.getVal() +  Nbkg_D_plus.getVal())

print(f"Integral (D_plus) in additional range: {integral_D_plus_additional}")
print(f"Expected Yield (D_plus) in additional range: {expected_yield_D_plus_additional}")


# Calculate the integral of the PDF for D_minus over the additional range
integral_D_minus_additional = model_D_minus.createIntegral(
    ROOT.RooArgSet(x),
    ROOT.RooFit.NormSet(ROOT.RooArgSet(x)),
    ROOT.RooFit.Range(additional_range_name)
).getVal()

# Expected yield for D_minus in the additional range
expected_yield_D_minus_additional = integral_D_minus_additional * (Nsig_D_minus.getVal() + Nbkg_D_minus.getVal())

print(f"Integral (D_minus) in additional range: {integral_D_minus_additional}")
print(f"Expected Yield (D_minus) in additional range: {expected_yield_D_minus_additional}")

'''
ToyMC_all = ROOT.RooMCStudy(sim_model, {x,cat}, Extended(True), FitOptions(Save(True),PrintEvalErrors(0),PrintLevel(-1), NumCPU(6), Offset(True)))
ToyMC_all.generateAndFit(1000)

toyMC_frame_Acp = ToyMC_all.plotPull(Acp, Bins(30), FitGauss(True))
toyMC_frame_N_total = ToyMC_all.plotPull(N_total, Bins(30), FitGauss(True))

common_title = "Pull"
toyMC_frame_Acp.GetXaxis().SetTitle("A_{CP}(D^{#pm})" +  f" {common_title}")
toyMC_frame_N_total.GetXaxis().SetTitle("N_{sig}(D^{#pm})" +  f" {common_title}")


toyMC_canvas = ROOT.TCanvas("toyMC_canvas", "D+ fit", 800, 600)
toyMC_frame_Acp.Draw()
toyMC_canvas.SaveAs(f"toy_Acp_{ref_tree}_{tree_name}.png")

toyMC_canvas_N_total = ROOT.TCanvas("toyMC_canvas_N_total", "D+ fit", 800, 600)
toyMC_frame_N_total.Draw()
toyMC_canvas_N_total.SaveAs(f"toy_N_total_{ref_tree}_{tree_name}.png")
'''
sPlot = RooStats.SPlot("sPlot", "sPlot", data_combined,
                       sim_model,
                       RooArgList(N_total, Nbkg_total))

# Extract sWeights
# sWeights are stored in a RooDataSet as an additional variable
sWeights = sPlot.GetSDataSet()

# Print or access the sWeights
print("sWeights dataset:")
sWeights.Print()

#print("sPlot dataset:")
#sPlot.Print()

N_total_sWeight = sPlot.GetYieldFromSWeight("N_total")
Nbkg_total_sWeight = sPlot.GetYieldFromSWeight("Nbkg_total")

print(f"Yield N_total is {N_total.getVal()}. From sWeights it is {N_total_sWeight}")
print(f"Yield Nbkg_total is {Nbkg_total.getVal()}. From sWeights it is {Nbkg_total_sWeight}")

# Optionally, you can get the sWeight for each event
#sWeight_variable = sWeights.addColumn("sWeight")  # This is optional, to make the column available
#for i in range(sWeights.numEntries()):
for i in range(0,10):
    print(f"Entry {i}: sWeight = {sWeights.get(i).getRealValue('sWeight')}")
for i in range(0,10):
    N_total_sWeight = sPlot.GetSWeight(i, "N_total")
    print(f"Entry {i}: N_total sWeight = {N_total_sWeight}")
    Nbkg_total_sWeight = sPlot.GetSWeight(i, "Nbkg_total")
    print(f"Entry {i}: Nbkg_total sWeight = {Nbkg_total_sWeight}")
    Total_sWeight = sPlot.GetSumOfEventSWeight(i)
    print(f"Entry {i}: Total sWeight = {Total_sWeight}")
    print("======================")


data_combined.Print()

output_file = TFile(f"{file_sweight}", "RECREATE")

# Save the RooDataSet to the file
data_combined.Write("sweight")

# Close the file
output_file.Close()

cdata = ROOT.TCanvas("sPlot", "sPlot demo", 600, 600)
cdata.Divide(1, 2)
cdata.cd(0)

sdata_Pip_p = ROOT.RooDataSet(data_combined.GetName(), data_combined.GetTitle(), data_combined, data_combined.get(), "", "N_total_sw")

Pip_p_frame = BDT.frame(0, 1, 50)
#Pip_p_frame.SetMinimum(0)  # Set y-axis minimum to 0
#Pip_p_frame.SetAxisRange(0,5.2)
#Pip_p_frame.SetAxisRange(0,,"Y")

sdata_Pip_p.plotOn(Pip_p_frame, ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
#Pip_p_frame.GetYaxis().SetRangeUser(0,)  # Set y-axis minimum to 0
Pip_p_frame.GetYaxis().SetRangeUser(0, Pip_p_frame.GetMaximum())
Pip_p_frame.SetTitle("sWeighted BDT")
Pip_p_frame.Draw()

cdata.SaveAs("test_gg.png")
