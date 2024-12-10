import ROOT
import glob
import ctypes
import os

ROOT.gROOT.LoadMacro('/home/jykim/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()
plot_file_name = "/share/storage/jykim/plots/MC15rd/etapip/pipipi/MC15rd_etapip_pipipi_Dp_M_opt_v3_novo_rhopeta.png"
result_name = "/share/storage/jykim/plots/MC15rd/etapip/pipipi/MC15rd_etapip_pipipi_Dp_M_opt_v3_novo_result_rhopeta.txt"

file_dir = os.path.dirname(plot_file_name)
result_dir = os.path.dirname(result_name)
os.makedirs(file_dir, exist_ok=True)
os.makedirs(result_dir, exist_ok=True)


# Get the tree from the file
tree_name = "etapip_pipipi_rhopeta"

# Define fitting variable and its range
fit_variable = "Dsp_Dp_M"
fit_var_name = "M(D^{+}) [GeV/c^{2}]"
fit_range = (1.7, 1.86)
#fit_range = (1.76, 2.05)
rank_var = tree_name + "_rank"
truth_var = "Dp_isSignal"
charge_var = "Dsp_Pip_charge"
cuts = rank_var + "==1"
#cuts_Dp = cuts + " && Pip_charge==1"
#cuts_Dm = cuts + " && Pip_charge==-1"
#cuts_Dp = "Pip_charge==1 && iCascDcyBrP_Dsp_0==2 && abs(Pip_genMotherPDG)==213 && abs(etapip_Eta_genMotherPDG)==431"
#cuts_Dm = "Pip_charge==-1 && iCascDcyBrCcP_Dsp_0==2 && abs(Pip_genMotherPDG)==213 && abs(etapip_Eta_genMotherPDG)==431"
#cuts_Dp = "Pip_charge==1 && abs(Pip_genMotherPDG)==213 && abs(etapip_Eta_genMotherPDG)==431"
#cuts_Dm = "Pip_charge==-1 && abs(Pip_genMotherPDG)==213 && abs(etapip_Eta_genMotherPDG)==431"
cuts_Dp = "Dsp_Pip_charge==1"
cuts_Dm = "Dsp_Pip_charge==-1"

# Create a RooRealVar for the fitting variable
x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
x.setRange("fitRange", fit_range[0], fit_range[1])
chiProb_rank = ROOT.RooRealVar(rank_var, rank_var, 0, 30)
truth_var = ROOT.RooRealVar(truth_var, truth_var, 0, 30)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)
#Dsp_topo = ROOT.RooRealVar("iCascDcyBrP_Dsp_0", "",-1,10000, "")
#Dsp_cc_topo = ROOT.RooRealVar("iCascDcyBrCcP_Dsp_0", "",-1,10000, "")
Pip_genMotherPDG  = ROOT.RooRealVar("Pip_genMotherPDG", "",-1000000,1000000, "")
etapip_Eta_genMotherPDG  = ROOT.RooRealVar("etapip_Eta_genMotherPDG", "",-1000000,1000000, "")

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/etapip_eteeta/MC15rd_etaetapip_loose_v3_241208_rhopeta"
cm_elements = ["15rd_eta_e7_18_4S_v3", "15rd_eta_e20_b26_v1", "15rd_eta_e20_e26_4S_v2", "15rd_eta_e21_5S_scan_v1", "15rd_eta_mori_off_v1"]

file_list = []
for element in cm_elements:
    pattern = f"{base_path}/{element}/{tree_name}/cc*.BCS.root"
    file_list += glob.glob(pattern)

print(file_list)
# Create a TChain and add all ROOT files
mychain = ROOT.TChain(tree_name)
for file_name in file_list:
    mychain.Add(file_name)

tree_name_cc = "etapip_pipipi"
mychain_cc = ROOT.TChain(tree_name_cc)
for file_name in file_list:
    mychain_cc.Add(file_name)


print(cuts_Dp)
#before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,truth_var, Pip_charge,Dsp_topo,Dsp_cc_topo, Pip_genMotherPDG, etapip_Eta_genMotherPDG), cuts_Dp)
#before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,truth_var, Pip_charge, Pip_genMotherPDG, etapip_Eta_genMotherPDG), cuts_Dp)
before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,Pip_charge), cuts_Dp)


