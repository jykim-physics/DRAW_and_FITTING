import ROOT

# Step 1: Open the ROOT file
input_file = ROOT.TFile("output_data_combined.root", "READ")

# Step 2: Access the TTree by its name
tree = input_file.Get("etapip_gg_sw")  # Replace "customTreeName" with the name you used

if not tree:
    print("TTree not found!")
else:
    # Step 3: Create a TCanvas for drawing
    canvas = ROOT.TCanvas("canvas", "Canvas", 800, 600)  # You can adjust the canvas size

    # Step 4: Draw the Pip_p branch weighted by the sWeight variable
    tree.Draw("Pip_p >> hist(100, min_value, max_value)", "sWeight")

    # Optional: Add histogram formatting (title, axis labels, etc.)
    hist = ROOT.gDirectory.Get("hist")  # Get the histogram created in the Draw command
    #hist.SetTitle("Pip_p distribution weighted by sWeight")
    #hist.GetXaxis().SetTitle("Pip_p")
    #hist.GetYaxis().SetTitle("Weighted Entries")

    # Step 5: Save the plot as a PNG file
    canvas.SaveAs("Pip_p_weighted_by_sWeight_plot.png")

# Step 6: Close the ROOT file
input_file.Close()

print("Weighted plot saved as Pip_p_weighted_by_sWeight_plot.png")

