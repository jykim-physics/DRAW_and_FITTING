import ROOT

# Step 1: Open the ROOT file containing the TTree
input_file = ROOT.TFile("output_data_combined.root", "READ")

# Step 2: Get the TTree (ntuple) from the ROOT file
mychain = input_file.Get("etapip_gg_sw")  # Replace "customTreeName" with the name of your TTree

if not mychain:
    print("TTree not found!")
else:
    # Step 3: Define the variables used in the dataset
    # Create ROOT RooRealVar objects for each branch (variable)
    x = ROOT.RooRealVar("Dp_M", "Dp_M", 1.7, 2.1)
    Pip_charge = ROOT.RooRealVar("Pip_charge", "Pip_charge", -3, 3)
    Pip_p = ROOT.RooRealVar("Pip_p", "Pip_p", 0, 10)  # Adjust range as needed
    N_total_sw = ROOT.RooRealVar("Nbkg_total_sw", "N_total_sw", -10, 10)

    # Step 4: Define the cuts or conditions (optional, if needed)
    cuts_Dp = "Dp_M>1.7 & Dp_M<2.1"  # This is just an example condition, can be adjusted

    # Step 5: Create the RooDataSet with the desired variables and cuts
    before_data = ROOT.RooDataSet("data", "", mychain, ROOT.RooArgSet(x,  Pip_p,  N_total_sw), cuts_Dp)
    #before_data = ROOT.RooDataSet("data", "", mychain, ROOT.RooArgSet(x, Pip_charge, Pip_p,  N_total_sw), cuts_Dp)
    before_data.Print()

    data = ROOT.RooDataSet(before_data.GetName(), before_data.GetTitle(),before_data, before_data.get(), '' ,  'Nbkg_total_sw')
    data.Print()

    # Step 6: Create a RooPlot for the variable Pip_p
    #frame = Pip_p.frame(ROOT.RooFit.Title("Pip_p distribution weighted by sWeight"))
    frame = x.frame(ROOT.RooFit.Title("Pip_p distribution weighted by sWeight"))

    # Step 7: Plot the data with the weight variable sWeight
    data.plotOn(frame)

    # Step 8: Draw the plot on a canvas
    canvas = ROOT.TCanvas("canvas", "Canvas", 800, 600)
    frame.Draw()

    # Step 9: Save the plot as a PNG file
    canvas.SaveAs("Pip_p_weighted_by_sWeight_RooDataSet_plot.png")

# Step 10: Close the ROOT file
input_file.Close()

print("Weighted plot saved as Pip_p_weighted_by_sWeight_RooDataSet_plot.png")

