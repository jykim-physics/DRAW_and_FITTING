import ROOT

input_file = ROOT.TFile.Open("tight_v2_240708_Kp_BCS_etapi0const_ccbar_output_00000_job402330223_00.root", "READ")
input_tree = input_file.Get("etapip_gg")

output_file = ROOT.TFile("output.root", "RECREATE")

interested_branches = ["Dp_M", "Dp_isSignal", "Dp_chiProb"]

# Disable all branches initially
input_tree.SetBranchStatus("*", 0)

# Enable only the interested branches
for branch in interested_branches:
    print(branch)
    input_tree.SetBranchStatus(branch, 1)

# Clone the tree structure withh the content
output_tree = input_tree.CloneTree()

output_tree.Write()
input_file.Close()
output_file.Close()

