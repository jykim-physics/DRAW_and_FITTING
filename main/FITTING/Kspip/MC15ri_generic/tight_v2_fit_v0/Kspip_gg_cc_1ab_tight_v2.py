import ROOT
from ROOT import RooFit
import glob
import ctypes
import os

file_name = "/share/storage/jykim/plots/MC15ri/Kspip/generic/MC15ri_1ab_Kspip_cc_fit_tight_v2_fitv0.png"
fitresult_name = "/share/storage/jykim/plots/MC15ri/Kspip/generic/fitresult/MC15ri_1ab_Kspip_cc_fit_tight_v2.root"
dir_path = os.path.dirname(file_name)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)
dir_path = os.path.dirname(fitresult_name)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)


ROOT.gROOT.LoadMacro('/home/jykim/workspace/git/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

base_file_loc =  '/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15ri_generic/MC15ri_Kspip_tight_v2_240420/'

#loc_ccbar = base_file_loc + 'ccbar/tight_v2_240420_ccbar_output_021*.root'
loc_ccbar = base_file_loc + 'ccbar/*.root'
# loc_ccbar = base_file_loc + 'topo/resultfile/result_antiKstar/standard.root'
loc_uubar = base_file_loc + 'uubar/*.root'
loc_ddbar = base_file_loc + 'ddbar/*.root'
loc_ssbar = base_file_loc + 'ssbar/*.root'
loc_charged = base_file_loc + 'charged/*.root'
loc_mixed = base_file_loc + 'mixed/*.root'
loc_taupair = base_file_loc + 'taupair/*.root'

file_list = [loc_ccbar,loc_uubar,loc_uubar,loc_ssbar,loc_charged,loc_mixed,loc_taupair]
#file_list = [loc_ccbar,loc_charged,loc_mixed]
#file_list = [loc_ccbar,loc_mixed]

# Get the tree from the file
tree_name = "Ks"

mychain = ROOT.TChain(tree_name)

for i in file_list:
    mychain.Add(i)

print(file_list)


# Define variable and its range
fit_variable = "Dp_M"
fit_var_name = "M(D^{+}) [GeV/c^{2}]"
#fit_range = (1.76, 2.05)
fit_range = (1.82, 1.92)
rank_var = tree_name + "_rank"
truth_var = "Dp_isSignal"
charge_var = "Pih_charge"

# Cuts
cuts = rank_var + "==1" 
cuts += " && " + charge_var + "==-1"

# Create RooRealVar
x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
x.setBins(70)
chiProb_rank = ROOT.RooRealVar(rank_var, rank_var, 0, 30)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)


print(cuts)
before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,chiProb_rank,Pip_charge), cuts)


w_1 = ROOT.RooRealVar('w_1', 'w', 0,1)
w_1.setVal(1)
before_data.addColumn(w_1)
data = ROOT.RooDataSet(before_data.GetName(), before_data.GetTitle(),before_data, before_data.get(), '' ,  'w_1')
N_total = data.sumEntries()
print(N_total)

# Define parameters for the double-sided Crystal Ball PDF
mean = ROOT.RooRealVar("mean", "mean", 1.86, 1.84, 1.9)

# Create double-sided Crystal Ball PDF
sigma_gauss = ROOT.RooRealVar("sigma_gauss", "sigma", 0.005, 0.0001, 0.1)
gauss = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma_gauss)

sigma_gauss2 = ROOT.RooRealVar("sigma_gauss2", "sigma", 0.001, 0.0001, 0.1)
gauss2 = ROOT.RooGaussian("gauss2", "gauss2", x, mean, sigma_gauss2)

sig_fraction = ROOT.RooRealVar("sig_fraction", "fraction", 0.5, 0.0, 1.0)
sig_model = ROOT.RooAddPdf("sig_model", "sig_model", ROOT.RooArgList(gauss, gauss2),ROOT.RooArgList(sig_fraction))

x_bkg1_Cheby_c0 = ROOT.RooRealVar("x_bkg1_Cheby_c0", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c1 = ROOT.RooRealVar("x_bkg1_Cheby_c1", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c2 = ROOT.RooRealVar("x_bkg1_Cheby_c2", "c0",0.0, -1.0, 1.0)

#bkg_model = ROOT.RooChebychev("bkg_model", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1, x_bkg1_Cheby_c2))
bkg_model = ROOT.RooPolynomial("bkg_model", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1, x_bkg1_Cheby_c2))


nsig = ROOT.RooRealVar("nsig","# signal events",N_total*0.1,0,N_total)
nbkg1 = ROOT.RooRealVar("nbkg1","# bkg events",N_total*0.01,0, N_total)
#nDs = ROOT.RooRealVar("nDs","# bkg events",N_total*0.8,0, N_total)

#extended_model = ROOT.RooAddPdf("extended_model", "x_model", ROOT.RooArgSet(sig_model,bkg_model, Ds_model), ROOT.RooArgSet(nsig, nbkg1, nDs))
extended_model = ROOT.RooAddPdf("extended_model", "x_model", ROOT.RooArgSet(sig_model,bkg_model), ROOT.RooArgSet(nsig, nbkg1))

#r = extended_model.fitTo(data,NumCPU=4, Extended=ROOT.kTRUE,PrintLevel=-1, Save=1,SumW2Error=True)
r = extended_model.fitTo(data,  RooFit.Extended(True), RooFit.PrintLevel(3), RooFit.Save(1),RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4))
#r = extended_model.fitTo(data, ROOT.RooFit.PrintLevel(-1), Save=1,SumW2Error=True)

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

data.plotOn(frame, ROOT.RooFit.Name("data"), ROOT.RooFit.XErrorSize(0))


#model.plotOn(frame, ROOT.RooFit.Name("Signal"),ROOT.RooFit.Components("CB_left"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed))
extended_model.plotOn(frame, ROOT.RooFit.Name("Signal"),ROOT.RooFit.Components("sig_model"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed))
extended_model.plotOn(frame, ROOT.RooFit.Name("Background"),ROOT.RooFit.Components("bkg_model"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kGreen+2))
#extended_model.plotOn(frame, ROOT.RooFit.Name("Ds+"),ROOT.RooFit.Components("Ds_model"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kViolet))

extended_model.plotOn(frame, ROOT.RooFit.Name("Fitting"))

frame.Draw("PE")
frame.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.2, 0.65, 0.45, 0.90)
# leg1.SetFillColor(ROOT.kWhite)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)
    # leg1.SetHeader("The Legend title","C")
leg1.AddEntry("data", "MC", "PE")
leg1.AddEntry("Fitting", "Fit", "l")
leg1.AddEntry("Signal", "Signal", "l")
leg1.AddEntry("Background", "Bkg", "l")
#leg1.AddEntry("Ds+", "D_{s}^{+}", "l")

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

f = ROOT.TFile(fitresult_name, "RECREATE")
r.Write("jykim")
f.Close()


