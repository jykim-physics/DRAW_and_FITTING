import ROOT
import glob
import ctypes
file_name_Dp = "/share/storage/jykim/plots/MC15ri/etapip/pipipi/MC15ri_1M_etapip_pipipi_Dp_M_opt_v0_johnson_conv_simul_Dp.png"
file_name_Dm = "/share/storage/jykim/plots/MC15ri/etapip/pipipi/MC15ri_1M_etapip_pipipi_Dp_M_opt_v0_johnson_conv_simul_Dsp.png"
result_name = "/share/storage/jykim/plots/MC15ri/etapip/pipipi/MC15ri_1M_etapip_pipipi_Dp_M_opt_v0_johnson_conv_result_simul.txt"

ROOT.gROOT.LoadMacro('/home/jykim/workspace/git/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

# Define tree and variable names
tree_name = "etapip_pipipi"
fit_variable = "Dp_M"
fit_var_name = "M(D^{+}) [GeV/c^{2}]"
fit_range = (1.75, 2.06)
cuts_Dp = "Pip_charge == 1"
cuts_Dm = "Pip_charge == -1"

# Define fitting variable and create RooRealVars
#x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
x = ROOT.RooRealVar("Dp_M", "M(D^{+}) [GeV/c^{2}]", 1.75, 2.06)  # Range specific for Dp
#x.setBins(80)

truth_var = ROOT.RooRealVar("Dp_isSignal", "Dp_isSignal", 0, 30)
Pip_charge = ROOT.RooRealVar("Pip_charge", "Pip_charge", -1, 1)

# Load datasets for Dp
mychain_Dp = ROOT.TChain(tree_name)
mychain_Dp.Add("/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15ri_sigMC/Dptoetapip_pipipi/241030_loose_v1/etapip_pipipi/*BCS.root")
data_Dp = ROOT.RooDataSet("data_Dp", "", mychain_Dp, ROOT.RooArgSet(x, truth_var, Pip_charge), cuts_Dp + " && Dp_M>1.8 && Dp_M<1.93")
#data_Dp = ROOT.RooDataSet("data_Dp", "", mychain_Dp, ROOT.RooArgSet(x, truth_var, Pip_charge), cuts_Dp )

mychain_Dp_cc = ROOT.TChain(tree_name)
mychain_Dp_cc.Add("/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15ri_sigMC/Dptoetapip_pipipi_cc/241030_loose_v1/etapip_pipipi/*BCS.root")
data_Dm = ROOT.RooDataSet("data_Dm", "", mychain_Dp_cc, ROOT.RooArgSet(x, truth_var, Pip_charge), cuts_Dm +  " && Dp_M>1.8 && Dp_M<1.93")
#data_Dm = ROOT.RooDataSet("data_Dm", "", mychain_Dp_cc, ROOT.RooArgSet(x, truth_var, Pip_charge), cuts_Dm )

data_Dp.append(data_Dm)

# Load datasets for Dsp
mychain_Dsp = ROOT.TChain(tree_name)
mychain_Dsp.Add("/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15ri_sigMC/Dsptoetapip_pipipi/241030_loose_v1/etapip_pipipi/*BCS.root")
data_Dsp = ROOT.RooDataSet("data_Dsp", "", mychain_Dsp, ROOT.RooArgSet(x, truth_var, Pip_charge), cuts_Dp +  " && Dp_M>1.89 && Dp_M<2.04")
#data_Dsp = ROOT.RooDataSet("data_Dsp", "", mychain_Dsp, ROOT.RooArgSet(x, truth_var, Pip_charge), cuts_Dp )

mychain_Dsp_cc = ROOT.TChain(tree_name)
mychain_Dsp_cc.Add("/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15ri_sigMC/Dsptoetapip_pipipi_cc/241030_loose_v1/etapip_pipipi/*BCS.root")
data_Dsp_cc = ROOT.RooDataSet("data_Dsm", "", mychain_Dsp_cc, ROOT.RooArgSet(x, truth_var, Pip_charge), cuts_Dm +  " && Dp_M>1.89 && Dp_M<2.04")
#data_Dsp_cc = ROOT.RooDataSet("data_Dsm", "", mychain_Dsp_cc, ROOT.RooArgSet(x, truth_var, Pip_charge), cuts_Dm )

data_Dsp.append(data_Dsp_cc)

# Combine data with a category variable
sample = ROOT.RooCategory("sample", "sample")
sample.defineType("Dp")
sample.defineType("Dsp")

# Apply category-specific ranges to the data
#x.setRange("Dp_range", 1.75, 2.06)  # Range for Dp category
#x.setRange("Dsp_range", 1.85, 2.1)  # Range for Dsp category

combined_data = ROOT.RooDataSet("combined_data", "combined data", ROOT.RooArgSet(x),
                                ROOT.RooFit.Index(sample),
                                ROOT.RooFit.Import("Dp", data_Dp),
                                ROOT.RooFit.Import("Dsp", data_Dsp))

# Shared Gaussian parameters
mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0, -1, 1)
sigma_gaussian = ROOT.RooRealVar("sigma_gaussian", "sigma of Gaussian", 0.01, 0.0001, 1)
mean_gaussian_Dsp = ROOT.RooRealVar("mean_gaussian_Dsp", "mean of Gaussian", 0, -1, 1)
sigma_gaussian_Dsp = ROOT.RooRealVar("sigma_gaussian_Dsp", "sigma of Gaussian", 0.01, 0.0001, 1)

