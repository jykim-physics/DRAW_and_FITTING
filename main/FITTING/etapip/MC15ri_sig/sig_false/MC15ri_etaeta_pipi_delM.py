import ROOT
import glob
import ctypes

ROOT.gROOT.LoadMacro('/home/jykim/workspace/git/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()
file_name = "/share/storage/jykim/plots/MC15ri/etaeta/pipi/MC15ri_1M_etaeta_pipi_delM_tight_v1_false.png"


# Get the tree from the file
tree = "etaeta_pipi"
tree_name = "etaeta_pipi_tag"

# Define fitting variable and its range
fit_variable = "Dstarp_delM"
fit_var_name = "#Delta M [GeV/c^{2}]"
fit_range = (0.140, 0.160)
rank_var = tree + "_rank"
truth_var = "Dstarp_isSignal"
cuts = rank_var + "==1" + " && " + truth_var + "!=1"

# Create a RooRealVar for the fitting variable
x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
chiProb_rank = ROOT.RooRealVar(rank_var, rank_var, 0, 30)
truth_var = ROOT.RooRealVar(truth_var, truth_var, 0, 30)

# Create a TChain and add all ROOT files
mychain = ROOT.TChain(tree_name)
mychain.Add("/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15ri_sigMC/Dtoetaeta_pipipi_pipipi/240405_tight_v1_treefit_BCS_etapi0const/*.root")

# data = ROOT.RooDataSet("data","", ROOT.RooArgSet(x,y,z), ROOT.RooFit.Import(mychain), Cut=" D0_M>1.68 & D0_M<2.05 & Belle2Pi0Veto_75MeV > 0.022 ")
print(cuts)
before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,chiProb_rank,truth_var), cuts)


w_1 = ROOT.RooRealVar('w_1', 'w', 0,1)
w_1.setVal(1)
before_data.addColumn(w_1)
data = ROOT.RooDataSet(before_data.GetName(), before_data.GetTitle(),before_data, before_data.get(), '' ,  'w_1')
N_total = data.sumEntries()
print(N_total)



# Define parameters for the Gaussian PDF
mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean_gaussian", 0.1455, 0.14,0.15)
sigma_gaussian = ROOT.RooRealVar("sigma_gaussian", "sigma_gaussian", 0.0001, 0.00001, 0.1)
sigma_gaussian2 = ROOT.RooRealVar("sigma_gaussian2", "sigma_gaussian2", 0.0001, 0.00001, 0.1)

# Create Gaussian PDF
gaussian = ROOT.RooGaussian("gaussian", "gaussian", x, mean_gaussian, sigma_gaussian)
gaussian2 = ROOT.RooGaussian("gaussian2", "gaussian2", x, mean_gaussian, sigma_gaussian2)

# Define parameters for the bifurcated Gaussian PDF
#mean_bifurcated = ROOT.RooRealVar("mean_bifurcated", "mean_bifurcated", 1.86, 1.8, 1.9)
sigma_left = ROOT.RooRealVar("sigma_left", "sigma_left", 0.002, 0.00001, 0.01)
sigma_right = ROOT.RooRealVar("sigma_right", "sigma_right", 0.002, 0.00001, 0.01)

# Create bifurcated Gaussian PDF
bifurcated_gaussian = ROOT.RooBifurGauss("bifurcated_gaussian", "bifurcated_gaussian", x, mean_gaussian, sigma_left, sigma_right)

# Combine Gaussian and bifurcated Gaussian with a fraction parameter
frac = ROOT.RooRealVar("frac", "frac", 0.5, 0.0, 1.0)
frac2 = ROOT.RooRealVar("frac2", "frac2", 0.5, 0.0, 1.0)
model = ROOT.RooAddPdf("model", "model", ROOT.RooArgList(gaussian, gaussian2, bifurcated_gaussian), ROOT.RooArgList(frac,frac2))

# Perform the fit
result = model.fitTo(data, ROOT.RooFit.Range(fit_range[0], fit_range[1]), ROOT.RooFit.NumCPU(4))
#result.Print()

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
frame = x.frame(" ")

#frame.GetYaxis().SetTitleOffset(0.2)

data.plotOn(frame, ROOT.RooFit.Name("data1"), ROOT.RooFit.XErrorSize(0))


model.plotOn(frame, ROOT.RooFit.Name("bifurcated_gaussian"),ROOT.RooFit.Components("bifurcated_gaussian"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed))
model.plotOn(frame, ROOT.RooFit.Name("gauss"),ROOT.RooFit.Components("gaussian"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kGreen+2))
model.plotOn(frame, ROOT.RooFit.Name("gauss2"),ROOT.RooFit.Components("gaussian2"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kGreen+4))
model.plotOn(frame, ROOT.RooFit.Name("fitting"))

frame.Draw("PE")
frame.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.68, 0.65, 0.93, 0.9)
# leg1.SetFillColor(ROOT.kWhite)
leg1.SetFillColor(0)

    # leg1.SetHeader("The Legend title","C")
leg1.AddEntry("data1", "MC", "PE")
leg1.AddEntry("fitting", "Fit", "l")
leg1.AddEntry("bifurcated_gaussian", "bifurcated gauss", "l")
leg1.AddEntry("gauss", "gauss1", "l")
leg1.AddEntry("gauss2", "gauss2", "l")
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
