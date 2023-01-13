import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ROOT
import ctypes
try:
#     plt.style.use('belle2')
    plt.style.use('belle2_serif')
#     plt.style.use('belle2_modern')
except OSError:
    print("Please install belle2 matplotlib style")   
px = 1/plt.rcParams['figure.dpi']


from main.data_tools.extract_ntuples import get_pd, get_np

ROOT.RooClassFactory.makePdf("MyPdf_xsquared_nopara", "x", "", "x*x")
#ROOT.RooClassFactory.makePdf("MyPdf_xsquared", "x,c0", "", "c0*x*x")

ROOT.gROOT.ProcessLineSync(".x MyPdf_xsquared_nopara.cxx+")


file_loc = '/media/jykim/T7/storage/01_recon/pi0veto_calib/D2kmpippi0/ntuple/tightcut_control_recon_mdst_30M.root'
base_filter = 'D0_M>1.70 && D0_M<1.98 && antiKstarpi0_rank_Dstp==1'

tree = 'control'
signal_variables = ['D0_M','D0_cosHel_0']

np_data = get_np(file=file_loc, tree='control',base_filter=base_filter,variables=signal_variables)

xrange = (-1,1)
file_name='test_coshel_extended.png'

x = ROOT.RooRealVar("cos#theta_{H}", "cos#theta_{H}", xrange[0], xrange[1], "")
x.setBins(50)
#Signal##########################
#c0 = ROOT.RooRealVar("c0", "c0",0.5, -1,1)
#sig_model = ROOT.MyPdf_xsquared_nopara("sig_model", "pdf", x, c0)
sig_model = ROOT.MyPdf_xsquared_nopara("sig_model", "pdf", x)

#Bkg################################
#1 rho+K-
b1_mean = ROOT.RooRealVar("b1_mean", "mean of gaussians", 0.5,0, 1.)
b1_sigma1 = ROOT.RooRealVar("b1_sigma1", "width of gaussians", 0.5,0,1)
b1_sigma2 = ROOT.RooRealVar("b1_sigma2", "width of gaussians", 0.2,0,1)
b1_sigma3 = ROOT.RooRealVar("b1_sigma3", "width of gaussians", 0.2,0,1)

b1_1 = ROOT.RooGaussian("b1_1", "Signal component 1", x, b1_mean, b1_sigma1)
b1_2 = ROOT.RooGaussian("b1_2", "Signal component 1", x, b1_mean, b1_sigma2)
b1_3 = ROOT.RooGaussian("b1_3", "Signal component 1", x, b1_mean, b1_sigma3)
# sig2 = ROOT.RooCBShape("sig2", "Signal component 2", x, mean, sigma2, alpha, n_CB)
# sig3 = ROOT.RooNovosibirsk("sig3", "Signal component 3", x, mean, Novo_width, Novo_tail)
b1_frac = ROOT.RooRealVar("b1_frac", "fraction of component 1 in signal", 0.2, 0.0, 1.0)
b1_sum1 = ROOT.RooAddPdf("sig_sum1", "Signal1", [b1_1, b1_2], b1_frac)

b2_frac = ROOT.RooRealVar("b2_2frac", "fraction of component 2 in signal", 0.2, 0.0, 1.0)
bkg_model1 = ROOT.RooAddPdf("sig", "Signal", [b1_3, b1_sum1], b2_frac)
##############################
#6 K-rho1700+
bkg2_file_loc = '/media/jykim/T7/storage/01_recon/pi0veto_calib/D2kmrho1700p/ntuple/tightcut_control_recon_mdst_1M.root'
#base_filter = 'D0_M>1.70 && D0_M<1.98 && abs(antiKstar_InvM - 0.89555)<0.06 && abs(Dstarp_Q - 0.00593)<0.0006 && Dstarp_CMS_p>2.3 && antiKstarpi0_rank_Dstp==1'
bkg2_base_filter = 'D0_M>1.70 && D0_M<1.98 && antiKstarpi0_rank_Dstp==1 '
bkg2_signal_variables = ['D0_M','D0_cosHel_0']

bkg2_np_data = get_np(file=bkg2_file_loc, tree='control',base_filter=bkg2_base_filter,variables=bkg2_signal_variables)

#dummy_x = ROOT.RooRealVar("cos#theta_{H}_dummy", "cos#theta_{H}", xrange[0], xrange[1], "")
#x.setBins(50)

bkg2_data = ROOT.RooDataSet.from_numpy({"cos#theta_{H}": bkg2_np_data['D0_cosHel_0']}, [x])