# Dp-specific Crystal Ball parameters
mean_cb_Dp = ROOT.RooRealVar("mean_cb_Dp", "mean of Crystal Ball (Dp)", 1.86, 1.8, 1.9)
sigma_cb_Dp = ROOT.RooRealVar("sigma_cb_Dp", "sigma of Crystal Ball (Dp)", 0.01, 0.000001, 0.5)
alpha_cb_Dp = ROOT.RooRealVar("alpha_cb_Dp", "alpha of Crystal Ball (Dp)", 1.5, 0.1, 5)
n_cb_Dp = ROOT.RooRealVar("n_cb_Dp", "n of Crystal Ball (Dp)", 3, 0.1, 10)

# Dsp-specific Crystal Ball parameters
mean_cb_Dsp = ROOT.RooRealVar("mean_cb_Dsp", "mean of Crystal Ball (Dsp)", 1.96, 1.91, 2.1)
sigma_cb_Dsp = ROOT.RooRealVar("sigma_cb_Dsp", "sigma of Crystal Ball (Dsp)", 0.01, 0.000001, 0.5)
alpha_cb_Dsp = ROOT.RooRealVar("alpha_cb_Dsp", "alpha of Crystal Ball (Dsp)", 1.5, 0.1, 10)
n_cb_Dsp = ROOT.RooRealVar("n_cb_Dsp", "n of Crystal Ball (Dsp)", 3, 0.1, 20)

# Coefficients for combining PDFs
frac_Dp = ROOT.RooRealVar("frac_Dp", "fraction of Gaussian in Dp model", 0.5, 0, 1)
frac_Dsp = ROOT.RooRealVar("frac_Dsp", "fraction of Gaussian in Dsp model", 0.5, 0, 1)

# Create Crystal Ball PDFs
cb_Dp = ROOT.RooCBShape("cb_Dp", "Crystal Ball PDF (Dp)", x, mean_cb_Dp, sigma_cb_Dp, alpha_cb_Dp, n_cb_Dp)
cb_Dsp = ROOT.RooCBShape("cb_Dsp", "Crystal Ball PDF (Dsp)", x, mean_cb_Dsp, sigma_cb_Dsp, alpha_cb_Dsp, n_cb_Dsp)

# Create Gaussian PDF (same for both Dp and Dsp)
gaussian_Dp = ROOT.RooGaussian("gaussian_Dp", "Gaussian PDF (Dp)", x, mean_cb_Dp, sigma_gaussian)
gaussian_Dsp = ROOT.RooGaussian("gaussian_Dsp", "Gaussian PDF (Dsp)", x, mean_cb_Dsp, sigma_gaussian_Dsp)

# Create combined models (Gaussian + Crystal Ball)
model_Dp = ROOT.RooAddPdf("model_Dp", "Gaussian + Crystal Ball (Dp)", ROOT.RooArgList(gaussian_Dp, cb_Dp), ROOT.RooArgList(frac_Dp))
model_Dsp = ROOT.RooAddPdf("model_Dsp", "Gaussian + Crystal Ball (Dsp)", ROOT.RooArgList(gaussian_Dsp, cb_Dsp), ROOT.RooArgList(frac_Dsp))


# Create a simultaneous PDF
sim_pdf = ROOT.RooSimultaneous("sim_pdf", "Simultaneous fit", sample)
sim_pdf.addPdf(model_Dp, "Dp")
sim_pdf.addPdf(model_Dsp, "Dsp")

# Perform the fit
#result = sim_pdf.fitTo(combined_data, ROOT.RooFit.Range("Dp_range,Dsp_range"), ROOT.RooFit.NumCPU(4), ROOT.RooFit.Save())
result = sim_pdf.fitTo(combined_data, ROOT.RooFit.Range(fit_range[0], fit_range[1]), ROOT.RooFit.NumCPU(8), ROOT.RooFit.Save())
result.Print()



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

plot_x_range = (1.8, 1.95)
canvas_D_plus.cd(1)
#frame_D_plus = x.frame(ROOT.RooFit.Title("D+ fit"))
frame_D_plus = x.frame(plot_x_range[0], plot_x_range[1])
#frame_D_minus.GetXaxis().SetRangeUser(plot_x_range[0], plot_x_range[1])
slicedData_Dp = combined_data.reduce(Cut="sample==sample::Dp")
slicedData_Dp.plotOn(frame_D_plus, Name="data")
sim_pdf.plotOn(frame_D_plus, Name="Fitting",ProjWData=(sample, slicedData_Dp))
frame_D_plus.Draw("PE")

frame_D_plus.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.8, 0.65, 1.00, 0.90)
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
pullplot = x.frame(plot_x_range[0], plot_x_range[1])
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

#xmin1 = ctypes.c_double(fit_range[0])
#xmax1 = ctypes.c_double(fit_range[1])
xmin1 = ctypes.c_double(plot_x_range[0])
xmax1 = ctypes.c_double(plot_x_range[1])
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
####

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

plot_x_range = (1.89, 2.05)
canvas_D_minus.cd(1)
frame_D_minus = x.frame(plot_x_range[0],plot_x_range[1])
slicedData_Dm = combined_data.reduce(Cut="sample==sample::Dsp")
slicedData_Dm.plotOn(frame_D_minus, Name="data")
sim_pdf.plotOn(frame_D_minus, Name="Fitting",ProjWData=(sample, slicedData_Dm))
frame_D_minus.Draw("PE")
# frame_D_minus.GetXaxis().SetRangeUser(plot_x_range[0], plot_x_range[1])

frame_D_minus.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.8, 0.65, 1.00, 0.90)
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
pullplot = x.frame(plot_x_range[0], plot_x_range[1])
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

#min1 = ctypes.c_double(fit_range[0])
#xmax1 = ctypes.c_double(fit_range[1])
xmin1 = ctypes.c_double(plot_x_range[0])
xmax1 = ctypes.c_double(plot_x_range[1])
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

# f = ROOT.TFile(fitresult_name, "RECREATE")
# fit_result.Write("jykim")
# f.Close()
