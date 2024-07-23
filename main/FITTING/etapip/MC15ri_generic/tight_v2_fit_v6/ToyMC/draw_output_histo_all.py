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

# Loop through all the branches and create histograms
for branch in branches:
    branch_name = branch.GetName()
    print(branch_name)
    
    # Create a histogram for the current branch
    histogram = ROOT.TH1F(branch_name, branch_name, 100, 0, 0)
    
    # Fill the histogram with the data from the branch
    chain.Draw(f"{branch_name}>>{branch_name}")
    
    # Write the histogram to the ROOT file
    histogram.Write()

    # Create a canvas and draw the histogram
    canvas = ROOT.TCanvas(branch_name, branch_name, 800, 600)
    histogram.Draw()
    
    # Save the canvas as a PNG file
    canvas.SaveAs(os.path.join(output_dir, f"{branch_name}.png"))

# Close the output file
output_file.Close()
