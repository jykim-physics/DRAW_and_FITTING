import ROOT
from ROOT import RooFit
import glob
import os

# Create a TChain and add all the ROOT files to it using glob
chain = ROOT.TChain("toymc")
files = glob.glob("v6_100_*.root")
for file in files:
    chain.Add(file)

# Create a directory to save PNG files
output_dir = "histograms"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Define the branch name to be processed
#branch_name = "pulls_Acp"
#branch_name = "pulls_Dm"
branch_name = "pulls_Dp"

# Create a histogram for the current branch
histogram = ROOT.TH1F(branch_name, branch_name, 50, -5, 5)  # Adjusted bin range for typical pulls distribution

# Fill the histogram with the data from the branch
chain.Draw(f"{branch_name}>>{branch_name}")

# Create a RooRealVar to represent the variable in the dataset
x = ROOT.RooRealVar(branch_name, branch_name, -5, 5)

# Create a RooDataHist from the TH1F histogram
data_hist = ROOT.RooDataHist("data_hist", "data_hist", ROOT.RooArgList(x), histogram)

# Define the parameters of the Gaussian
mean = ROOT.RooRealVar("mean", "mean of gaussian", 0, -2, 2)
sigma = ROOT.RooRealVar("sigma", "width of gaussian", 1, 0.1, 2)

# Define the Gaussian PDF
gauss = ROOT.RooGaussian("gauss", "gaussian PDF", x, mean, sigma)

# Fit the Gaussian to the data
r = gauss.fitTo(data_hist, RooFit.Save(1))
r.Print()

# Create a frame to draw the histogram and the fit result
frame = x.frame()
data_hist.plotOn(frame)
gauss.plotOn(frame)

# Create a canvas and draw the frame
canvas = ROOT.TCanvas(branch_name, branch_name, 800, 600)
frame.Draw()

# Remove x-axis label and modify the title
frame.SetXTitle("")
#frame.SetTitle("Acp pull")
frame.SetTitle(branch_name)

# Get the mean and sigma values with errors
mean_val = mean.getValV()
mean_err = mean.getError()
sigma_val = sigma.getValV()
sigma_err = sigma.getError()

# Display the mean and sigma values with errors on the canvas
pave_text = ROOT.TPaveText(0.6, 0.7, 0.9, 0.9, "NDC")
pave_text.AddText(f"#mu: {mean_val:.3f} #pm {mean_err:.3f}")
pave_text.AddText(f"#sigma: {sigma_val:.3f} #pm {sigma_err:.3f}")
pave_text.SetFillColor(0)
pave_text.Draw()

# Save the canvas as a PNG file
canvas.SaveAs(os.path.join(output_dir, f"fit_{branch_name}.png"))

# Save the modified histogram to the ROOT file
output_file = ROOT.TFile("histograms.root", "RECREATE")
histogram.Write()
output_file.Close()



