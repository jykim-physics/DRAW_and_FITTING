import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory
import glob
import ctypes
import os
import math

ROOT.gROOT.LoadMacro('/home/jykim/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()
file_name = "/share/storage/jykim/plots/MC15rd/etapip/gg/MC15rd_6M_etapip_gg_Dp_M_opt_v7_CB_conv_extended_sim.png"
file_name_Ds = "/share/storage/jykim/plots/MC15rd/etapip/gg/MC15rd_6M_etapip_gg_Dp_M_opt_v7_CB_conv_extended_Ds_sim.png"
result_name = "/share/storage/jykim/plots/MC15rd/etapip/gg/MC15rd_6M_etapip_gg_Dp_M_opt_v7_CB_conv_result_extended_sim.txt"

file_dir = os.path.dirname(file_name)
result_dir = os.path.dirname(result_name)
os.makedirs(file_dir, exist_ok=True)
os.makedirs(result_dir, exist_ok=True)

# Get the tree from the file
tree_name = "etapip_gg"

# Define fitting variable and its range
fit_variable = "Dp_M"
fit_var_name = "M(D^{+}) [GeV/c^{2}]"
fit_range = (1.76, 1.96)
fit_range = (1.763, 1.963)
#fit_range = (1.78, 1.94)
fit_range = (1.78, 2.04)
fit_range_Dp = (1.78, 1.94)
fit_range_Ds = (1.88, 2.04)

rank_var = tree_name + "_rank"
truth_var = "Dp_isSignal"
charge_var = "Pip_charge"
cuts_Dp = " Pip_charge==1"
cuts_Dm = " Pip_charge==-1"
cuts_Dp_fit = cuts_Dp + f" &&  Dp_M>{fit_range_Dp[0]} &&  Dp_M<{fit_range_Dp[1]}"
cuts_Dm_fit = cuts_Dm + f" &&  Dp_M>{fit_range_Dp[0]} &&  Dp_M<{fit_range_Dp[1]}"
cuts_Dsp_fit = cuts_Dp + f" &&  Dp_M>{fit_range_Ds[0]} &&  Dp_M<{fit_range_Ds[1]}"
cuts_Dsm_fit = cuts_Dm + f" &&  Dp_M>{fit_range_Ds[0]} &&  Dp_M<{fit_range_Ds[1]}"

pi0_dphi_var =  "eta_Pi0_daughterDiffOfPhi_0_1"
pi0_dangle_var =  "eta_Pi0_daughterAngle_0_1"
g1_p_var = "etapip_pi0_gamma1_p"
g2_p_var = "etapip_pi0_gamma2_p"

# Create a RooRealVar for the fitting variable
x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
x.setRange("range_Dp", fit_range_Dp[0], fit_range_Dp[1])
x.setRange("range_Ds", fit_range_Ds[0], fit_range_Ds[1])
chiProb_rank = ROOT.RooRealVar(rank_var, rank_var, 0, 30)
truth_var = ROOT.RooRealVar(truth_var, truth_var, 0, 30)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)


mychain = ROOT.TChain(tree_name)
mychain.Add("/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_gg/250122_loose_v7/etapip_gg/train_Dp_dz/all/*BCS.root")
tree_name_cc = "etapip_gg"
mychain_cc = ROOT.TChain(tree_name_cc)
mychain_cc.Add("/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_gg_cc/250122_loose_v7/etapip_gg/train_Dp_dz/all/*BCS.root")
before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,truth_var, Pip_charge), cuts_Dp_fit)

w_1 = ROOT.RooRealVar('w_1', 'w', 0,1)
w_1.setVal(1)
before_data.addColumn(w_1)
data = ROOT.RooDataSet(before_data.GetName(), before_data.GetTitle(),before_data, before_data.get(), '' ,  'w_1')

before_data_cc = ROOT.RooDataSet("data_cc","", mychain_cc, ROOT.RooArgSet(x,truth_var, Pip_charge), cuts_Dm_fit)
before_data_cc.addColumn(w_1)
data_cc = ROOT.RooDataSet(before_data_cc.GetName(), before_data_cc.GetTitle(),before_data_cc, before_data_cc.get(), '' ,  'w_1')
data.append(data_cc)

N_total = data.sumEntries()
print(N_total)

N_signal = ROOT.RooRealVar("N_signal", "Number of signal events", N_total, 0.5*N_total, 2*N_total)  # Initial guess and bounds

