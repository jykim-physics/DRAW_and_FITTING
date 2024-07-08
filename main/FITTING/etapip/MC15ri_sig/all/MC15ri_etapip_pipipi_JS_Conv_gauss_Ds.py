import ROOT
import glob
import ctypes

ROOT.gROOT.LoadMacro('/home/jykim/workspace/git/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()
file_name = "/share/storage/jykim/plots/MC15ri/etapip/pipipi/MC15ri_1M_etapip_pipipi_Dp_M_tight_v2_johnson_conv_gauss_Ds.png"


# Get the tree from the file
tree_name = "etapip_pipipi"

# Define fitting variable and its range
fit_variable = "Dp_M"
fit_var_name = "M(D^{+}) [GeV/c^{2}]"
fit_range = (1.76, 1.95)
#fit_range = (1.67, 2.05)
#fit_range = (1.78, 1.93)
fit_range = (1.76, 2.05)
rank_var = tree_name + "_rank"
truth_var = "Dp_isSignal"
charge_var = "Pip_charge"
cuts = rank_var + "==1" 
cuts_Dp = cuts + " && Pip_charge==1"
cuts_Dm = cuts + " && Pip_charge==-1"

# Create a RooRealVar for the fitting variable
x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
chiProb_rank = ROOT.RooRealVar(rank_var, rank_var, 0, 30)
truth_var = ROOT.RooRealVar(truth_var, truth_var, 0, 30)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)

# Create a TChain and add all ROOT files
mychain = ROOT.TChain(tree_name)
mychain.Add("/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15ri_sigMC/Dsptoetapip_pipipi/240419_tight_v2_Kp_BCS_etapi0const/*.root")
#mychain.Add("/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15ri_sigMC/Dptoetapip_gg_cc/240419_tight_v2_Kp_BCS_etapi0const/*.root")

tree_name_cc = "etapip_pipipi"
mychain_cc = ROOT.TChain(tree_name_cc)
mychain_cc.Add("/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15ri_sigMC/Dsptoetapip_pipipi_cc/240419_tight_v2_Kp_BCS_etapi0const/*.root")


# data = ROOT.RooDataSet("data","", ROOT.RooArgSet(x,y,z), ROOT.RooFit.Import(mychain), Cut=" D0_M>1.68 & D0_M<2.05 & Belle2Pi0Veto_75MeV > 0.022 ")
print(cuts)
before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,chiProb_rank,truth_var, Pip_charge), cuts_Dp)


w_1 = ROOT.RooRealVar('w_1', 'w', 0,1)
w_1.setVal(1)
before_data.addColumn(w_1)
data = ROOT.RooDataSet(before_data.GetName(), before_data.GetTitle(),before_data, before_data.get(), '' ,  'w_1')

before_data_cc = ROOT.RooDataSet("data_cc","", mychain_cc, ROOT.RooArgSet(x,chiProb_rank,truth_var, Pip_charge), cuts_Dm)
before_data_cc.addColumn(w_1)
data_cc = ROOT.RooDataSet(before_data_cc.GetName(), before_data_cc.GetTitle(),before_data_cc, before_data_cc.get(), '' ,  'w_1')

data.append(data_cc)

N_total = data.sumEntries()
print(N_total)

mean_johnson = ROOT.RooRealVar("mean_johnson", "mean of Johnson", 1.96, 1.91, 2.1)
sigma_johnson = ROOT.RooRealVar("sigma_johnson", "sigma of Johnson", 0.01, 0.00001, 0.5)
gamma = ROOT.RooRealVar("gamma", "gamma of Johnson", 0.1, 0.001, 10)
delta = ROOT.RooRealVar("delta", "delta of Johnson", 0.1, 0.001, 10)
mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0, -1, 1)
sigma_gaussian = ROOT.RooRealVar("sigma_gaussian", "sigma of Gaussian", 0.01, 0.0001, 1)

# Create a Johnson distribution
johnson = ROOT.RooJohnson("johnson", "Johnson PDF", x, mean_johnson, sigma_johnson, gamma, delta)

# Create a Gaussian distribution
gaussian = ROOT.RooGaussian("gaussian", "Gaussian PDF", x, mean_gaussian, sigma_gaussian)

# Convolute the Johnson distribution with Gaussian
johnson_gauss = ROOT.RooFFTConvPdf("johnson_gauss", "Convolution of Johnson and Gaussian", x, johnson, gaussian)

#mean_gaussian2 = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0, -1, 1)
sigma_gaussian2 = ROOT.RooRealVar("sigma_gaussian2", "sigma of Gaussian", 0.01, 0.0001, 1)
gaussian2 = ROOT.RooGaussian("gaussian2", "Gaussian PDF", x, mean_johnson, sigma_gaussian2)

# Define parameters for the 1st-order polynomial PDF
#a0 = ROOT.RooRealVar("a0", "a0", 0.0, -1.0, 1.0)
#a1 = ROOT.RooRealVar("a1", "a1", 0.0, -1.0, 1.0)

# Create 1st-order polynomial PDF
#polynomial = ROOT.RooPolynomial("polynomial", "polynomial", x, ROOT.RooArgList(a0, a1))

# Combine the two PDFs
fraction = ROOT.RooRealVar("fraction", "fraction", 0.5, 0.0, 1.0)

model = ROOT.RooAddPdf("CB_left", "model", ROOT.RooArgList(johnson_gauss, gaussian2), ROOT.RooArgList(fraction))
#model = CB_lef

# Perform the fit
result = model.fitTo(data, ROOT.RooFit.Range(fit_range[0], fit_range[1]), ROOT.RooFit.NumCPU(4))
#result.Print()

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
frame = x.frame(" ")

#frame.GetYaxis().SetTitleOffset(0.2)

data.plotOn(frame, ROOT.RooFit.Name("data1"), ROOT.RooFit.XErrorSize(0))


model.plotOn(frame, ROOT.RooFit.Name("johnson_gauss"),ROOT.RooFit.Components("johnson_gauss"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kGreen+2))
model.plotOn(frame, ROOT.RooFit.Name("gaussian2"),ROOT.RooFit.Components("gaussian2"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed))
model.plotOn(frame, ROOT.RooFit.Name("fitting"))

frame.Draw("PE")
frame.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.23, 0.60, 0.53, 0.9)
# leg1.SetFillColor(ROOT.kWhite)
leg1.SetFillColor(0)

    # leg1.SetHeader("The Legend title","C")
leg1.AddEntry("data1", "MC", "PE")
leg1.AddEntry("fitting", "Fit", "l")
leg1.AddEntry("gaussian2", "Gauss", "l")
leg1.AddEntry("johnson_gauss", "Covoluted Johnson", "l")

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
canv.SaveAs(file_name)

# Save the final figure as .png
#canv.SaveAs("fit_result_with_pull.png")