import ROOT

# Step 1: Open the ROOT file
input_file = ROOT.TFile("output_data_combined.root", "READ")

# Step 2: Access the TTree by its name
# If you assigned a custom name, use that name; otherwise, try the default one.
tree = input_file.Get("etapip_gg_sw")  # Replace "customTreeName" with the name you used

if not tree:
    print("TTree not found!")
else:
    canvas = ROOT.TCanvas("canvas", "Canvas", 800, 600)
    # Step 3: Draw the Dp_M variable from the tree
    # Assuming the variable you're interested in is called 'Dp_M'
    tree.Draw("Dp_M")

    canvas.SaveAs("Dp_M_plot.png")

# Step 4: Close the ROOT file
input_file.Close()


