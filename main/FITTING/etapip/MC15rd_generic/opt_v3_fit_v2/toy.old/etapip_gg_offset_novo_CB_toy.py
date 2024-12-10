import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory
from ROOT.RooFit import Extended, FitOptions, Save, PrintEvalErrors, PrintLevel, Bins, FitGauss,    NumCPU, Strategy, Offset
import glob
import ctypes
import os

file_name_Dp = "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/MC15rd_etapip_gg_fit_opt_loose_v2_fitv1_Dp.png"
file_name_Dm = "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/MC15rd_etapip_gg_fit_opt_loose_v2_fitv1_Dm.png"
fitresult_name = "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/MC15rd_etapip_gg_fit_opt_loose_v2_fitv1.root"
fitresult_text = "/share/storage/jykim/plots/MC15rd/etapip/gg/generic/fitresult/MC15rd_etapip_gg_fit_opt_loose_v2_fitv1.txt"
dir_path = os.path.dirname(file_name_Dp)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)
dir_path = os.path.dirname(fitresult_name)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

#file_list = ['/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15ri/etapip_eteeta/MC15ri_etaetapip_loose_v2_241106_yespi0veto/etapip_gg/MC15ri*.root']
base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/etapip_eteeta/MC15rd_etaetapip_loose_v2_241115_MC15rd_weight_q_s"
cm_elements = ["15rd_eta_e7_18_4S_v3", "15rd_eta_e20_b26_v1", "15rd_eta_e20_e26_4S_v2", "15rd_eta_e21_5S_scan_v1", "15rd_eta_mori_off_v1"]

tree_name = "etapip_gg"
file_list = []
for element in cm_elements:
    pattern = f"{base_path}/{element}/{tree_name}/*.BCS.root"
    file_list += glob.glob(pattern)

print(file_list)
mychain = ROOT.TChain(tree_name)
for i in file_list:
    mychain.Add(i)
print(file_list)

# Define variable and its range
fit_variable = "Dp_M"
fit_var_name = "M(D^{+}) [GeV/c^{2}]"
#fit_range = (1.66, 2.06)
fit_range = (1.70, 2.06)
truth_var = "Dp_isSignal"
charge_var = "Pip_charge"

cuts_Dp = charge_var + "==1"
cuts_Dm = charge_var + "==-1"

x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
x.setBins(200)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)

before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,Pip_charge), cuts_Dp)

w_1 = ROOT.RooRealVar('w_1', 'w', 0,1)
#scale = 1
#scale = 427.87/1000
scale = 1/4
w_1.setVal(scale)
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