mychain_Ds = ROOT.TChain(tree_name)
mychain_Ds.Add("/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dsptoetapip_gg/250122_loose_v7/etapip_gg/train_Dp_dz/all/*BCS.root")
mychain_Ds_cc = ROOT.TChain(tree_name_cc)
mychain_Ds_cc.Add("/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dsptoetapip_gg_cc/250122_loose_v7/etapip_gg/train_Dp_dz/all/*BCS.root")
before_data_Ds = ROOT.RooDataSet("data_Ds","", mychain_Ds, ROOT.RooArgSet(x,truth_var, Pip_charge), cuts_Dsp_fit)

before_data_Ds.addColumn(w_1)
data_Ds = ROOT.RooDataSet(before_data_Ds.GetName(), before_data_Ds.GetTitle(),before_data_Ds, before_data_Ds.get(), '' ,  'w_1')

before_data_Ds_cc = ROOT.RooDataSet("data_Ds_cc","", mychain_Ds_cc, ROOT.RooArgSet(x,truth_var, Pip_charge), cuts_Dsm_fit)
before_data_Ds_cc.addColumn(w_1)
data_Ds_cc = ROOT.RooDataSet(before_data_Ds_cc.GetName(), before_data_Ds_cc.GetTitle(),before_data_Ds_cc, before_data_Ds_cc.get(), '' ,  'w_1')
data_Ds.append(data_Ds_cc)

N_total_Ds = data_Ds.sumEntries()
print(N_total_Ds)

N_signal_Ds = ROOT.RooRealVar("N_signal_Ds", "Number of signal events", N_total_Ds, 0.5*N_total_Ds, 2*N_total_Ds)  # Initial guess and bounds




mean = ROOT.RooRealVar("mean", "mean", 1.86, 1.8, 2.0)
sigma = ROOT.RooRealVar("sigma", "sigma", 0.02, 0.001, 0.1)
sigmaL = ROOT.RooRealVar("sigmaL", "sigma", 0.02, 0.0001, 0.1)
sigmaR = ROOT.RooRealVar("sigmaR", "sigma", 0.01, 0.0001, 0.1)
alphaL = ROOT.RooRealVar("alphaL", "alphaL", 0.2, 0.0, 5.0)
nL = ROOT.RooRealVar("nL", "nL", 3.0, 0.0, 10.0)
alphaR = ROOT.RooRealVar("alphaR", "alphaR", 0.3, 0.0, 5)
nR = ROOT.RooRealVar("nR", "nR", 2.0, 0.0, 5.0)

# Create double-sided Crystal Ball PDF
#CB = ROOT.RooCrystalBall("CB", "CB_left", x, mean, sigma, alphaL, nL, alphaR, nR)
CB = ROOT.RooCrystalBall("CB", "CB", x, mean, sigmaL, sigmaR, alphaL, nL, alphaR, nR)


#mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0, -1, 1)
mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0)
sigma_gaussian = ROOT.RooRealVar("sigma_gaussian", "sigma of Gaussian", 0.01, 0.0001, 0.1)
# Create a Gaussian distribution
gaussian = ROOT.RooGaussian("gaussian", "Gaussian PDF", x, mean_gaussian, sigma_gaussian)

sigma_gaussian_Ds = ROOT.RooRealVar("sigma_gaussian_Ds", "sigma of Gaussian", 0.008, 0.0001, 0.1)
gaussian_Ds = ROOT.RooGaussian("gaussian_Ds", "Gaussian PDF", x, mean_gaussian, sigma_gaussian_Ds)

# Convolute the Johnson distribution with Gaussian
model = ROOT.RooFFTConvPdf("model", "Convolution of Johnson and Gaussian", x, CB, gaussian)

extended_signal_model = ROOT.RooAddPdf(
    "extended_signal_model",
    "Extended Signal Model",
    ROOT.RooArgList(model),
    ROOT.RooArgList(N_signal)
)

mean_Ds = ROOT.RooRealVar("mean_Ds", "mean_Ds", 1.96, 1.9, 2.0)
CB_Ds = ROOT.RooCrystalBall("CB_Ds", "CB_Ds", x, mean_Ds, sigmaL, sigmaR, alphaL, nL, alphaR, nR)
model_Ds = ROOT.RooFFTConvPdf("model_Ds", "Convolution of Johnson and Gaussian", x, CB_Ds, gaussian_Ds)

extended_signal_model_Ds = ROOT.RooAddPdf(
    "extended_signal_model_Ds",
    "Extended Signal Model_Ds",
    ROOT.RooArgList(model_Ds),
    ROOT.RooArgList(N_signal_Ds)
)

cat = RooCategory("sample", "sample")
cat.defineType("Dp")
cat.defineType("Ds")

sim_model = RooSimultaneous("sim_model", "Simultaneous model", cat)
sim_model.addPdf(extended_signal_model, "Dp")
sim_model.addPdf(extended_signal_model_Ds, "Ds")

