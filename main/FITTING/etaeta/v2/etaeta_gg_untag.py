import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory, RooStats, TFile
from ROOT.RooFit import Extended, FitOptions, Save, PrintEvalErrors, PrintLevel, Bins, FitGauss,    NumCPU, Strategy, Offset
import glob
import ctypes
import os
import argparse

parser = argparse.ArgumentParser(description="Process Dp_CMS_sign argument")
#suffix = "sumw2fixed"
file_name_Dp = f"Dp_etaeta_gg_untag.png"
file_name_Dm = f"Dm_etaeta_gg_untag.png"
file_name_Dall = f"Dall_etaeta_gg_untag.png"
fitresult_name = f"etaeta_gg_untag.result.root"
fitresult_text = f"etaeta_gg_untag.txt"
file_sweight = f"etaeta_gg_untag_sweight.root"

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC16rd/eteeta/MC16rd_etaeta_cuts_v2_260513"
cm_elements = ["16rd_2eta_R2_4S_v1", "16rd_2eta_R2_off_v1"]

tree_name = "etaeta_gg_untag"
file_list = []
for element in cm_elements:
    pattern = f"{base_path}/{element}/{tree_name}/ranked/*ranked.root"
    file_list += glob.glob(pattern)

print(file_list)
mychain = ROOT.TChain(tree_name)
for i in file_list:
    mychain.Add(i)
#print(file_list)
print(f"Numer of files: {len(file_list)}")

# Define variable and its range
fit_variable = "untag_D0_M"
fit_var_name = "M(#eta_{#gamma#gamma}#eta_{#gamma#gamma}) [GeV/c^{2}]"
#fit_range = (1.60, 2.1)
fit_range = (1.70, 2.0)
#fit_range = (1.74, 2.0)
#fit_range = (1.755, 2.045)

cuts_before_fit = "rank_untag_D0_chiProb==1"

x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
#x.setBins(200)
rank_untag_D0_chiProb = ROOT.RooRealVar("rank_untag_D0_chiProb", "rank_untag_D0_chiProb", -1000000, 10000000)

full_var_set = ROOT.RooArgSet(x, rank_untag_D0_chiProb)

#full_var_set = ROOT.RooArgSet(x, Pip_charge, Dp_CMS_cosTheta, BDT, Pip_dr, Dp_dz,
#                              Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane,
                              #etapip_Eta_Easym, Dp_cosHelicityAngleMomentum,
                              #Dp_CMS_p,rank_Dp_chiProb,ds_weight)
data = ROOT.RooDataSet("data","Data",full_var_set,ROOT.RooFit.Import(mychain),ROOT.RooFit.Cut(cuts_before_fit))

scale=1
N_scale=1
N_total = RooRealVar("N_total", "N_total (N_D+ + N_D-)", 15000*scale*N_scale, 10000*scale*N_scale, 50000*scale*N_scale)  # N_total = N_D+ + N_D-

Nbkg_total = ROOT.RooRealVar("Nbkg_total", "Number of background events for D+", 500000*scale*N_scale, 200000*scale*N_scale,1000000*scale*N_scale)

mean = ROOT.RooRealVar("mean", "mean", 1.87, 1.82, 1.88)  # Central value
sigma = ROOT.RooRealVar("sigma", "sigma", 0.002, 0.00001, 0.1)  # Width parameter
gamma = ROOT.RooRealVar("gamma", "gamma", 0.01, -8.0, 8.0)  # Skewness parameter
delta = ROOT.RooRealVar("delta", "delta", 0.6, 0.001, 3.0)  # Shape parameter

# Create the RooJohnson PDF
#johnson = ROOT.RooJohnson("johnson", "double-sided Crystal Ball using Johnson SU", x,  mean, sigma, gamma, delta)
sig_model  = ROOT.RooJohnson("sig_model", "double-sided Crystal Ball using Johnson SU", x,  mean, sigma, gamma, delta)

mean_gauss = ROOT.RooRealVar("mean_gauss", "Gaussian mean", 0.0)  # Convolution will   center the Gaussian at zero
sigma_gauss = ROOT.RooRealVar("sigma_gauss", "Gaussian width", 0.002, 0.000001, 0.1)


# Create the Gaussian PDF
gauss = ROOT.RooGaussian("gauss", "Gaussian PDF", x, mean_gauss, sigma_gauss)

# Perform the convolution
#sig_model = ROOT.RooFFTConvPdf("sig_model", "Convolution of Johnson SU and Gaussian", x, johnson, gauss)


x_bkg1_Cheby_c0 = ROOT.RooRealVar("x_bkg1_Cheby_c0", "c0",0.1, -1.0, 1.0)
x_bkg1_Cheby_c1 = ROOT.RooRealVar("x_bkg1_Cheby_c1", "c0",0.1, -1.0, 1.0)
x_bkg1_Cheby_c2 = ROOT.RooRealVar("x_bkg1_Cheby_c2", "c0",0.1, -1.0, 1.0)
x_bkg1_tau = ROOT.RooRealVar("x_bkg1_tau", "c0",-5, -20, 5)

#bkg_comb = ROOT.RooExponential("bkg_comb", "x_bkg1", x, x_bkg1_tau)
#model_bkg = ROOT.RooPolynomial("model_bkg", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1, x_bkg1_Cheby_c2))
model_bkg = ROOT.RooExponential("model_bkg", "x_bkg1", x, x_bkg1_tau)
#model_bkg = ROOT.RooPolynomial("model_bkg", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1))


# Define extended PDFs for D+ and D-
model_D_all = ROOT.RooAddPdf("model_D_all", "D model",
                              ROOT.RooArgList(sig_model, model_bkg),
                              ROOT.RooArgList(N_total, Nbkg_total))

# Fit the model
#fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(8), RooFit.Strategy(2))
fit_result = model_D_all.fitTo(data, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(8), RooFit.Strategy(2), ROOT.RooFit.Offset(True))

# Print fit results
fit_result.Print("v")

# Output N_total
N_total_value = N_total.getVal()
N_total_error = N_total.getError()

print(f"N_total = {N_total_value:.0f} ± {N_total_error:.3f}")

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

frame_D_all = x.frame(ROOT.RooFit.Title("D0 fit"))
frame_D_all.GetXaxis().SetTitle("M(#eta_{#gamma#gamma}#eta_{#gamma#gamma}) [GeV/c^{2}]")

data.plotOn(frame_D_all, Name="data")
model_D_all.plotOn(frame_D_all, Name="Background", Components="model_bkg", LineColor=ROOT.kGreen+2)
model_D_all.plotOn(frame_D_all, Name="Fitting")
frame_D_all.Draw("PE")
frame_D_all.GetXaxis().CenterTitle(True)

#leg1 = ROOT.TLegend(0.2, 0.65, 0.4, 0.90)
leg1 = ROOT.TLegend(0.2, 0.2, 0.4, 0.45)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)
leg1.AddEntry("data", "#scale[1.33]{#font[42]{MC}}", "PE")
leg1.AddEntry("Fitting", "#scale[1.33]{#font[42]{Fit}}", "l")
leg1.AddEntry("Background", "#scale[1.33]{#font[42]{Combinatorial}}", "l")
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