N_total = RooRealVar("N_total", "N_total (N_D+ + N_D-)", 70000*scale, 50000*scale, 150000*scale)  # N_total = N_D+ + N_D-
Acp = RooRealVar("Acp", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

# Use Acp and N_total to define the expected signal yields for D+ and D-
Nsig_D_plus = RooFormulaVar("Nsig_D_plus",
    "0.5 * N_total * (1 + Acp)",
    RooArgList(N_total, Acp))

Nsig_D_minus = RooFormulaVar("Nsig_D_minus",
    "0.5 * N_total * (1 - Acp)",
    RooArgList(N_total, Acp))

N_total_Ds = RooRealVar("N_total_Ds", "N_total (N_Ds+ + N_Ds-)", 150000*scale, 130000*scale,300000*scale)  # N_total = N_D+ + N_D-
Acp_Ds = RooRealVar("Acp_Ds", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

# Use Acp and N_total to define the expected signal yields for D+ and D-
Nsig_Ds_plus = RooFormulaVar("Nsig_Ds_plus",
    "0.5 * N_total_Ds * (1 + Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))

Nsig_Ds_minus = RooFormulaVar("Nsig_Ds_minus",
    "0.5 * N_total_Ds * (1 - Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))

mean = ROOT.RooRealVar("mean", "mean", 1.870171395, 1.85, 1.89)
sigma = ROOT.RooRealVar("sigma", "sigma",  0.00191079011)
alphaL = ROOT.RooRealVar("alphaL", "alphaL", 0.419305017)
nL = ROOT.RooRealVar("nL", "nL", 3.401633712)
alphaR = ROOT.RooRealVar("alphaR", "alphaR", 0.810107475)
nR = ROOT.RooRealVar("nR", "nR", 2.704652489)

# Create double-sided Crystal Ball PDF
CB = ROOT.RooCrystalBall("CB", "CB_left", x, mean, sigma, alphaL, nL, alphaR, nR)

#mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0, -0.1, 0.1)
mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0)
sigma_gaussian = ROOT.RooRealVar("sigma_gaussian", "sigma of Gaussian", 0.001, 0.00001, 0.1)
gaussian = ROOT.RooGaussian("gaussian", "Gaussian PDF", x, mean_gaussian, sigma_gaussian)

# Convolute the Johnson distribution with Gaussian
sig_model = ROOT.RooFFTConvPdf("sig_model", "Convolution of Johnson and Gaussian", x, CB, gaussian)

Ds_mean = ROOT.RooRealVar("Ds_mean", "mean", 1.968163260, 1.94, 1.98)
Ds_sigma = ROOT.RooRealVar("Ds_sigma", "sigma", 0.00448147003)
Ds_alphaL = ROOT.RooRealVar("Ds_alphaL", "alphaL", 0.843861958)
Ds_nL = ROOT.RooRealVar("Ds_nL", "nL", 3.029465323)
Ds_alphaR = ROOT.RooRealVar("Ds_alphaR", "alphaR", 1.391028020)
Ds_nR = ROOT.RooRealVar("Ds_nR", "nR", 2.587126763)

# Create double-sided Crystal Ball PDF
Ds_CB = ROOT.RooCrystalBall("Ds_CB", "CB_left", x, Ds_mean, Ds_sigma, Ds_alphaL, Ds_nL, Ds_alphaR, Ds_nR)

#Ds_mean_gaussian = ROOT.RooRealVar("Ds_mean_gaussian", "mean of Gaussian", 0, -0.1, 0.1)
Ds_mean_gaussian = ROOT.RooRealVar("Ds_mean_gaussian", "mean of Gaussian", 0)
Ds_sigma_gaussian = ROOT.RooRealVar("Ds_sigma_gaussian", "sigma of Gaussian", 0.001, 0.00001, 0.1)

# Create a Gaussian distribution
Ds_gaussian = ROOT.RooGaussian("Ds_gaussian", "Gaussian PDF", x, Ds_mean_gaussian, Ds_sigma_gaussian)

# Convolute the Johnson distribution with Gaussian
Ds_model = ROOT.RooFFTConvPdf("Ds_model", "Convolution of Johnson and Gaussian", x, Ds_CB, Ds_gaussian)

x_bkg1_Cheby_c0 = ROOT.RooRealVar("x_bkg1_Cheby_c0", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c1 = ROOT.RooRealVar("x_bkg1_Cheby_c1", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c2 = ROOT.RooRealVar("x_bkg1_Cheby_c2", "c0",0.0, -1.0, 1.0)
x_bkg1_tau = ROOT.RooRealVar("x_bkg1_tau", "c0",-0.5, -20, 0)

novo_mean = ROOT.RooRealVar("novo_mean", "Mean", 1.724834555)
novo_sigma = ROOT.RooRealVar("novo_sigma", "Sigma", 0.0642836120)
novo_tail = ROOT.RooRealVar("novo_tail", "Tail", 0.316263240)
# Create Novosibirsk PDF
rhopeta  = ROOT.RooNovosibirsk("rhopeta", "Novosibirsk PDF", x, novo_mean, novo_sigma, novo_tail)

#novo_mean_gaussian = ROOT.RooRealVar("novo_mean_gaussian", "mean of Gaussian", 0, -0.5, 0.5)
#novo_sigma_gaussian = ROOT.RooRealVar("novo_sigma_gaussian", "sigma of Gaussian", 0.01, 0.000001, 0.1)
#novo_gaussian = ROOT.RooGaussian("novo_gaussian", "Gaussian PDF", x, novo_mean_gaussian, novo_sigma_gaussian)
#rhopeta = ROOT.RooFFTConvPdf("rhopeta", "Convolution of Novosibirsk and Gaussian", x, novo, novo_gaussian)

bkg_comb = ROOT.RooExponential("bkg_comb", "x_bkg1", x, x_bkg1_tau)
#model_bkg = ROOT.RooPolynomial("model_bkg", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1, x_bkg1_Cheby_c2))

bkg_frac = ROOT.RooRealVar("bkg_frac", "fraction of Gaussian in BKG", 0.25, 0.1, 1)

model_bkg = ROOT.RooAddPdf("model_bkg", "Gaus + Exp", RooArgList(rhopeta, bkg_comb), bkg_frac)


Nbkg_D_plus = ROOT.RooRealVar("Nbkg_D_plus", "Number of background events for D+", 100000*scale, 50000*scale, 300000*scale)
Nbkg_D_minus = ROOT.RooRealVar("Nbkg_D_minus", "Number of background events for D-", 100000*scale,50000*scale, 300000*scale)


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

data_combined = RooDataSet("data_combined", "Combined data", RooArgList(x, w_1), RooFit.Index(cat),
                           RooFit.Import("D_plus", data),
                           RooFit.Import("D_minus", data_cc),
                           RooFit.WeightVar('w_1'))

# Fit the model to the combined data
#fit_result = sim_model.fitTo(data_combined, RooFit.Save())
#fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4), RooFit.Strategy(2), RooFit.Minos(0), RooFit.Hesse(1))
#fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4), RooFit.Strategy(0), RooFit.Minos(0), RooFit.Hesse(1))
nll = sim_model.createNLL(data_combined, ROOT.RooFit.Extended(True), ROOT.RooFit.NumCPU(15), RooFit.SumW2Error(True),  ROOT.RooFit.Offset(True))

# Step 2: Perform the Migrad minimization
minimizer = ROOT.RooMinimizer(nll)
#minimizer.setStrategy(2)
minimizer.setStrategy(0)
minimizer.setPrintLevel(3)
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
leg1.AddEntry("data", "MC", "PE")
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
leg1.AddEntry("data", "MC", "PE")
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
ToyMC_all = ROOT.RooMCStudy(sim_model, {x,cat}, Extended(True), FitOptions(Save(True),              PrintEvalErrors(0), PrintLevel(-1), NumCPU(6), Offset(True)))
ToyMC_all.generateAndFit(1000)

toyMC_frame_Acp = ToyMC_all.plotPull(Acp, Bins(30), FitGauss(True))
toyMC_frame_Acp_Ds = ToyMC_all.plotPull(Acp_Ds, Bins(30), FitGauss(True))
toyMC_frame_N_total = ToyMC_all.plotPull(N_total, Bins(30), FitGauss(True))
toyMC_frame_N_total_Ds = ToyMC_all.plotPull(N_total_Ds, Bins(30), FitGauss(True))

toyMC_canvas = ROOT.TCanvas("toyMC_canvas", "D+ fit", 800, 600)
toyMC_frame_Acp.Draw()
toyMC_canvas.SaveAs(f"toy_Acp_{tree_name}.png")

toyMC_canvas_Ds = ROOT.TCanvas("toyMC_canvas_Ds", "D+ fit", 800, 600)
toyMC_frame_Acp_Ds.Draw()
toyMC_canvas_Ds.SaveAs(f"toy_Acp_Ds_{tree_name}.png")

toyMC_canvas_N_total = ROOT.TCanvas("toyMC_canvas_N_total", "D+ fit", 800, 600)
toyMC_frame_N_total.Draw()
toyMC_canvas_N_total.SaveAs(f"toy_N_total_{tree_name}.png")

toyMC_canvas_N_total_Ds = ROOT.TCanvas("toyMC_canvas_N_total_Ds", "D+ fit", 800, 600)
toyMC_frame_N_total_Ds.Draw()
toyMC_canvas_N_total_Ds.SaveAs(f"toy_N_total_Ds_{tree_name}.png")
