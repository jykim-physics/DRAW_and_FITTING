import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory
from ROOT.RooFit import Extended, FitOptions, Save, PrintEvalErrors, PrintLevel, Bins, FitGauss,    NumCPU, Strategy, Offset
import glob
import ctypes
import os
import math

ROOT.gROOT.LoadMacro('/home/jykim/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()
#file_name = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/MC15rd_6M_etapip_pipipi_K_Dp_M_opt_v7_CB_conv_extended_train_Dp_CMS_p_Ds.0.90.new_Ds.weighted.png"
#result_name = "/share/storage/jykim/plots/MC15rd/etaKp/pipipi/MC15rd_6M_etapip_pipipi_K_Dp_M_opt_v7_CB_conv_result_extended_train_Dp_CMS_p_Ds.0.90.new_Ds.weighted.txt"
file_name = "./test.png"
result_name = "./test.txt"

file_dir = os.path.dirname(file_name)
result_dir = os.path.dirname(result_name)
os.makedirs(file_dir, exist_ok=True)
os.makedirs(result_dir, exist_ok=True)

# Get the tree from the file
tree_name = "etapip_pipipi_K"

# Define fitting variable and its range
fit_variable = "Dp_M"
#fit_var_name = "M(D^{+}) [GeV/c^{2}]"
fit_var_name = "M(#eta_{3#pi}K^{+}) [GeV/c^{2}]"
fit_range =  (1.92, 2.01)
rank_var = tree_name + "_rank"
truth_var = "Dp_isSignal"
charge_var = "Pip_charge"
cuts = rank_var + "==1"
cuts_Dp = "(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & (Pip_genMotherPDG == 431 & Pip_mcPDG == 321)  &  Pip_charge==1"
cuts_Dm = "(etapip_Eta_isSignal == 1) & (Pip_genMotherID == etapip_Eta_genMotherID) & (Pip_genMotherPDG == -431 & Pip_mcPDG == -321)  &  Pip_charge==-1"

pi0_dphi_var =  "eta_Pi0_daughterDiffOfPhi_0_1"
pi0_dangle_var =  "eta_Pi0_daughterAngle_0_1"
g1_p_var = "etapip_pi0_gamma1_p"
g2_p_var = "etapip_pi0_gamma2_p"

# Create a RooRealVar for the fitting variable
x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
chiProb_rank = ROOT.RooRealVar(rank_var, rank_var, 0, 30)
truth_var = ROOT.RooRealVar(truth_var, truth_var, 0, 30)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)
ds_weight = ROOT.RooRealVar("ds_weight", "ds_weight", -1000, 1000)
etapip_Eta_isSignal = ROOT.RooRealVar("etapip_Eta_isSignal", "etapip_Eta_isSignal", -1000000, 1000000)
Pip_genMotherID = ROOT.RooRealVar("Pip_genMotherID", "Pip_genMotherID", -1000000, 1000000)
etapip_Eta_genMotherID = ROOT.RooRealVar("etapip_Eta_genMotherID", "etapip_Eta_genMotherID", -1000000, 1000000)
Pip_genMotherPDG = ROOT.RooRealVar("Pip_genMotherPDG", "Pip_genMotherPDG", -1000000, 1000000)
Pip_mcPDG = ROOT.RooRealVar("Pip_mcPDG", "Pip_mcPDG", -1000000, 1000000)

full_var_set = ROOT.RooArgSet(x, truth_var, Pip_charge, ds_weight, etapip_Eta_isSignal, Pip_genMotherID, etapip_Eta_genMotherID, Pip_genMotherPDG, Pip_mcPDG)

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/etapip_eteeta/MC15rd_etaetapip_loose_v7_250122_skimhad_if_true_Dp_CMS_p_v2"
cm_elements = ["15rd_eta_e7_18_4S_v3", "15rd_eta_e20_b26_v1", "15rd_eta_e20_e26_4S_v2", "15rd_eta_e21_5S_scan_v1", "15rd_eta_mori_off_v1"]

tree_name = "etapip_pipipi_K"
file_list = []
for element in cm_elements:
    #pattern = f"{base_path}/{element}/{tree_name}/{args.train}/skimhad/*.BCS.root"
    #pattern = f"{base_path}/{element}/{tree_name}/train_Dp_dz/skimhad/*.BCS.root"
    #pattern = f"{base_path}/{element}/{tree_name}/train_Dp_dz/skimhad/re_FoM/*.BCS.root"
    #pattern = f"{base_path}/{element}/{tree_name}/train_Dp_dz/skimhad/new_FOM/*.BCS.root"
    pattern = f"{base_path}/{element}/{tree_name}/min_unc_search/0.90/weighted/*.BCS.root"
    file_list += glob.glob(pattern)

