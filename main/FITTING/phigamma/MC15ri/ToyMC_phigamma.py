import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ROOT
import ctypes
import math
try:
#     plt.style.use('belle2')
    plt.style.use('belle2_serif')
#     plt.style.use('belle2_modern')
except OSError:
    print("Please install belle2 matplotlib style")   
px = 1/plt.rcParams['figure.dpi']

from main.data_tools.extract_ntuples import get_pd, get_np
from main.data_tools.extract_Nevents import get_Nevents

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/Belle2Style.C')
ROOT.SetBelle2Style()

base_file_loc =  '/media/jykim/T7/storage/01_recon/massvetov2_optimzed_sigext_1ab_sigbkg/'

loc_ccbar = base_file_loc + 'ccbar/recon_udst_*.root'
# loc_ccbar = base_file_loc + 'topo/resultfile/result_antiKstar/standard.root'
loc_uubar = base_file_loc + 'uubar/recon_udst_*.root'
loc_ddbar = base_file_loc + 'ddbar/recon_udst_*.root'
loc_ssbar = base_file_loc + 'ssbar/recon_udst_*.root'
loc_charged = base_file_loc + 'charged/recon_udst_*.root'
loc_mixed = base_file_loc + 'mixed/recon_udst_*.root'
loc_taupair = base_file_loc + 'taupair/recon_udst_*.root'

file_list = [loc_ccbar,loc_uubar,loc_uubar,loc_ssbar,loc_charged,loc_mixed,loc_taupair]


loc_ccbar_CC = base_file_loc + 'ccbar/recon_udst_*.root/phi_cc'
# loc_ccbar = base_file_loc + 'topo/resultfile/result_antiKstar/standard.root'
loc_uubar_CC = base_file_loc + 'uubar/recon_udst_*.root/phi_cc'
loc_ddbar_CC = base_file_loc + 'ddbar/recon_udst_*.root/phi_cc'
loc_ssbar_CC = base_file_loc + 'ssbar/recon_udst_*.root/phi_cc'
loc_charged_CC = base_file_loc + 'charged/recon_udst_*.root/phi_cc'
loc_mixed_CC = base_file_loc + 'mixed/recon_udst_*.root/phi_cc'
loc_taupair_CC = base_file_loc + 'taupair/recon_udst_*.root/phi_cc'


file_list += [loc_ccbar_CC,loc_uubar_CC,loc_uubar_CC,loc_ssbar_CC,loc_charged_CC,loc_mixed_CC,loc_taupair_CC]

mychain = ROOT.TChain("phi")
# mychain = ROOT.TChain("phi_cc")

for i in file_list:
    mychain.Add(i)
    
yrange = (-1, 1)
x = ROOT.RooRealVar("D0_M", "M(D^{0}) [GeV/c^{2}]", 1.68, 2.05, "")
y = ROOT.RooRealVar("D0_cosHel_0", "cos#theta_{H}", yrange[0], yrange[1], "")
# z = ROOT.RooRealVar("Belle2Pi0Veto_75MeV", "M(D^{0}) [GeV/c^{2}]",0,10, "")
z = ROOT.RooRealVar("dM_pi0_75MeV", "M(D^{0}) [GeV/c^{2}]",0,10, "")


# data = ROOT.RooDataSet("data","", ROOT.RooArgSet(x,y,z), ROOT.RooFit.Import(mychain), Cut=" D0_M>1.68 & D0_M<2.05 & Belle2Pi0Veto_75MeV > 0.022 ")
data = ROOT.RooDataSet("data","", ROOT.RooArgSet(x,y,z), ROOT.RooFit.Import(mychain), Cut=" D0_M>1.68 & D0_M<2.05 & dM_pi0_75MeV > 0.023 ")

N_total = data.sumEntries()
print(N_total)
# hist_data = ROOT.RooDataSet("hist_data","", ROOT.RooArgSet(x,y,z), ROOT.RooFit.Import(mychain), Cut="D0_M>1.78 & D0_M<1.91 & Belle2Pi0Veto_75MeV > 0.022 ")

ROOT.RooClassFactory.makePdf("MyPdf_xsquared_nopara", "x", "", "x*x")
ROOT.RooClassFactory.makePdf("MyPdf_one_minus_squared", "y", "", "1-y*y")

ROOT.gROOT.ProcessLineSync(".x MyPdf_xsquared_nopara.cxx+")
ROOT.gROOT.ProcessLineSync(".x MyPdf_one_minus_squared.cxx+")

f = ROOT.TFile.Open("/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/phigamma/1D_1ab_sigbkg/phig_MC15ri_half1M_signalMC_fitresult.root")
result_object = ROOT.gDirectory.Get("phig")
f.Close()

