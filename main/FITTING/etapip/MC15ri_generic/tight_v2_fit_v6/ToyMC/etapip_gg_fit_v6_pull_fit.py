import ROOT
import numpy as np
import json
import glob
import os

# Directory containing the JSON files
json_dir = './'  # Replace with your directory path if different
json_pattern = 'v6_100_*.json'  # Pattern to match all relevant JSON files

# Use glob to find all files matching the pattern
json_files = glob.glob(os.path.join(json_dir, json_pattern))

# Define RooRealVar for pulls
pull_var = ROOT.RooRealVar("pull", "pull", -10, 10)  # Adjust the range if needed
x = ROOT.RooRealVar("x", "pull", -10, 10)  # Adjust the range if needed

# Create an empty RooDataSet to hold all the pull values
pull_data = ROOT.RooDataSet("pull_data", "Pull Distribution Data", ROOT.RooArgSet(pull_var))

# Process each JSON file
for json_file in json_files:
    with open(json_file, 'r') as f:
        data = json.load(f)

    n_gen_Acp = data['n_gen_Acp']
    n_recon_Acp = data['n_recon_Acp']
    n_recon_err_Acp = data['n_recon_err_Acp']

    # Calculate pulls
    pulls_Acp = [(val - Ngen) / err for Ngen, val, err in zip(n_gen_Acp, n_recon_Acp, n_recon_err_Acp)]
    pulls_Acp = np.array(pulls_Acp)

    # Fill the RooDataSet with pull values
    for pull in pulls_Acp:
    
        pull_var.setVal(pull)
        pull_data.add(ROOT.RooArgSet(pull_var))

# Create a Gaussian PDF
mean = ROOT.RooRealVar("mean", "mean of Gaussian", 0, -4, 4)
sigma = ROOT.RooRealVar("sigma", "width of Gaussian", 0.1, 0.000001, 1)
gauss = ROOT.RooGaussian("gauss", "Gaussian PDF", x, mean, sigma)

# Perform the fit to the data
gauss.fitTo(pull_data)

# Create a frame to draw the histogram
frame = x.frame(ROOT.RooFit.Title("Acp Pull Distribution"))

# Plot the data in the frame
pull_data.plotOn(frame)

# Plot the fitted Gaussian on the frame
gauss.plotOn(frame)

# Create a canvas and draw the frame
c_sig = ROOT.TCanvas("c_sig", "c_sig", 800, 600)
frame.Draw()

# Save the canvas as an image
c_sig.SaveAs("pull_distribution_with_fit.png")

# Show the canvas
c_sig.Draw()