expHist_data = bkg2_data.binnedClone()
bkg_model2 = ROOT.RooHistPdf("bkg_model2","histopd", x , expHist_data, 2)
##############################
#2 K*- pi+
b3_tau = ROOT.RooRealVar("b3_tau", "tau",-2, -10,0)
bkg_model3= ROOT.RooExponential("bkg_mdoel3", "Signal component 1", x, b3_tau)
##############################
#3 K1430- pi+
b4_c0 = ROOT.RooRealVar("b4_c0", "c0",0.5, -1,1)
b4_c1 = ROOT.RooRealVar("b4_c1", "c1",0.2, -1,1)
b4_c2 = ROOT.RooRealVar("b4_c2", "c2",0.3, -1,1)
bkg_model4 = ROOT.RooChebychev("bkg_model4", "Signal component 1", x, ROOT.RooArgList(b4_c0, b4_c1, b4_c2))

##############################
#4 K1680m pi+
b5_tau = ROOT.RooRealVar("b5_tau", "tau",-2, -10,0)

b5_mean = ROOT.RooRealVar("b5_mean", "mean of gaussians", 0.5,0, 1.)
b5_sigma1 = ROOT.RooRealVar("b5_sigma1", "width of gaussians", 0.5,0,1)
b5_1 = ROOT.RooExponential("b5_1", "Signal component 1", x, b5_tau)
b5_2 = ROOT.RooBreitWigner("b5_2", "Signal component 2", x, b5_mean, b5_sigma1)

b5_frac = ROOT.RooRealVar("b5_frac", "fraction of component 2 in signal", 0.2, 0.0, 1.0)
bkg_model5 = ROOT.RooAddPdf("bkg_model5", "Signal", [b5_1, b5_2], b5_frac)
##############################
#5 antiK1430 pi0
b6_c0 = ROOT.RooRealVar("b6_c0", "c0",0.5, -1.,1.)
b6_mean = ROOT.RooRealVar("b6_mean", "mean of gaussians", 0.5,0, 1.)
b6_sigma1 = ROOT.RooRealVar("b6_sigma1", "width of gaussians", 0.5,0,1)

b6_1 = ROOT.RooPolynomial("b6_1", "Signal component 1", x, ROOT.RooArgList(b6_c0), lowestOrder=1)
b6_2 = ROOT.RooGaussian("b6_2", "Signal component 2", x, b6_mean, b6_sigma1)

b6_frac = ROOT.RooRealVar("b6_frac", "fraction of component 2 in signal", 0.2, 0.0, 1.0)
bkg_model6 = ROOT.RooAddPdf("bkg_model6", "Signal", [b6_1, b6_2], b6_frac)
##############################
#1

##############################
# Add all bkg models

bkg_model2_frac =  ROOT.RooRealVar("bkg_model2_frac", "fraction of component 2 in bkg", 0.2, 0.0, 1.0)
bkg_model3_frac =  ROOT.RooRealVar("bkg_model3_frac", "fraction of component 2 in bkg", 0.2, 0.0, 1.0)
bkg_model4_frac =  ROOT.RooRealVar("bkg_model4_frac", "fraction of component 2 in bkg", 0.2, 0.0, 1.0)
bkg_model5_frac =  ROOT.RooRealVar("bkg_model5_frac", "fraction of component 2 in bkg", 0.2, 0.0, 1.0)
bkg_model6_frac =  ROOT.RooRealVar("bkg_model6_frac", "fraction of component 2 in bkg", 0.2, 0.0, 1.0)



bkg_model_21 = ROOT.RooAddPdf("bkg_model_21", "Bkg", [bkg_model2, bkg_model1], bkg_model2_frac)
bkg_model_321 = ROOT.RooAddPdf("bkg_model_321", "Bkg", [bkg_model3, bkg_model_21], bkg_model3_frac)
bkg_model_4321 = ROOT.RooAddPdf("bkg_model_4321", "Bkg", [bkg_model4, bkg_model_321], bkg_model4_frac)
bkg_model_54321 = ROOT.RooAddPdf("bkg_model_54321", "Bkg", [bkg_model5, bkg_model_4321], bkg_model5_frac)
bkg_model = ROOT.RooAddPdf("bkg_model", "Bkg", [bkg_model6, bkg_model_54321], bkg_model6_frac)
#bkg_model = ROOT.RooAddPdf("bkg_model", "Bkg", [bkg_model1, bkg_model2], bkg_model1_frac)
#bkg_model = ROOT.RooAddPdf("bkg_model", "Bkg", [bkg_model1, bkg_model2], bkg_model1_frac)