w_1 = ROOT.RooRealVar('w_1', 'w', 0,1)
w_1.setVal(1/4)
before_data.addColumn(w_1)
data = ROOT.RooDataSet(before_data.GetName(), before_data.GetTitle(),before_data, before_data.get(), '' ,  'w_1')

print(cuts_Dm)
#before_data_cc = ROOT.RooDataSet("data_cc","", mychain_cc, ROOT.RooArgSet(x,truth_var, Pip_charge, Dsp_topo,Dsp_cc_topo, Pip_genMotherPDG, etapip_Eta_genMotherPDG), cuts_Dm)
#before_data_cc = ROOT.RooDataSet("data_cc","", mychain_cc, ROOT.RooArgSet(x,truth_var, Pip_charge,  Pip_genMotherPDG, etapip_Eta_genMotherPDG), cuts_Dm)
before_data_cc = ROOT.RooDataSet("data_cc","", mychain_cc, ROOT.RooArgSet(x,Pip_charge), cuts_Dm)
before_data_cc.addColumn(w_1)
data_cc = ROOT.RooDataSet(before_data_cc.GetName(), before_data_cc.GetTitle(),before_data_cc, before_data_cc.get(), '' ,  'w_1')

data.append(data_cc)

N_total = data.sumEntries()
print(N_total)

mean = ROOT.RooRealVar("mean", "Mean", 1.7, 1.65, 1.75)
sigma = ROOT.RooRealVar("sigma", "Sigma", 0.05, 0.001, 0.1)
tail = ROOT.RooRealVar("tail", "Tail", 0.2, 0.001, 0.5)
#mean = ROOT.RooRealVar("mean", "Mean", 1.7, 1.65, 1.71445)
#sigma = ROOT.RooRealVar("sigma", "Sigma", 0.05, 0.001, 0.0743477)
#tail = ROOT.RooRealVar("tail", "Tail", 0.2, 0.001, 0.436177)

# Create Novosibirsk PDF
model  = ROOT.RooNovosibirsk("CB_left", "Novosibirsk PDF", x, mean, sigma, tail)

mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0, -1, 1)
sigma_gaussian = ROOT.RooRealVar("sigma_gaussian", "sigma of Gaussian", 0.01, 0.0001, 1)

# Create a Gaussian distribution
gaussian = ROOT.RooGaussian("gaussian", "Gaussian PDF", x, mean_gaussian, sigma_gaussian)

# Convolute the Johnson distribution with Gaussian
#model = ROOT.RooFFTConvPdf("CB_left", "Convolution of Johnson and Gaussian", x, Novo, gaussian)

# Define parameters for the 1st-order polynomial PDF
a0 = ROOT.RooRealVar("a0", "a0", 0.0, -1.0, 1.0)
a1 = ROOT.RooRealVar("a1", "a1", 0.0, -1.0, 1.0)

# Create 1st-order polynomial PDF
polynomial = ROOT.RooPolynomial("polynomial", "polynomial", x, ROOT.RooArgList(a0, a1))

# Combine the two PDFs
fraction = ROOT.RooRealVar("fraction", "fraction", 0.5, 0.0, 1.0)
#model = ROOT.RooAddPdf("model", "model", ROOT.RooArgList(CB_left, polynomial), ROOT.RooArgList(fraction))
#model = CB_lef

# Perform the fit
result = model.fitTo(data, ROOT.RooFit.Range("fitRange"), ROOT.RooFit.NumCPU(4), ROOT.RooFit.Save())
result.Print()

# Print the full fit result
#result.Print()

# Open a text file in write mode
with open(result_name, "w") as f:

    # Print the full fit result to the file
    f.write("Full fit result summary:\n")
    result.Print("v")  # Verbose print (prints more details)

    # Alternatively, write specific attributes to the file
    f.write("\nSpecific fit result details:\n")
    f.write(f"Status: {result.status()}\n")
    f.write(f"Covariance quality: {result.covQual()}\n")
    f.write(f"EDM (Estimated Distance to Minimum): {result.edm()}\n")
    f.write(f"Min NLL: {result.minNll()}\n")

    # Access and write parameter values and errors to the file
    f.write("\nFitted Parameters:\n")
    params = result.floatParsFinal()  # This returns the final fitted parameters
    for i in range(params.getSize()):
        param = params[i]
        f.write(f"{param.GetName()} = {param.getVal()} ± {param.getError()}\n")

    # Optionally print a completion message
    f.write("\nFit result saved successfully.\n")

