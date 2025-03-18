import ROOT

# Open the ROOT files
root_file = ROOT.TFile("output_file_gg.root", "READ")
data_combined = root_file.Get("sweight")
data_combined.Print()

MC_root_file = ROOT.TFile("output_file_gg_MC15rd.root", "READ")
MC_combined = MC_root_file.Get("sweight")
MC_combined.Print()

# Create canvases for plotting
cdata = ROOT.TCanvas("cdata", "Data Histogram", 800, 600)
cMC = ROOT.TCanvas("cMC", "MC Histogram", 800, 600)

# Create a histogram for 'BDT' variable, range [0, 1], with a reasonable number of bins (e.g., 50)
h_data = ROOT.TH1F("h_data", "Data Histogram", 50, 0, 1)
h_MC = ROOT.TH1F("h_MC", "MC Histogram", 50, 0, 1)

# Loop through data_combined (Data)
for i in range(data_combined.numEntries()):
    entry = data_combined.get(i)

    # Extract BDT value and weight
    BDT_value = entry.getRealValue("BDT")
    weight = entry.getRealValue("w_1")
    N_total_sw = entry.getRealValue("N_total_sw")
    #print(f"{BDT_value}")
    #print(f"{weight}")
    #print(f"{N_total_sw}")

    # Apply the weight and N_total_sw
    total_weight = weight * N_total_sw

    # Fill the histogram
    h_data.Fill(BDT_value, total_weight)

# Loop through MC_combined (MC)
for i in range(MC_combined.numEntries()):
    entry = MC_combined.get(i)

    # Extract BDT value and weight
    BDT_value = entry.getRealValue("BDT")
    weight = entry.getRealValue("w_1")
    N_total_sw = entry.getRealValue("N_total_sw")

    # Apply the weight and N_total_sw
    total_weight = weight * N_total_sw

    # Fill the histogram
    h_MC.Fill(BDT_value, total_weight)

# Draw the histograms
cdata.cd()
h_data.SetLineColor(ROOT.kBlue)  # Set color for data histogram
h_data.Draw("PE")

cMC.cd()
h_MC.SetLineColor(ROOT.kRed)  # Set color for MC histogram
h_MC.Draw("PE")

# Save the canvases as images
cdata.SaveAs("data_histogram.png")
cMC.SaveAs("mc_histogram.png")

# Close the ROOT files
root_file.Close()
MC_root_file.Close()