data_combined = RooDataSet("data_combined", "Combined data", RooArgList(x, w_1), RooFit.Index(cat),
                           RooFit.Import("Dp", data),
                           RooFit.Import("Ds", data_Ds),
                           RooFit.WeightVar('w_1'))
nll = sim_model.createNLL(data_combined, ROOT.RooFit.Extended(True), ROOT.RooFit.NumCPU(4), RooFit.SumW2Error(True),  ROOT.RooFit.Offset(True), ROOT.RooFit.Range(fit_range[0], fit_range[1]))

minimizer = ROOT.RooMinimizer(nll)
minimizer.setStrategy(2)
#minimizer.setStrategy(0)
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
result  = minimizer.save()
#r.Print("v")

# Print fit results
result.Print()

fitted_N_signal = N_signal.getVal()
total_signal_events =  6*1e6
signal_efficiency = fitted_N_signal / total_signal_events

def calculate_sig_eff_err(eff, N_gen):

    error = math.sqrt(eff * (1 - eff) / N_gen)
    return error

# Open a text file in write mode
with open(result_name, "w") as f:

    # Print the full fit result to the file
    f.write("Full fit result summary:\n")
    result.Print("v")  # Verbose print (prints more details)

    # Alternatively, write specific attributes to the file
    f.write("\nSpecific fit result details:\n")
    f.write(f"Status: {result.status()}\n")
    f.write(f"Covariance quality: {result.covQual()}\n")
    f.write(f"EDM (Estimated Distance to Minimum): {result.edm()}\n")
    f.write(f"Min NLL: {result.minNll()}\n")

    # Access and write parameter values and errors to the file
    f.write("\nFitted Parameters:\n")
    params = result.floatParsFinal()  # This returns the final fitted parameters
    for i in range(params.getSize()):
        param = params[i]
        f.write(f"{param.GetName()} = {param.getVal()} ± {param.getError()}\n")

    f.write(f"Fitted number of signal events: {fitted_N_signal}\n")
    f.write(f"Total number of signal events in dataset: {total_signal_events}\n")
    f.write(f"Signal efficiency: {signal_efficiency:.6f}\n")
    f.write(f"Signal efficiency stats. error: {calculate_sig_eff_err(signal_efficiency,total_signal_events):.8f}\n")

    f.write(f"Counting Signal efficiency: {N_total/total_signal_events:.6f}\n")

    # Optionally print a completion message
    f.write("\nFit result saved successfully.\n")

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
frame_D_plus = x.frame(ROOT.RooFit.Title("D+ fit"), ROOT.RooFit.Range("range_Dp"))
#simPdf.plotOn(frame1, Slice(sample, "plus"), Components("bkg"), ProjWData(sample, combData), LineStyle(kDashed));
#simPdf.plotOn(frame1, Slice(sample, "plus"), ProjWData(sample, combData));
slicedData_Dp = data_combined.reduce(Cut="sample==sample::Dp")
slicedData_Dp.plotOn(frame_D_plus, Name="data")
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

# leg1.SetTextSize(0.05)
# leg1.SetTextAlign(13)

leg1.SetBorderSize(0)
leg1.Draw()

hpull = frame_D_plus.pullHist()
hpull.SetFillStyle(1001)
hpull.SetFillColor(1);
for i in range(0,hpull.GetN()):#(int i=0;i<hpull.GetN();++i):
    hpull.SetPointError(i,0.0,0.0,0.0,0.0)
pullplot = x.frame( ROOT.RooFit.Range("range_Dp"))
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

xmin1 = ctypes.c_double(fit_range_Dp[0])
xmax1 = ctypes.c_double(fit_range_Dp[1])
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
canvas_D_plus.SaveAs(file_name)

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
frame_D_minus = x.frame(ROOT.RooFit.Title("D+ fit"), ROOT.RooFit.Range("range_Ds"))
slicedData_Dm = data_combined.reduce(Cut="sample==sample::Ds")
slicedData_Dm.plotOn(frame_D_minus, Name="data")
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

# leg1.SetTextSize(0.05)
# leg1.SetTextAlign(13)

leg1.SetBorderSize(0)
leg1.Draw()

hpull = frame_D_minus.pullHist()
hpull.SetFillStyle(1001)
hpull.SetFillColor(1);
for i in range(0,hpull.GetN()):#(int i=0;i<hpull.GetN();++i):
    hpull.SetPointError(i,0.0,0.0,0.0,0.0)
pullplot = x.frame( ROOT.RooFit.Range("range_Ds"))
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

xmin1 = ctypes.c_double(fit_range_Ds[0])
xmax1 = ctypes.c_double(fit_range_Ds[1])
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
canvas_D_minus.SaveAs(file_name_Ds)

f = ROOT.TFile(result_name, "RECREATE")
result.Write("jykim")
f.Close()