# The file is automatically closed after the 'with' block

# Plot the result
#canvas = ROOT.TCanvas("canvas", "canvas", 800, 555)
canv = ROOT.TCanvas("canvas", "canvas", 700, 640)
xlow = ctypes.c_double()
ylow = ctypes.c_double()
xup = ctypes.c_double()
yup = ctypes.c_double()

canv.GetPad(0).GetPadPar(xlow, ylow, xup, yup)
canv.Divide(1,2)

xlow = xlow.value
ylow = ylow.value
xup = xup.value
yup = yup.value

upPad = canv.GetPad(1)
upPad.SetPad(xlow, ylow+0.25*(yup-ylow),xup,yup)

dwPad = canv.GetPad(2)
dwPad.SetPad(xlow, ylow,xup,ylow+0.25*(yup-ylow))

canv.cd(1)
frame = x.frame()

#frame.GetYaxis().SetTitleOffset(0.2)

data.plotOn(frame, ROOT.RooFit.Name("data1"), ROOT.RooFit.XErrorSize(0))


#model.plotOn(frame, ROOT.RooFit.Name("Signal"),ROOT.RooFit.Components("CB_left"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed))
model.plotOn(frame, ROOT.RooFit.Name("fitting"))

frame.Draw("PE")
frame.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.68, 0.65, 0.93, 0.9)
# leg1.SetFillColor(ROOT.kWhite)
leg1.SetFillColor(0)

    # leg1.SetHeader("The Legend title","C")
leg1.AddEntry("data1", "MC", "PE")
leg1.AddEntry("fitting", "Fit", "l")
#leg1.AddEntry("Signal", "Signal", "l")
# leg1.AddEntry("fitx_bkg3", "bkg3", "l")

# leg1.SetTextSize(0.05)
# leg1.SetTextAlign(13)

leg1.SetBorderSize(0)
leg1.Draw()

hpull = frame.pullHist()
hpull.SetFillStyle(1001)
hpull.SetFillColor(1);
for i in range(0,hpull.GetN()):#(int i=0;i<hpull.GetN();++i):
    hpull.SetPointError(i,0.0,0.0,0.0,0.0)
pullplot = x.frame()
pullplot.SetTitle("")
pullplot.addPlotable(hpull,"BE")
    # pullplot.addPlotable(hpull,"PE")

pullplot.SetYTitle("Pull")
pullplot.GetXaxis().SetTitleSize(0)
pullplot.GetYaxis().SetTitleSize(0.22)
pullplot.GetYaxis().CenterTitle(True)
pullplot.GetYaxis().SetTitleOffset(0.2)
pullplot.SetMinimum(-4.)
pullplot.SetMaximum(4.)
pullplot.GetXaxis().SetLabelSize(0.15)
pullplot.GetYaxis().SetLabelSize(0.105)
canv.cd(2)
pullplot.Draw()

xmin1 = ctypes.c_double(fit_range[0])
xmax1 = ctypes.c_double(fit_range[1])
line = ROOT.TLine(xmin1,0.0,xmax1,0.0)
line1 = ROOT.TLine(xmin1,3.0,xmax1,3.0)
line2 = ROOT.TLine(xmin1,-3.0,xmax1,-3.0)

line.SetLineColor(ROOT.kGray+1)
line.SetLineWidth(3)
line1.SetLineColor(ROOT.kBlack)
line2.SetLineColor(ROOT.kGray+1)
line1.SetLineStyle(2)
line2.SetLineStyle(2)
line.Draw("SAME")
line1.Draw("SAME")
line2.Draw("SAME")

canv.Update()

canv.Draw()
canv.SaveAs(plot_file_name)

# Save the final figure as .png
#canv.SaveAs("fit_result_with_pull.png")
