import ROOT

# Load the Belle2 style
ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

# Open ROOT files
root_file = ROOT.TFile("output_file_gg.root", "READ")
data_combined = root_file.Get("sweight")
MC_root_file = ROOT.TFile("output_file_gg_MC15rd.root", "READ")
MC_combined = MC_root_file.Get("sweight")

# Create canvas for the histograms and ratio plot
cdata_mc = ROOT.TCanvas("cdata_mc", "Data and MC Comparison", 800, 800)

title = ROOT.TLatex()
title.SetTextSize(0.04)  # Adjust size
title.SetTextAlign(23)  # Center alignment
title.DrawLatexNDC(0.5, 0.95, "Data vs MC Comparison")  # Position at the top

pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1)
pad2 = ROOT.TPad("pad2", "pad2", 0, 0.0, 1, 0.3)
pad1.SetBottomMargin(0.02)  # No bottom margin for the upper plot
#pad2.SetTopMargin(0)  # No top margin for the lower plot
pad2.SetTopMargin(0.04)  # No top margin for the lower plot
pad1.Draw()
pad2.Draw()

# Create histograms
h_data = ROOT.TH1F("h_data", "Data Histogram", 50, 0, 1)
h_MC = ROOT.TH1F("h_MC", "MC Histogram", 50, 0, 1)

# Enable SumW2 for error calculation
h_data.Sumw2()
h_MC.Sumw2()

# Set titles
#h_data.SetXTitle("BDT Score")
h_data.SetTitle("Data vs MC Comparison")
#h_MC.SetXTitle("BDT Score")

# Fill the histograms with data and MC entries
for i in range(data_combined.numEntries()):
    entry = data_combined.get(i)
    BDT_value = entry.getRealValue("BDT")
    N_total_sw = entry.getRealValue("N_total_sw")
    h_data.Fill(BDT_value, N_total_sw)

for i in range(MC_combined.numEntries()):
    entry = MC_combined.get(i)
    BDT_value = entry.getRealValue("BDT")
    N_total_sw = entry.getRealValue("N_total_sw")
    h_MC.Fill(BDT_value, N_total_sw)

# Normalize the histograms
#h_data.Scale(1.0 / h_data.Integral())
#h_MC.Scale(1.0 / h_MC.Integral())

# Set line and marker styles
h_data.SetLineColor(ROOT.kBlue)
h_MC.SetLineColor(ROOT.kRed)
h_data.SetMarkerColor(ROOT.kBlue)
h_MC.SetMarkerColor(ROOT.kRed)

# Draw histograms on the upper pad
pad1.cd()
h_MC.Draw("PE")  # MC histogram
h_data.Draw("PE SAME")  # Overlay data histogram

# Add legend
legend = ROOT.TLegend(0.2, 0.75, 0.4, 0.9)
legend.AddEntry(h_data, "Data", "PE")
legend.AddEntry(h_MC, "MC", "PE")
legend.Draw()

# Create the ratio plot (Data / MC) on the lower pad
pad2.cd()
h_ratio = h_data.Clone("h_ratio")
h_ratio.Divide(h_MC)  # Ratio of data to MC

# Set the axis titles and range for the ratio plot
#h_ratio.SetXTitle("BDT Score")
h_ratio.SetYTitle("Data / MC")
h_ratio.SetMinimum(0)  # Set lower limit of the ratio plot
h_ratio.SetMaximum(2)  # Set upper limit of the ratio plot (adjust as needed)

# Adjust title and label sizes
h_ratio.GetXaxis().SetTitleSize(0.12)  # Increase X-axis title size
h_ratio.GetYaxis().SetTitleSize(0.12)  # Increase Y-axis title size
h_ratio.GetXaxis().SetLabelSize(0.1)  # Increase X-axis label size
h_ratio.GetYaxis().SetLabelSize(0.10)  # Increase Y-axis label size
h_ratio.GetXaxis().SetTitleOffset(0.85)  # Adjust X-axis title offset
#h_ratio.GetYaxis().SetTitleOffset(0.4)  # Adjust Y-axis title offset
h_ratio.GetYaxis().SetTitleOffset(0.6)  # Adjust Y-axis title offset

# Draw the ratio plot with error bars
#h_ratio.SetMarkerStyle(21)
h_ratio.SetMarkerColor(ROOT.kBlack)
h_ratio.Draw("PE")

# Add a reference gray line at y = 1
line = ROOT.TLine(h_ratio.GetXaxis().GetXmin(), 1, h_ratio.GetXaxis().GetXmax(), 1)
#line.SetLineColor(ROOT.kGray)
line.SetLineStyle(2)  # Dashed line style
line.Draw()

# Save the canvas as an image
cdata_mc.SaveAs("data_and_mc_ratio.png")

# Close the ROOT files
root_file.Close()
MC_root_file.Close()