fit_args = result_object.floatParsFinal()
x_sig_alpha= ROOT.RooRealVar("x_sig_alpha", "",  fit_args.at(0).getVal()) 
x_sig_mean = ROOT.RooRealVar("x_sig_mean", "",  fit_args.at(1).getVal()) 
# x_sig_mean = ROOT.RooRealVar("x_sig_mean", "mean of gaussians", 1.863,1.86, 1.88)
x_sig_n_CB = ROOT.RooRealVar("x_sig_n_CB", "",  fit_args.at(2).getVal()) 
x_sig_sig1frac = ROOT.RooRealVar("x_sig_sig1frac", "",  fit_args.at(3).getVal()) 
x_sig_sigma1 = ROOT.RooRealVar("x_sig_sigma1", "",  fit_args.at(4).getVal()) 
x_sig_sigma2 = ROOT.RooRealVar("x_sig_sigma2", "",  fit_args.at(5).getVal()) 
# x_sig_sigma2 = ROOT.RooRealVar("x_sig_sigma2", "",  0.01,0.001,0.1) 

f = ROOT.TFile.Open("/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/phigamma/1D_1ab_sigbkg/phig_MC15ri_1ab_Vpi0_fitresult.root")
result_object2 = ROOT.gDirectory.Get("phig")
f.Close()
fit_args2 = result_object2.floatParsFinal()

#V pi0
x_bkg1_alpha = ROOT.RooRealVar("x_bkg1_alpha", "",  fit_args2.at(0).getVal()) 
x_bkg1_mean = ROOT.RooRealVar("x_bkg1_mean", "",  fit_args2.at(1).getVal()) 
x_bkg1_n_CB = ROOT.RooRealVar("x_bkg1_n_CB", "",  fit_args2.at(2).getVal()) 
x_bkg1_sigma2 = ROOT.RooRealVar("x_bkg1_sigma2", "",  fit_args2.at(3).getVal()) 

#Others
f = ROOT.TFile.Open("/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/phigamma/1D_1ab_sigbkg/phig_MC15ri_1ab_others_fitresult.root")
result_object3 = ROOT.gDirectory.Get("phig")
f.Close()

fit_args3 = result_object3.floatParsFinal()
x_bkg2frac1 = ROOT.RooRealVar("x_bkg2frac1", "fraction of component 1 in signal", fit_args3.at(0).getVal())
x_bkg2_tau = ROOT.RooRealVar("x_bkg2_tau", "",  fit_args3.at(1).getVal()) 
x_bkg2_c0 = ROOT.RooRealVar("x_bkg2_c0", "c0",fit_args3.at(2).getVal()) 
x_bkg2_c1 = ROOT.RooRealVar("x_bkg2_c1", "c0",fit_args3.at(3).getVal())


####################
#D0_M
# x.setBins(50)
x_sig_sig1 = ROOT.RooGaussian("x_sig_sig1", "Signal component 1", x, x_sig_mean, x_sig_sigma1)
x_sig_sig2 =  ROOT.RooCBShape("x_sig_sig2", "Signal component 2", x, x_sig_mean, x_sig_sigma2, x_sig_alpha, x_sig_n_CB)

x_sig_model = ROOT.RooAddPdf("x_sig_model", "model", [x_sig_sig1, x_sig_sig2], x_sig_sig1frac)

#### Construct bkg model for x
#phi pi0
 
# x_bkg1_1 = ROOT.RooGaussian("x_bkg1_1", "Signal component 1", x, x_bkg1_mean, x_bkg1_sigma1)
# x_bkg1_2 = ROOT.RooCBShape("x_bkg1_2", "Signal component 2", x, x_bkg1_mean, x_bkg1_sigma2, x_bkg1_alpha, x_bkg1_n_CB)
# x_bkg1_model = ROOT.RooAddPdf("x_bkg1_model", "Signal1", [x_bkg1_1, x_bkg1_2], x_bkg1frac1)

x_bkg1_model = ROOT.RooCBShape("x_bkg1_model", "Signal component 2", x, x_bkg1_mean, x_bkg1_sigma2, x_bkg1_alpha, x_bkg1_n_CB)


####BKG2
# remaining
x_bkg2_2 = ROOT.RooPolynomial("x_bkg2_2", "Signal component 1", x,ROOT.RooArgList(x_bkg2_c0, x_bkg2_c1))
x_bkg2_3 = ROOT.RooExponential("x_bkg2_3", "Signal component 1", x, x_bkg2_tau)
x_bkg2frac1 = ROOT.RooRealVar("x_bkg2frac1", "fraction of component 1 in signal", 0.5, 0.0, 1.0)
x_bkg2_model = ROOT.RooAddPdf("x_bkg2_model", "model", [x_bkg2_2, x_bkg2_3], x_bkg2frac1)




