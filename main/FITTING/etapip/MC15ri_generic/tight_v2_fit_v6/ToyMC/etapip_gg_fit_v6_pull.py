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
pull_var = ROOT.RooRealVar("pull", "pull", 100,-6, 6)

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

# Create a frame to draw the histogram
frame = pull_var.frame(ROOT.RooFit.Title("Acp Pull Distribution"))

# Plot the data in the frame
pull_data.plotOn(frame)

# Create a canvas and draw the frame
c_sig = ROOT.TCanvas("c_sig", "c_sig", 800, 600)
frame.Draw()

c_sig.SaveAs("pull_distribution.png")
# Show the canvas
c_sig.Draw()