####################################
# construct signal + bkg pdf
nsig = ROOT.RooRealVar("nsig","# signal events",3000,0.,100000)
nbkg = ROOT.RooRealVar("nbkg","# bkg events",10000,0.,100000)


#####################################
# Associated nsig/nbkg as expected number of events with sig/bkg
esig = ROOT.RooExtendPdf("esig", "extended signal pdf", sig_model, nsig)
ebkg = ROOT.RooExtendPdf("ebkg", "extended background pdf", bkg_model, nbkg)
 
# Sum extended components without coefs
# -------------------------------------------------------------------------
 
# Construct sum of two extended pdf (no coefficients required)
extended_model = ROOT.RooAddPdf("extended_model", "(g1+g2)+a", [ebkg, esig])


#extended_pdf = ROOT.RooAddPdf("extended_pdf","sig+bkg",ROOT.RooArgList(sig_model,bkg_model), ROOT.RooArgList(nsig,nbkg))
##################################
#Fitting


#A0 = ROOT.RooRealVar("A0", "A0",0.5, -1,1)
#A1 = ROOT.RooRealVar("A1", "A1",0.5, -1,1)
#poly_order1 = ROOT.RooPolynomial("poly_order1", "Signal component 1", x, ROOT.RooArgList(A0,A1), lowestOrder=1)


# x.setBins(70)

#mean = ROOT.RooRealVar("mean", "mean of gaussians", 0.5,0.3, 0.6)
#sigma1 = ROOT.RooRealVar("sigma1", "width of gaussians", 0.5,0,1)
#sigma2 = ROOT.RooRealVar("sigma2", "width of gaussians", 0.2,0,1)
#sigma3 = ROOT.RooRealVar("sigma3", "width of gaussians", 0.2,0,1)

# a2 = ROOT.RooRealVar("a2", "a2", 0.5, -1., 1.)
# b2 = ROOT.RooRealVar("b2", "b2", 0.3, -1., 1.)

# alpha = ROOT.RooRealVar("alpha", "width of gaussians", 0.5,0,10)
# n_CB = ROOT.RooRealVar("n_CB", "width of gaussians", 10,0,200)

# Novo_peak = ROOT.RooRealVar("Novo_peak", "Novo peak", 1.83,1.73,1.93)    
# Novo_width = ROOT.RooRealVar("Novo_widh", "Novo peak", 0.05,0,0.5)    
# Novo_tail = ROOT.RooRealVar("Novo_tail", "Novo peak", 0.5,0,10)    

#sig1 = ROOT.RooGaussian("sig1", "Signal component 1", x, mean, sigma1)
#sig2 = ROOT.RooGaussian("sig2", "Signal component 1", x, mean, sigma2)
#sig3 = ROOT.RooGaussian("sig3", "Signal component 1", x, mean, sigma3)

# pow2 = ROOT.RooPower("pow", "pow", x, RooArgList(0, a2), RooArgList(0,2))

# sig2 = ROOT.RooCBShape("sig2", "Signal component 2", x, mean, sigma2, alpha, n_CB)
# sig3 = ROOT.RooNovosibirsk("sig3", "Signal component 3", x, mean, Novo_width, Novo_tail)

#sig1frac = ROOT.RooRealVar("sig1frac", "fraction of component 1 in signal", 0.2, 0.0, 1.0)
#sig_sum1 = ROOT.RooAddPdf("sig_sum1", "Signal1", [sig1, sig2], sig1frac)

#sig2frac = ROOT.RooRealVar("sig2frac", "fraction of component 2 in signal", 0.2, 0.0, 1.0)
#rhopkm_cosHel = ROOT.RooAddPdf("rhopkm_cosHel", "Signal", [sig3, sig_sum1], sig2frac)

#bkg1frac = ROOT.RooRealVar("bkg1frac", "fraction of component 2 in signal", 0.2, 0.0, 1.0)
#bkg_all = ROOT.RooAddPdf("bkg_all", "Signal", [poly_order1, rhopkm_cosHel], bkg1frac)

#sigbkgfrac = ROOT.RooRealVar("sigbkgfrac", "fraction of component 2 in signal", 0.2, 0.0, 1.0)
#sig = ROOT.RooAddPdf("sig", "Signal", [cosHel_sigpdf, bkg_all], sigbkgfrac)




data = ROOT.RooDataSet.from_numpy({"cos#theta_{H}": np_data['D0_cosHel_0']}, [x])

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
r = extended_model.fitTo(data, NumCPU=12, Range=(xrange[0],xrange[1]))