print(file_list)
mychain = ROOT.TChain(tree_name)
for i in file_list:
    mychain.Add(i)



# data = ROOT.RooDataSet("data","", ROOT.RooArgSet(x,y,z), ROOT.RooFit.Import(mychain), Cut=" D0_M>1.68 & D0_M<2.05 & Belle2Pi0Veto_75MeV > 0.022 ")
print(cuts)
#before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,truth_var, Pip_charge), cuts_Dp)

before_data = ROOT.RooDataSet("data", "", mychain, full_var_set, cuts_Dp)
scale = 1/4
w_scaled = ROOT.RooFormulaVar("w_scaled", "Scaled Weight", f"{scale}*ds_weight", ROOT.RooArgList(ds_weight))
before_data.addColumn(w_scaled)

data = ROOT.RooDataSet("data_weighted", "Weighted Data", before_data, before_data.get(), "", "w_scaled")

mychain_cc = ROOT.TChain(tree_name)
for i in file_list:
    mychain_cc.Add(i)
#before_data_cc = ROOT.RooDataSet("data","", mychain_cc, ROOT.RooArgSet(x,Pip_charge,Dp_CMS_cosTheta), cuts_Dm)
#before_data_cc.addColumn(w_1)
#data_cc = ROOT.RooDataSet(before_data_cc.GetName(), before_data_cc.GetTitle(),before_data_cc, before_data_cc.get(), '' ,  'w_1')

before_data_cc = ROOT.RooDataSet("data", "", mychain_cc, full_var_set, cuts_Dm)
before_data_cc.addColumn(w_scaled)
data_cc = ROOT.RooDataSet("data_weighted_cc", "Weighted Data", before_data_cc, before_data_cc.get(), "", "w_scaled")

#data.append(data_cc)

N_total = data.sumEntries()
N_total = 2*N_total
#print(N_total)

N_signal = ROOT.RooRealVar("N_signal", "Number of signal events", N_total, 0.8*N_total, 1.2*N_total)  # Initial guess and bounds
Acp = RooRealVar("Acp", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

# Use Acp and N_total to define the expected signal yields for D+ and D-
Nsig_plus = RooFormulaVar("Nsig_plus",
    "0.5 * N_signal * (1 + Acp)",
    RooArgList(N_signal, Acp))

Nsig_minus = RooFormulaVar("Nsig_minus",
    "0.5 * N_signal * (1 - Acp)",
    RooArgList(N_signal, Acp))


mean = ROOT.RooRealVar("mean", "mean", 1.96, 1.9, 2.0)
sigma = ROOT.RooRealVar("sigma", "sigma", 0.001, 0.0001, 0.01)
sigmaL = ROOT.RooRealVar("sigmaL", "sigma", 0.002, 0.00001, 0.01)
sigmaR = ROOT.RooRealVar("sigmaR", "sigma", 0.003, 0.00001, 0.01)
alphaL = ROOT.RooRealVar("alphaL", "alphaL", 1.2, 0.0, 5.0)
nL = ROOT.RooRealVar("nL", "nL", 2.0, 0.0, 5.0)
alphaR = ROOT.RooRealVar("alphaR", "alphaR", 1.5, 0.0, 5.0)
nR = ROOT.RooRealVar("nR", "nR", 1.0, 0.0, 5.0)

# Create double-sided Crystal Ball PDF
#CB = ROOT.RooCrystalBall("CB", "CB_left", x, mean, sigma, alphaL, nL, alphaR, nR)
CB = ROOT.RooCrystalBall("CB", "CB_left", x, mean, sigmaL, sigmaR, alphaL, nL, alphaR, nR)


#mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0, -1, 1)
mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0)
sigma_gaussian = ROOT.RooRealVar("sigma_gaussian", "sigma of Gaussian", 0.008, 0.0001, 0.05)
# Create a Gaussian distribution
gaussian = ROOT.RooGaussian("gaussian", "Gaussian PDF", x, mean_gaussian, sigma_gaussian)

# Convolute the Johnson distribution with Gaussian
model = ROOT.RooFFTConvPdf("CB_left", "Convolution of Johnson and Gaussian", x, CB, gaussian)

model_plus = ROOT.RooAddPdf("model_plus", "D+ model",
                              ROOT.RooArgList(model),
                              ROOT.RooArgList(Nsig_plus))
