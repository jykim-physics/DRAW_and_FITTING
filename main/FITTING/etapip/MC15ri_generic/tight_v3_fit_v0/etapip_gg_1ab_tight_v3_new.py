import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory
import glob
import ctypes
import os

file_name = "/share/storage/jykim/plots/MC15ri/etapip/gg/generic/MC15ri_1ab_etapip_gg_fit_tight_v2_fitv2.png"
fitresult_name = "/share/storage/jykim/plots/MC15ri/etapip/gg/generic/fitresult/MC15ri_1ab_etapip_gg_fit_tight_v2_fitv2.root"
fitresult_text = ""
dir_path = os.path.dirname(file_name)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)
dir_path = os.path.dirname(fitresult_name)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)

ROOT.gROOT.LoadMacro('/home/jykim/workspace/git/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

base_file_loc =  '/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15ri/etapip_eteeta/MC15ri_etaetapip_tight_v3_241014/etapip_gg/'

#loc_ccbar = base_file_loc + 'ccbar/tight_v2_240419_Kp_BCS_etapi0const_ccbar_output_02*.root'
loc_ccbar = base_file_loc + '*ccbar*.root'
# loc_ccbar = base_file_loc + 'topo/resultfile/result_antiKstar/standard.root'
loc_uubar = base_file_loc + '*uubar*.root'
loc_ddbar = base_file_loc + '*ddbar*.root'
loc_ssbar = base_file_loc + '*ssbar*.root'
loc_charged = base_file_loc + '*charged*.root'
loc_mixed = base_file_loc + 'mixed*.root'
loc_taupair = base_file_loc + '*taupair*.root'

file_list = [loc_ccbar,loc_uubar,loc_ddbar,loc_ssbar,loc_charged,loc_mixed,loc_taupair]
#file_list = [loc_ccbar]

tree_name = "etapip_gg"
mychain = ROOT.TChain(tree_name)
for i in file_list:
    mychain.Add(i)
print(file_list)

# Define variable and its range
fit_variable = "Dp_M"
fit_var_name = "M(D^{+}) [GeV/c^{2}]"
fit_range = (1.84, 2.04)
truth_var = "Dp_isSignal"
charge_var = "Pip_charge"

cuts_Dp = charge_var + "==1"
cuts_Dm = charge_var + "==-1"

x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
x.setBins(80)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)

before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,Pip_charge), cuts_Dp)

w_1 = ROOT.RooRealVar('w_1', 'w', 0,1)
w_1.setVal(1)
before_data.addColumn(w_1)
data = ROOT.RooDataSet(before_data.GetName(), before_data.GetTitle(),before_data, before_data.get(), '' ,  'w_1')
Num_total = data.sumEntries()
print(Num_total)

mychain_cc = ROOT.TChain(tree_name)
for i in file_list:
    mychain_cc.Add(i)
before_data_cc = ROOT.RooDataSet("data","", mychain_cc, ROOT.RooArgSet(x,Pip_charge), cuts_Dm)
before_data_cc.addColumn(w_1)
data_cc = ROOT.RooDataSet(before_data_cc.GetName(), before_data_cc.GetTitle(),before_data_cc, before_data_cc.get(), '' ,  'w_1')

#data.append(data_cc)
Num_total_cc = data_cc.sumEntries()
print(Num_total_cc)

