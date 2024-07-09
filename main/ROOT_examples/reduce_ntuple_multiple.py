import ROOT

# List of input ROOT files
input_files = [
    "tight_v2_240708_Kp_BCS_etapi0const_ccbar_output_00000_job402330223_00.root",
    "tight_v2_240708_Kp_BCS_etapi0const_ccbar_output_00000_job402330223_00.root",
    # Add more files as needed
]

# Create a TChain to combine multiple ROOT files
chain = ROOT.TChain("etapip_gg")
for file_name in input_files:
    chain.Add(file_name)

output_file = ROOT.TFile("output.root", "RECREATE")

interested_branches = ["Dp_M", "Dp_isSignal", "Dp_chiProb"]

# Disable all branches initially
chain.SetBranchStatus("*", 0)

# Enable only the interested branches
for branch in interested_branches:
    chain.SetBranchStatus(branch, 1)

# Create an output TTree with only the selected branches
output_tree = chain.CloneTree(0)  # Clone structure only, no data

# Fill the output tree with the content of the selected branches
output_tree.CopyEntries(chain)

# Write the output tree to the new file
output_tree.Write()
output_file.Close()