model_minus = ROOT.RooAddPdf("model_minus", "D- model",
                              ROOT.RooArgList(model),
                              ROOT.RooArgList(Nsig_minus))

cat = RooCategory("sample", "sample")
cat.defineType("D_plus")
cat.defineType("D_minus")

sim_model = RooSimultaneous("sim_model", "Simultaneous model", cat)
sim_model.addPdf(model_plus, "D_plus")
sim_model.addPdf(model_minus, "D_minus")

data_combined = RooDataSet("data_combined", "Combined data", full_var_set,RooFit.Index(cat),
                           RooFit.Import("D_plus", data),
                           RooFit.Import("D_minus", data_cc),
                           RooFit.WeightVar('w_scaled'))

#extended_signal_model = ROOT.RooAddPdf(
#    "extended_signal_model",
#    "Extended Signal Model",
#    ROOT.RooArgList(model),
#    ROOT.RooArgList(N_signal)
#)


# Define parameters for the 1st-order polynomial PDF
a0 = ROOT.RooRealVar("a0", "a0", 0.0, -1.0, 1.0)
a1 = ROOT.RooRealVar("a1", "a1", 0.0, -1.0, 1.0)

# Create 1st-order polynomial PDF
polynomial = ROOT.RooPolynomial("polynomial", "polynomial", x, ROOT.RooArgList(a0, a1))

# Combine the two PDFs
fraction = ROOT.RooRealVar("fraction", "fraction", 0.5, 0.0, 1.0)
#model = ROOT.RooAddPdf("model", "model", ROOT.RooArgList(CB_left, polynomial), ROOT.RooArgList(fraction))
#model = CB_lef

# Perform the fit
#result = model.fitTo(data, ROOT.RooFit.Range(fit_range[0], fit_range[1]), ROOT.RooFit.NumCPU(4), ROOT.RooFit.Save())
#result.Print()

#result = extended_signal_model.fitTo(
result = sim_model.fitTo(
    data_combined,
    ROOT.RooFit.Extended(True),  # Enable extended likelihood fit
    ROOT.RooFit.Range(fit_range[0], fit_range[1]),
    ROOT.RooFit.NumCPU(8),
    ROOT.RooFit.Save(),
    ROOT.RooFit.Offset(True),
    ROOT.RooFit.Strategy(2)
)
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

# Plot the result
#canvas = ROOT.TCanvas("canvas", "canvas", 800, 555)
canv = ROOT.TCanvas("canvas", "canvas", 700, 640)
xlow = ctypes.c_double()
ylow = ctypes.c_double()
xup = ctypes.c_double()
yup = ctypes.c_double()

canv.GetPad(0).GetPadPar(xlow, ylow, xup, yup)
canv.Divide(1,2)

xlow = xlow.value
ylow = ylow.value
xup = xup.value
yup = yup.value

upPad = canv.GetPad(1)
upPad.SetPad(xlow, ylow+0.25*(yup-ylow),xup,yup)

dwPad = canv.GetPad(2)
dwPad.SetPad(xlow, ylow,xup,ylow+0.25*(yup-ylow))

canv.cd(1)
frame = x.frame()

#frame.GetYaxis().SetTitleOffset(0.2)

data_combined.plotOn(frame, ROOT.RooFit.Name("data1"), ROOT.RooFit.XErrorSize(0))


#model.plotOn(frame, ROOT.RooFit.Name("Signal"),ROOT.RooFit.Components("CB_left"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed))
#model.plotOn(frame, ROOT.RooFit.Name("fitting"))
sim_model.plotOn(frame, ROOT.RooFit.Name("fitting"), ProjWData=(cat))

frame.Draw("PE")
frame.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.68, 0.65, 0.93, 0.9)
# leg1.SetFillColor(ROOT.kWhite)
leg1.SetFillColor(0)

    # leg1.SetHeader("The Legend title","C")
leg1.AddEntry("data1", "MC", "PE")
leg1.AddEntry("fitting", "Fit", "l")
#leg1.AddEntry("Signal", "Signal", "l")
# leg1.AddEntry("fitx_bkg3", "bkg3", "l")

# leg1.SetTextSize(0.05)
# leg1.SetTextAlign(13)

leg1.SetBorderSize(0)
leg1.Draw()

hpull = frame.pullHist()
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
canv.cd(2)
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

canv.Update()

canv.Draw()
canv.SaveAs(file_name)

# Save the final figure as .png
#canv.SaveAs("fit_result_with_pull.png")
