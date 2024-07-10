import ROOT
import glob

# Create a TChain and add all the ROOT files to it using glob
chain = ROOT.TChain("toymc")
files = glob.glob("v6_100_*.root")
for file in files:
    chain.Add(file)

# Create a RooRealVar for the branch we are interested in
pulls_Acp = ROOT.RooRealVar("pulls_Acp", "pulls_Acp", -10, 10)

# Create a RooDataSet from the TChain
data = ROOT.RooDataSet("data", "dataset with pulls_Acp", chain, ROOT.RooArgSet(pulls_Acp))

# Define the mean and sigma for the Gaussian
mean = ROOT.RooRealVar("mean", "mean of gaussian", 0, -5, 5)
sigma = ROOT.RooRealVar("sigma", "width of gaussian", 1, 0.1, 5)

# Create the Gaussian model
gauss = ROOT.RooGaussian("gauss", "gaussian PDF", pulls_Acp, mean, sigma)

# Fit the Gaussian model to the data
result = gauss.fitTo(data, ROOT.RooFit.Save())

# Create a frame for the variable
frame = pulls_Acp.frame(ROOT.RooFit.Title("Pulls_Acp Gaussian Fit"))

# Plot the data on the frame
data.plotOn(frame)

# Plot the Gaussian fit on the frame
gauss.plotOn(frame)

# Draw the frame on a canvas
canvas = ROOT.TCanvas("canvas", "Pulls_Acp Gaussian Fit", 800, 600)
frame.Draw()

# Save the plot to a file
canvas.SaveAs("pulls_Acp_fit_v6.png")

# Print the fit results
result.Print()

# Keep the GUI alive
# ROOT.gApplication.Run()
