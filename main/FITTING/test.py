import ROOT
import glob

ROOT.gROOT.LoadMacro('Belle2Style.C')
ROOT.SetBelle2Style()


# Get the tree from the file
tree_name = "etapip_gg"

# Define fitting variable and its range
fit_variable = "Dp_M"
fit_range = (1.7, 2)

# Create a RooRealVar for the fitting variable
Dp_M = ROOT.RooRealVar(fit_variable, fit_variable, fit_range[0], fit_range[1])

# Create a TChain and add all ROOT files
chain = ROOT.TChain("etapip_gg")
chain.Add("/media/jykim/T7_2/storage/Ntuples_ghi_2/MC15ri_sigMC/Dptoetapip_gg/240405_tight_v1_treefit_BCS_etapi0const/*.root")

# Create a RooDataSet directly from the TChain
combined_data = ROOT.RooDataSet("combined_data", "combined_data", chain, ROOT.RooArgSet(Dp_M))


# Define parameters for the double-sided Crystal Ball PDF
mean = ROOT.RooRealVar("mean", "mean", 1.95, 1.8, 2.0)
sigma = ROOT.RooRealVar("sigma", "sigma", 0.02, 0.001, 0.1)
alphaL = ROOT.RooRealVar("alphaL", "alphaL", 1.0, 0.0, 10.0)
nL = ROOT.RooRealVar("nL", "nL", 1.0, 0.0, 10.0)
alphaR = ROOT.RooRealVar("alphaR", "alphaR", 1.0, 0.0, 10.0)
nR = ROOT.RooRealVar("nR", "nR", 1.0, 0.0, 10.0)

# Create double-sided Crystal Ball PDF
CB_left = ROOT.RooCrystalBall("CB_left", "CB_left", Dp_M, mean, sigma, alphaL, nL, alphaR, nR)
#CB_right = ROOT.RooCBShape("CB_right", "CB_right", Dp_M, mean, sigma, alphaR, nR)

# Define parameters for the 1st-order polynomial PDF
a0 = ROOT.RooRealVar("a0", "a0", 0.0, -1.0, 1.0)
a1 = ROOT.RooRealVar("a1", "a1", 0.0, -1.0, 1.0)

# Create 1st-order polynomial PDF
polynomial = ROOT.RooPolynomial("polynomial", "polynomial", Dp_M, ROOT.RooArgList(a0, a1))

# Combine the two PDFs
fraction = ROOT.RooRealVar("fraction", "fraction", 0.5, 0.0, 1.0)
model = ROOT.RooAddPdf("model", "model", ROOT.RooArgList(CB_left, polynomial), ROOT.RooArgList(fraction))



# Define parameters for the double-sided Crystal Ball PDF
# (Assuming you have already defined these parameters)

# Define parameters for the 1st-order polynomial PDF
# (Assuming you have already defined these parameters)

# Combine the two PDFs
# (Assuming you have already defined the combined model)

# Perform the fit
result = model.fitTo(combined_data, ROOT.RooFit.Range(fit_range[0], fit_range[1]), ROOT.RooFit.NumCPU(6))

# Plot the result
canvas = ROOT.TCanvas("canvas", "canvas", 800, 555)
#canvas.Divide(1, 2)  # Divide canvas into two pads

# Upper pad for main plot
#canvas.cd(1)
#pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
#pad1.Draw()
#pad1.cd()
frame = Dp_M.frame()
combined_data.plotOn(frame)
model.plotOn(frame)
model.plotOn(frame, ROOT.RooFit.Components("CB_left"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed))
frame.Draw()

# Lower pad for pull distribution
#canvas.cd(2)
#pad2 = ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
#pad2.Draw()
#pad2.cd()
#frame_pull = Dp_M.frame(ROOT.RooFit.Title("Pull Distribution"))
#pull_hist = frame.pullHist()  # Get the pull histogram
#frame_pull.addPlotable(pull_hist, "P")
#frame_pull.SetMinimum(-5)  # Adjust as needed
#frame_pull.SetMaximum(5)   # Adjust as needed
#frame_pull.Draw()

# Save the final figure as .png
canvas.SaveAs("fit_result_with_pull.png")