################
#D0_cosHel_0
# yrange=(-1,1)
# y = ROOT.RooRealVar("cos#theta_{H}", "cos#theta_{H}", yrange[0], yrange[1], "")
# y.setBins(50)
ROOT.RooClassFactory.makePdf("MyPdf_one_minus_squared", "y", "", "1-y*y")
y_sig_model = ROOT.MyPdf_one_minus_squared("y_sig_model", "y_sig", y)

#### Construct bkg model for y
#phi pi0
ROOT.RooClassFactory.makePdf("MyPdf_xsquared_nopara", "x", "", "x*x")
y_bkg1_model = ROOT.MyPdf_xsquared_nopara("y_bkg1_model", "y_bkg1", y)

#remaining
# y_bkg2_c0 = ROOT.RooRealVar("y_bkg2_c0", "c0",0.5, -1,1)
# y_bkg2_c1 = ROOT.RooRealVar("y_bkg2_c1", "c1",0.2, -1,1)

y_bkg2_c0 = ROOT.RooRealVar("y_bkg2_c0", "c0",-1.1456e-01)
y_bkg2_c1 = ROOT.RooRealVar("y_bkg2_c1", "c1",3.5924e-01)

y_bkg2_model= ROOT.RooPolynomial("y_bkg2_model", "Signal component 1", y, ROOT.RooArgList(y_bkg2_c0, y_bkg2_c1))

####BKG3
# y_bkg3_c0 = ROOT.RooRealVar("y_bkg3_c0", "c0",0.1, 0,1.)
# y_bkg3_c1 = ROOT.RooRealVar("y_bkg3_c1", "c1",0.5, 0,1.)
# y_bkg3_c2 = ROOT.RooRealVar("y_bkg3_c2", "c2",-0.3, -1.,0.)
# y_bkg3_model = ROOT.RooChebychev("y_bkg3_model", "Signal component 1", y, ROOT.RooArgList(y_bkg3_c0, y_bkg3_c1, y_bkg3_c2))
# y_bkg3_model = ROOT.MyPdf_xsquared_nopara("y_bkg3_model", "y_bkg3", y)

#### Combine bkg models
# y_phipi0frac = ROOT.RooRealVar("y_phipi0frac", "fraction of component 1 in signal", 0.2, 0.0, 1.0)
# y_bkg_model = ROOT.RooAddPdf("y_bkg_model", "Signal", [y_bkg1_model, y_bkg2_model], y_phipi0frac)


################
bkg1_xy_model = ROOT.RooProdPdf("bkg1_xy_model","bkg1_xy_model",ROOT.RooArgSet(x_bkg1_model,y_bkg1_model))
bkg2_xy_model = ROOT.RooProdPdf("bkg2_xy_model","bkg2_xy_model",ROOT.RooArgSet(x_bkg2_model,y_bkg2_model))


sig_model = ROOT.RooProdPdf("sig_model","sig_xy_model",ROOT.RooArgSet(x_sig_model, y_sig_model))



####################################
# construct signal + bkg pdf
nsig = ROOT.RooRealVar("nsig","# signal events",N_total*0.01,0,N_total*0.5)
nbkg1 = ROOT.RooRealVar("nbkg1","# bkg events",N_total*0.8,0, N_total)
nbkg2 = ROOT.RooRealVar("nbkg2","# bkg events",N_total*0.1,0, N_total*0.5)
# nbkg3 = ROOT.RooRealVar("nbkg3","# bkg events",300,0., len(D0_M_np_data))


# extended_model = ROOT.RooAddPdf("extended_model", "x_model", ROOT.RooArgSet(sig_model,bkg1_xy_model,bkg2_xy_model,bkg3_xy_model), ROOT.RooArgSet(nsig, nbkg1, nbkg2, nbkg3))
extended_model = ROOT.RooAddPdf("extended_model", "x_model", ROOT.RooArgSet(sig_model,bkg1_xy_model,bkg2_xy_model), ROOT.RooArgSet(nsig, nbkg1, nbkg2))

#####################################
# # Associated nsig/nbkg as expected number of events with sig/bkg
# esig = ROOT.RooExtendPdf("esig", "extended signal pdf", sig_xy_model, nsig)
# ebkg = ROOT.RooExtendPdf("ebkg", "extended background pdf", bkg_xy_model, nbkg)
 
# # Sum extended components without coefs
# # -------------------------------------------------------------------------
 
