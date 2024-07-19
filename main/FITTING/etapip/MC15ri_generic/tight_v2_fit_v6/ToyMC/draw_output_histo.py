import ROOT
import glob
import os

# Create a TChain and add all the ROOT files to it using glob
chain = ROOT.TChain("toymc")
files = glob.glob("v6_100_*.root")
for file in files:
    chain.Add(file)

# Get the list of branches (columns) in the tree
branches = chain.GetListOfBranches()

# Create a new ROOT file to save the histograms
output_file = ROOT.TFile("histograms.root", "RECREATE")

# Create a directory to save PNG files
output_dir = "histograms"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Define the branch name to be processed
branch_name = "pulls_Acp"

# Create a histogram for the current branch
histogram = ROOT.TH1F(branch_name, branch_name, 100, -5, 5)  # Adjusted bin range for typical pulls distribution

# Fill the histogram with the data from the branch
chain.Draw(f"{branch_name}>>{branch_name}")

# Create a RooRealVar to represent the variable in the dataset
x = ROOT.RooRealVar(branch_name, branch_name, -5, 5)

# Create a RooDataHist from the TH1F histogram
data_hist = ROOT.RooDataHist("data_hist", "data_hist", ROOT.RooArgList(x), histogram)

# Define the parameters of the Gaussian
mean = ROOT.RooRealVar("mean", "mean of gaussian", 0, -5, 5)
sigma = ROOT.RooRealVar("sigma", "width of gaussian", 1, 0.1, 5)

# Define the Gaussian PDF
gauss = ROOT.RooGaussian("gauss", "gaussian PDF", x, mean, sigma)

# Fit the Gaussian to the data
gauss.fitTo(data_hist)

# Create a frame to draw the histogram and the fit result
frame = x.frame()
data_hist.plotOn(frame)
gauss.plotOn(frame)

# Write the histogram to the ROOT file
histogram.Write()

# Create a canvas and draw the frame
canvas = ROOT.TCanvas(branch_name, branch_name, 800, 600)
frame.Draw()

# Save the canvas as a PNG file
canvas.SaveAs(os.path.join(output_dir, f"{branch_name}.png"))

# Close the output file
output_file.Close()
