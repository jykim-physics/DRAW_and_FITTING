import ROOT

# Open the ROOT files
root_file = ROOT.TFile("output_file_gg.root", "READ")
data_combined = root_file.Get("sweight")
data_combined.Print()

MC_root_file = ROOT.TFile("output_file_gg_MC15rd.root", "READ")
MC_combined = MC_root_file.Get("sweight")
MC_combined.Print()

# Create canvas for drawing both histograms
cdata_mc = ROOT.TCanvas("cdata_mc", "Data and MC Histogram", 800, 600)

# Create histograms for 'BDT' variable, range [0, 1], with a reasonable number of bins (e.g., 50)
h_data = ROOT.TH1F("h_data", "Data Histogram", 50, 0, 1)
h_MC = ROOT.TH1F("h_MC", "MC Histogram", 50, 0, 1)

# Loop through data_combined (Data)
for i in range(data_combined.numEntries()):
    entry = data_combined.get(i)

    # Extract BDT value and weight
    BDT_value = entry.getRealValue("BDT")
    #weight = entry.getRealValue("weight")
    N_total_sw = entry.getRealValue("N_total_sw")

    # Apply the weight and N_total_sw
    total_weight = 1 * N_total_sw

    # Fill the histogram
    h_data.Fill(BDT_value, total_weight)

# Loop through MC_combined (MC)
for i in range(MC_combined.numEntries()):
    entry = MC_combined.get(i)

    # Extract BDT value and weight
    BDT_value = entry.getRealValue("BDT")
    #weight = entry.getRealValue("weight")
    N_total_sw = entry.getRealValue("N_total_sw")

    # Apply the weight and N_total_sw
    total_weight = 1 * N_total_sw

    # Fill the histogram
    h_MC.Fill(BDT_value, total_weight)

# Set line styles and colors for histograms
h_data.SetLineColor(ROOT.kBlue)  # Set color for data histogram
h_MC.SetLineColor(ROOT.kRed)  # Set color for MC histogram

# Draw the histograms (with error bars)
h_data.SetMarkerStyle(20)  # Marker for data
h_data.SetMarkerColor(ROOT.kBlue)  # Color for markers
h_MC.SetMarkerStyle(21)  # Marker for MC
h_MC.SetMarkerColor(ROOT.kRed)  # Color for markers

# Draw the histograms on the same canvas
h_data.Draw("E1")  # "E1" for error bars and points (data)
h_MC.Draw("E1 SAME")  # "SAME" to overlay the MC histogram on the same canvas

# Add a legend
legend = ROOT.TLegend(0.7, 0.75, 0.9, 0.9)
legend.AddEntry(h_data, "Data", "lep")  # "lep" for line and marker
legend.AddEntry(h_MC, "MC", "lep")  # "lep" for line and marker
legend.Draw()

# Save the canvas as an image
cdata_mc.SaveAs("data_and_mc_histogram.png")

# Close the ROOT files
root_file.Close()
MC_root_file.Close()

