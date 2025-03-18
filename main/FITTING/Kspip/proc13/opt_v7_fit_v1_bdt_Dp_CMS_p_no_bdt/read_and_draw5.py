import ROOT

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

root_file = ROOT.TFile("output_file_gg.root", "READ")
data_combined = root_file.Get("sweight")
data_combined.Print()

MC_root_file = ROOT.TFile("output_file_gg_MC15rd.root", "READ")
MC_combined = MC_root_file.Get("sweight")
MC_combined.Print()

cdata_mc = ROOT.TCanvas("cdata_mc", "Data and MC Histogram", 800, 600)

h_data = ROOT.TH1F("h_data", "Data Histogram", 50, 0, 1)
h_MC = ROOT.TH1F("h_MC", "MC Histogram", 50, 0, 1)

# Ensure histograms use SumW2 for error calculation
h_data.Sumw2()  # Enable SumW2 for data histogram
h_MC.Sumw2()  # Enable SumW2 for MC histogram

h_data.SetXTitle("BDT Score")  # Set X-axis title for data histogram
h_data.SetTitle("Data vs MC Comparison")  # Set overall title for data histogram

h_MC.SetXTitle("BDT Score")  # Set X-axis title for MC histogram
h_MC.SetTitle("Data vs MC Comparison")  # Set overall title for MC histogram

# Loop through data_combined (Data)
for i in range(data_combined.numEntries()):
    entry = data_combined.get(i)

    # Extract BDT value and weight
    BDT_value = entry.getRealValue("BDT")
    N_total_sw = entry.getRealValue("N_total_sw")

    # Apply the weight and N_total_sw
    total_weight = 1 * N_total_sw

    # Debugging: Print the BDT value and weight to check if they are correct
    if i % 10000 == 0:  # Print every 10000th entry for debugging
        print(f"Entry {i}: BDT_value = {BDT_value}, N_total_sw = {N_total_sw}, total_weight = {total_weight}")

    # Fill the histogram
    h_data.Fill(BDT_value, total_weight)

# Loop through MC_combined (MC)
for i in range(MC_combined.numEntries()):
    entry = MC_combined.get(i)

    # Extract BDT value and weight
    BDT_value = entry.getRealValue("BDT")
    N_total_sw = entry.getRealValue("N_total_sw")

    # Apply the weight and N_total_sw
    total_weight = 1 * N_total_sw

    # Debugging: Print the BDT value and weight to check if they are correct
    if i % 10000 == 0:  # Print every 10000th entry for debugging
        print(f"MC Entry {i}: BDT_value = {BDT_value}, N_total_sw = {N_total_sw}, total_weight = {total_weight}")

    # Fill the histogram
    h_MC.Fill(BDT_value, total_weight)

# Set line styles and colors for histograms
h_data.SetLineColor(ROOT.kBlue)  # Set color for data histogram
h_MC.SetLineColor(ROOT.kRed)  # Set color for MC histogram

# Draw the histograms (without x-axis error bars)
#h_data.SetMarkerStyle(20)  # Marker for data
h_data.SetMarkerColor(ROOT.kBlue)  # Color for markers
#h_MC.SetMarkerStyle(21)  # Marker for MC
h_MC.SetMarkerColor(ROOT.kRed)  # Color for markers

# Draw the histograms on the same canvas (without x-axis error bars)
h_MC.Draw("PE")
h_data.Draw("PE SAME")

# Add a legend and move it to the left
legend = ROOT.TLegend(0.2, 0.75, 0.4, 0.9)  # Adjusted position to move it to the left
#legend.AddEntry(h_data, "Data", "lep")  # "lep" for line and marker
#legend.AddEntry(h_MC, "MC", "lep")  # "lep" for line and marker
legend.AddEntry(h_data, "Data", "PE")  # "lep" for line and marker
legend.AddEntry(h_MC, "MC", "PE")  # "lep" for line and marker
legend.Draw()

# Save the canvas as an image
cdata_mc.SaveAs("data_and_mc_histogram.png")

# Close the ROOT files
root_file.Close()
MC_root_file.Close()