N_total = RooRealVar("N_total", "N_total (N_D+ + N_D-)", 100000, 80000, 120000)  # N_total = N_D+ + N_D-
Acp = RooRealVar("Acp", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

# Use Acp and N_total to define the expected signal yields for D+ and D-
Nsig_D_plus = RooFormulaVar("Nsig_D_plus",
    "0.5 * N_total * (1 + Acp)",
    RooArgList(N_total, Acp))

Nsig_D_minus = RooFormulaVar("Nsig_D_minus",
    "0.5 * N_total * (1 - Acp)",
    RooArgList(N_total, Acp))

N_total_Ds = RooRealVar("N_total_Ds", "N_total (N_Ds+ + N_Ds-)", 200000, 100000, 300000)  # N_total = N_D+ + N_D-
Acp_Ds = RooRealVar("Acp_Ds", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

# Use Acp and N_total to define the expected signal yields for D+ and D-
Nsig_Ds_plus = RooFormulaVar("Nsig_Ds_plus",
    "0.5 * N_total_Ds * (1 + Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))

Nsig_Ds_minus = RooFormulaVar("Nsig_Ds_minus",
    "0.5 * N_total_Ds * (1 - Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))

# true+false matched fixed
mean_johnson = ROOT.RooRealVar("mean_johnson", "mean of Johnson", 1.880337 )
sigma_johnson = ROOT.RooRealVar("sigma_johnson", "sigma of Johnson", 0.002835)
gamma = ROOT.RooRealVar("gamma", "gamma of Johnson", 0.321131 )
delta = ROOT.RooRealVar("delta", "delta of Johnson", 0.597178 )


mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0, -1, 1)
sigma_gaussian = ROOT.RooRealVar("sigma_gaussian", "sigma of Gaussian", 0.01, 0.00001, 1)

# Create a Johnson distribution
johnson = ROOT.RooJohnson("johnson", "Johnson PDF", x, mean_johnson, sigma_johnson, gamma, delta)

# Create a Gaussian distribution
gaussian = ROOT.RooGaussian("gaussian", "Gaussian PDF", x, mean_gaussian, sigma_gaussian)

# Convolute the Johnson distribution with Gaussian
sig_model = ROOT.RooFFTConvPdf("sig_model", "Convolution of Johnson and Gaussian", x, johnson, gaussian)

Ds_mean_johnson = ROOT.RooRealVar("Ds_mean_johnson", "mean of Johnson", 1.992838)
Ds_sigma_johnson = ROOT.RooRealVar("Ds_sigma_johnson", "sigma of Johnson", 0.001651)
Ds_gamma = ROOT.RooRealVar("Ds_gamma", "gamma of Johnson", 0.346944)
Ds_delta = ROOT.RooRealVar("Ds_delta", "delta of Johnson", 0.470654)

Ds_mean_gaussian = ROOT.RooRealVar("Ds_mean_gaussian", "mean of Gaussian", 0, -1, 1)
Ds_sigma_gaussian = ROOT.RooRealVar("Ds_sigma_gaussian", "sigma of Gaussian", 0.01, 0.00001, 1)

# Create a Johnson distribution
Ds_johnson = ROOT.RooJohnson("Ds_johnson", "Johnson PDF", x, Ds_mean_johnson, Ds_sigma_johnson, Ds_gamma, Ds_delta)

# Create a Gaussian distribution
Ds_gaussian = ROOT.RooGaussian("Ds_gaussian", "Gaussian PDF", x, Ds_mean_gaussian, Ds_sigma_gaussian)

# Convolute the Johnson distribution with Gaussian
Ds_model = ROOT.RooFFTConvPdf("Ds_model", "Convolution of Johnson and Gaussian", x, Ds_johnson, Ds_gaussian)

x_bkg1_Cheby_c0 = ROOT.RooRealVar("x_bkg1_Cheby_c0", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c1 = ROOT.RooRealVar("x_bkg1_Cheby_c1", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c2 = ROOT.RooRealVar("x_bkg1_Cheby_c2", "c0",0.0, -1.0, 1.0)
#x_bkg1_tau = ROOT.RooRealVar("x_bkg1_tau", "c0",-0.5, -20, 0)

#bkg_model = ROOT.RooPolynomial("bkg_model", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1))
#model_bkg = ROOT.RooExponential("model_bkg", "x_bkg1", x, x_bkg1_tau)
model_bkg = ROOT.RooPolynomial("model_bkg", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1))
#model_bkg = ROOT.RooPolynomial("model_bkg", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1, x_bkg1_Cheby_c2))

Nbkg_D_plus = ROOT.RooRealVar("Nbkg_D_plus", "Number of background events for D+", 600000, 300000, 700000)
Nbkg_D_minus = ROOT.RooRealVar("Nbkg_D_minus", "Number of background events for D-", 600000,300000, 700000)


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

data_combined = RooDataSet("data_combined", "Combined data", RooArgList(x), RooFit.Index(cat),
                           RooFit.Import("D_plus", data),
                           RooFit.Import("D_minus", data_cc))

# Fit the model to the combined data
#fit_result = sim_model.fitTo(data_combined, RooFit.Save())
#fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4), RooFit.Strategy(2), RooFit.Minos(0), RooFit.Hesse(1))
fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4), RooFit.Strategy(0), RooFit.Minos(0), RooFit.Hesse(1))

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
canvas_D_plus = ROOT.TCanvas("canvas_D_plus", "D+ fit", 700, 640)
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
sim_model.plotOn(frame_D_plus, Name="Background", Components="model_bkg", ProjWData=(cat, slicedData_Dp),LineColor=ROOT.kGreen+2, LineStyle=ROOT.kDashDotted)
sim_model.plotOn(frame_D_plus, Name="D+",Components="sig_model", ProjWData=(cat, slicedData_Dp),LineColor=ROOT.kRed, LineStyle=ROOT.kDashDotted)
sim_model.plotOn(frame_D_plus, Name="Ds+",Components="Ds_model", ProjWData=(cat, slicedData_Dp),LineColor=ROOT.kBlue+2, LineStyle=ROOT.kDashDotted)
sim_model.plotOn(frame_D_plus, Name="Fitting",ProjWData=(cat, slicedData_Dp))
frame_D_plus.Draw("PE")
frame_D_plus.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.8, 0.65, 1.00, 0.90)
# leg1.SetFillColor(ROOT.kWhite)
#leg1.SetFillColor(0)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)

    # leg1.SetHeader("The Legend title","C")
leg1.AddEntry("data", "MC", "PE")
leg1.AddEntry("Fitting", "Fit", "l")
leg1.AddEntry("D+", "D^{+}", "l")
leg1.AddEntry("Ds+", "D_{s}^{+}", "l")
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
pullplot.SetMinimum(-4.)
pullplot.SetMaximum(4.)
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
canvas_D_plus.SaveAs("D_plus_fit.png")

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

canvas_D_minus.cd(1)
frame_D_minus = x.frame(ROOT.RooFit.Title("D+ fit"))
slicedData_Dm = data_combined.reduce(Cut="sample==sample::D_minus")
slicedData_Dm.plotOn(frame_D_minus, Name="data")
sim_model.plotOn(frame_D_minus, Name="Background", Components="model_bkg", ProjWData=(cat, slicedData_Dm),LineColor=ROOT.kGreen+2, LineStyle=ROOT.kDashDotted)
sim_model.plotOn(frame_D_minus, Name="D+",Components="sig_model", ProjWData=(cat, slicedData_Dm),LineColor=ROOT.kRed, LineStyle=ROOT.kDashDotted)
sim_model.plotOn(frame_D_minus, Name="Ds+",Components="Ds_model", ProjWData=(cat, slicedData_Dm),LineColor=ROOT.kBlue+2, LineStyle=ROOT.kDashDotted)
sim_model.plotOn(frame_D_minus, Name="Fitting",ProjWData=(cat, slicedData_Dm))
frame_D_minus.Draw("PE")
frame_D_minus.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.8, 0.65, 1.00, 0.90)
# leg1.SetFillColor(ROOT.kWhite)
#leg1.SetFillColor(0)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)

    # leg1.SetHeader("The Legend title","C")
leg1.AddEntry("data", "MC", "PE")
leg1.AddEntry("Fitting", "Fit", "l")
leg1.AddEntry("D+", "D^{+}", "l")
leg1.AddEntry("Ds+", "D_{s}^{+}", "l")
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
pullplot.SetMinimum(-4.)
pullplot.SetMaximum(4.)
pullplot.GetXaxis().SetLabelSize(0.15)
pullplot.GetYaxis().SetLabelSize(0.105)
canvas_D_minus.cd(2)
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

canvas_D_minus.Update()
canvas_D_minus.SaveAs("D_minus_fit.png")