# r.Print()
canv.cd(1) 
#     frame = x.frame(Title="D^{0} #rightarrow #bar{K}^{*0} #pi^{0}")
frame = x.frame(Title=" ")

data.plotOn(frame,Name = "data1", XErrorSize=0)

# sig1.plotOn(frame, LineStyle="--", LineColor="r")
# sig2.plotOn(frame, LineStyle="--", LineColor="r")
# sig.plotOn(frame, Name="gauss1", Components=sig1, LineStyle=ROOT.kDashed, LineColor=593)
# sig.plotOn(frame, Name="CB1", Components=sig2, LineStyle=ROOT.kDashed, LineColor=593)
# sig.plotOn(frame, Name="CB2", Components=sig3, LineStyle=ROOT.kDashed, LineColor=593)


#sig.plotOn(frame, Name="CB2", Components=rhopkm_cosHel, LineStyle=ROOT.kDashed, LineColor=593)

extended_model.plotOn(frame, Name="signal", Components=sig_model, LineStyle=ROOT.kDashed, LineColor=593)
extended_model.plotOn(frame, Name="bkg1", Components=bkg_model1, LineStyle=ROOT.kDashed, LineColor=593)
extended_model.plotOn(frame, Name="bkg2", Components=bkg_model2, LineStyle=ROOT.kDashed, LineColor=593)
extended_model.plotOn(frame, Name="bkg3", Components=bkg_model3, LineStyle=ROOT.kDashed, LineColor=593)
extended_model.plotOn(frame, Name="bkg4", Components=bkg_model4, LineStyle=ROOT.kDashed, LineColor=593)
extended_model.plotOn(frame, Name="bkg5", Components=bkg_model5, LineStyle=ROOT.kDashed, LineColor=593)
extended_model.plotOn(frame, Name="bkg6", Components=bkg_model6, LineStyle=ROOT.kDashed, LineColor=593)


extended_model.plotOn(frame, Name="fitting")


# sig.paramOn(frame)
frame.GetXaxis().SetTitleSize(0.047)
frame.GetXaxis().CenterTitle(True)
frame.GetYaxis().SetTitleSize(0.04)
frame.GetYaxis().SetTitleOffset(1.2)
frame.Draw("PE")


leg1 = ROOT.TLegend(0.1,0.75, 0.25, 0.9)
leg1.SetFillColor(ROOT.kWhite)
# leg1.SetHeader("The Legend title","C")
leg1.AddEntry("data1", "MC", "PE")
leg1.AddEntry("fitting", "fit", "l")
leg1.Draw()

hpull = frame.pullHist()
hpull.SetFillStyle(1001)
hpull.SetFillColor(1);
for i in range(0,hpull.GetN()):#(int i=0;i<hpull.GetN();++i): 
    hpull.SetPointError(i,0.0,0.0,0.0,0.0)
# pullplot = x.frame(Title(" "))
pullplot = x.frame()
pullplot.SetTitle("")
pullplot.addPlotable(hpull,"BE")
# pullplot.addPlotable(hpull,"PE")

pullplot.SetYTitle("Pull")
pullplot.GetXaxis().SetTitleSize(0)
pullplot.GetYaxis().SetTitleSize(0.17)
pullplot.GetYaxis().CenterTitle(True)
pullplot.GetYaxis().SetTitleOffset(0.2)
pullplot.SetMinimum(-4.)
pullplot.SetMaximum(4.)
pullplot.GetXaxis().SetLabelSize(0.1)
pullplot.GetYaxis().SetLabelSize(0.09)
canv.cd(2)
pullplot.Draw()

xmin1 = ctypes.c_double(xrange[0])
xmax1 = ctypes.c_double(xrange[1])
# xmin1 = 0.1
# xmax1 = 0.18
line = ROOT.TLine(xmin1,0.0,xmax1,0.0)
line1 = ROOT.TLine(xmin1,3.0,xmax1,3.0)
line2 = ROOT.TLine(xmin1,-3.0,xmax1,-3.0)

line.SetLineColor(ROOT.kRed)
line.SetLineWidth(3)
line1.SetLineColor(ROOT.kRed)
line2.SetLineColor(ROOT.kRed)
line1.SetLineStyle(2)
line2.SetLineStyle(2)
line.Draw("SAME")
line1.Draw("SAME")
line2.Draw("SAME")

canv.Update()

canv.Draw()
canv.SaveAs(file_name)