# # Construct sum of two extended pdf (no coefficients required)
# extended_model = ROOT.RooAddPdf("extended_model", "bkg_sig", [ebkg, esig ])


# datax = ROOT.RooDataSet.from_numpy({"M(D^{0})": np_data['D0_M']}, [x])
# datay = ROOT.RooDataSet.from_numpy({"cos#theta_{H}": np_data['D0_cosHel_0']}, [y])

canv = ROOT.TCanvas("Canvas", "Canvas", 700, 640)

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

    # r = sig.fitTo(data,NumCPU=12, Range=(1.84,1.89))
# r = sig_xy_model.fitTo(data,NumCPU=12, Range=(1.70,1.98))
r = extended_model.fitTo(data,NumCPU=12, Extended=ROOT.kTRUE, PrintLevel=-1)

    # r.Print()

mcstudy = ROOT.RooMCStudy(
    extended_model,
    {x,y},
    Binned=True,
    Silence=True,
    Extended=True,
    FitOptions=dict(Save=True, PrintEvalErrors=0, NumCPU=12),
)
 
# Generate and fit events
# ---------------------------------------------
 
# Generate and fit 1000 samples of Poisson(nExpected) events
mcstudy.generateAndFit(100)
 
# Explore results of study
# ------------------------------------------------
# ------------------------------------------------
 
# Make plots of the distributions of mean, error on mean and the pull of
# mean
frame1 = mcstudy.plotParam(nsig, Bins=50)
frame2 = mcstudy.plotError(nsig, Bins=50)
frame3 = mcstudy.plotPull(nsig, Bins=50, FitGauss=False)
pullMean = ROOT.RooRealVar("pullMean","",0,-10,10)
pullSigma = ROOT.RooRealVar("pullSigma","",1,0.1,5)
#pullMean.setPlotLabel("pull #mu")   # // optional (to get nicer plot labels if you want)
#pullSigma.setPlotLabel("pull #sigma")
pullMean.setPlotLabel("#mu")   # // optional (to get nicer plot labels if you want)
pullSigma.setPlotLabel("#sigma")

pullGauss = ROOT.RooGaussian("pullGauss", "", frame3.getPlotVar() , pullMean, pullSigma)
r_pull = pullGauss.fitTo(mcstudy.fitParDataSet(),NumCPU=12,PrintLevel=-1)
# Plot distribution of minimized likelihood
frame4 = mcstudy.plotNLL(Bins=50)
 
# Make some histograms from the parameter dataset
# hh_cor_a0_s1f = mcstudy.fitParDataSet().createHistogram("hh", x_sig_sigma2, YVar=x_sig_mean)
# hh_cor_a0_a1 = mcstudy.fitParDataSet().createHistogram("hh", x_sig_mean, YVar=x_sig_sigma2)
 
# Access some of the saved fit results from individual toys
corrHist000 = mcstudy.fitResult(0).correlationHist("c000")
corrHist127 = mcstudy.fitResult(1).correlationHist("c001")
corrHist953 = mcstudy.fitResult(2).correlationHist("c002")
 
# Draw all plots on a canvas
# ROOT.gStyle.SetPalette(1)
# ROOT.gStyle.SetOptStat(0)
c = ROOT.TCanvas("rf801_mcstudy", "rf801_mcstudy", 1500, 500)
c.Divide(3, 1)
c.cd(1)
# ROOT.gPad.SetLeftMargin(0.15)
# frame3.GetYaxis().SetTitleOffset(1.4)
pullGauss.plotOn(frame3)
#pullGauss.paramOn(frame3,xmin=0.55, xmax=0.75, ymax=0.9, sigDigits=3)
pullGauss.paramOn(frame3, ROOT.RooFit.Layout(0.60, 0.80, 0.9), ROOT.RooFit.Format("NE",ROOT.RooFit.AutoPrecision(1)))

frame3.Draw("PE")
#
c.cd(2)
# ROOT.gPad.SetLeftMargin(0.15)
# frame1.GetYaxis().SetTitleOffset(1.4)
frame1.Draw("PE")
c.cd(3)
# ROOT.gPad.SetLeftMargin(0.15)
# frame2.GetYaxis().SetTitleOffset(1.4)
frame2.Draw("PE")
# c.cd(4)
# #ROOT.gPad.SetLeftMargin(0.15)
# frame4.GetYaxis().SetTitleOffset(1.4)
# frame4.Draw("PE")
c.SaveAs("rf801_mcstudy.png")
 
# Make ROOT.RooMCStudy object available on command line after
# macro finishes
ROOT.gDirectory.Add(mcstudy)
