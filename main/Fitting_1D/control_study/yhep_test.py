# %load_ext autoreload
# %autoreload 2
import seaborn as sns
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

import pandas as pd
import numpy as np

from main.data_tools.extract_ntuples import get_pd, get_np

file_loc = '/media/jykim/T7/storage/01_recon/pi0veto_calib/D2kmpippi0/ntuple/control_recon_mdst_DALITZ_30M.root'
base_filter = 'D0_M>1.76 && D0_M<1.93 && abs(antiKstar_InvM - 0.89555)<0.06 && abs(Dstarp_Q - 0.00593)<0.0006 && Dstarp_CMS_p>2.3 && antiKstarpi0_rank_Dstp==1'
#base_filter = 'D0_M>1.70 && D0_M<1.98 && abs(antiKstar_InvM - 0.89555)<0.06 && abs(Dstarp_Q - 0.00593)<0.0006 && Dstarp_CMS_p>2.3 && antiKstarpi0_rank_Dstp==1'
tree = 'control'
signal_variables = ['D0_M','D0_cosHel_0']
np_data = get_pd(file=file_loc, tree='control',base_filter=base_filter,variables=signal_variables)
#np_data = get_np(file=file_loc, tree='control',base_filter=base_filter,variables=signal_variables)
#np_data = np_data.sample(frac=0.3)
np_data = np_data['D0_M']
np_data = np_data.to_numpy()


x = ROOT.RooRealVar("M(D^{0})", "M(D^{0}) [GeV/c^{2}]", 1.70, 1.98, "")
x.setBins(50)


mean1 = ROOT.RooRealVar("mean1", "mean of gaussians", 1.861,1.84, 1.89)
sigma1_1 = ROOT.RooRealVar("sigma1_1", "width of gaussians", 0.021,0,1)
sigma1_2 = ROOT.RooRealVar("sigma1_2", "width of gaussians", 0.011,0,0.5)
sigma1_3= ROOT.RooRealVar("sigma1_3", "width of gaussians", 0.011,0,0.5)
alpha1 = ROOT.RooRealVar("alpha1", "width of gaussians", 0.71,0,5)
n_CB1 = ROOT.RooRealVar("n_CB1", "width of gaussians", 10.1,0,100) 
Novo_width1 = ROOT.RooRealVar("Novo_width1", "Novo peak", 0.51,0,1)    
Novo_tail1 = ROOT.RooRealVar("Novo_tail1", "Novo peak", 0.11,0,1)    

mean2 = ROOT.RooRealVar("mean2", "mean of gaussians", 1.862,1.84, 1.89)
sigma2_1 = ROOT.RooRealVar("sigma2_1", "width of gaussians", 0.022,0,1)
sigma2_2 = ROOT.RooRealVar("sigma2_2", "width of gaussians", 0.012,0,0.5)
sigma2_3 = ROOT.RooRealVar("sigma2_3", "width of gaussians", 0.012,0,0.5)
alpha2 = ROOT.RooRealVar("alpha2", "width of gaussians", 0.72,0,5)
n_CB2 = ROOT.RooRealVar("n_CB2", "width of gaussians", 10.2,0,100) 
Novo_width2 = ROOT.RooRealVar("Novo_width2", "Novo peak", 0.52,0,1)    
Novo_tail2 = ROOT.RooRealVar("Novo_tail2", "Novo peak", 0.12,0,1) 

mean3 = ROOT.RooRealVar("mean3", "mean of gaussians", 1.863,1.84, 1.89)
sigma3_1 = ROOT.RooRealVar("sigma3_1", "width of gaussians", 0.023,0,1)
sigma3_2 = ROOT.RooRealVar("sigma3_2", "width of gaussians", 0.013,0,0.5)
sigma3_3 = ROOT.RooRealVar("sigma3_3", "width of gaussians", 0.013,0,0.5)
alpha3 = ROOT.RooRealVar("alpha3", "width of gaussians", 0.73,0,5)
n_CB3 = ROOT.RooRealVar("n_CB3", "width of gaussians", 10.3,0,100) 
Novo_width3 = ROOT.RooRealVar("Novo_width3", "Novo peak", 0.53,0,1)    
Novo_tail3 = ROOT.RooRealVar("Novo_tail3", "Novo peak", 0.13,0,1) 

mean4 = ROOT.RooRealVar("mean4", "mean of gaussians", 1.864,1.84, 1.89)
sigma4_1 = ROOT.RooRealVar("sigma4_1", "width of gaussians", 0.04,0,1)
sigma4_2 = ROOT.RooRealVar("sigma4_2", "width of gaussians", 0.04,0,0.5)
sigma4_3 = ROOT.RooRealVar("sigma4_3", "width of gaussians", 0.04,0,0.5)
alpha4 = ROOT.RooRealVar("alpha4", "width of gaussians", 0.74,0,5)
n_CB4 = ROOT.RooRealVar("n_CB4", "width of gaussians", 10.4,0,100) 
Novo_width4 = ROOT.RooRealVar("Novo_width4", "Novo peak", 0.54,0,1)    
Novo_tail4 = ROOT.RooRealVar("Novo_tail4", "Novo peak", 0.14,0,1) 

mean5 = ROOT.RooRealVar("mean5", "mean of gaussians", 1.865,1.84, 1.89)
sigma5_1 = ROOT.RooRealVar("sigma5_1", "width of gaussians", 0.025,0,1)
sigma5_2 = ROOT.RooRealVar("sigma5_2", "width of gaussians", 0.015,0,0.5)
sigma5_3 = ROOT.RooRealVar("sigma5_3", "width of gaussians", 0.015,0,0.5)
alpha5 = ROOT.RooRealVar("alpha5", "width of gaussians", 0.75,0,5)
n_CB5 = ROOT.RooRealVar("n_CB5", "width of gaussians", 10.5,0,100) 
Novo_width5 = ROOT.RooRealVar("Novo_width5", "Novo peak", 0.55,0,1)    
Novo_tail5 = ROOT.RooRealVar("Novo_tail5", "Novo peak", 0.15,0,1) 

mean6 = ROOT.RooRealVar("mean6", "mean of gaussians", 1.866,1.84, 1.89)
sigma6_1 = ROOT.RooRealVar("sigma6_1", "width of gaussians", 0.026,0,1)
sigma6_2 = ROOT.RooRealVar("sigma6_2", "width of gaussians", 0.016,0,0.5)
sigma6_3 = ROOT.RooRealVar("sigma6_3", "width of gaussians", 0.016,0,0.5)
alpha6 = ROOT.RooRealVar("alpha6", "width of gaussians", 0.76,0,5)
n_CB6 = ROOT.RooRealVar("n_CB6", "width of gaussians", 10.6,0,100) 
Novo_width6 = ROOT.RooRealVar("Novo_width6", "Novo peak", 0.56,0,0.1)    
Novo_tail6 = ROOT.RooRealVar("Novo_tail6", "Novo peak", 0.16,0,1) 

#####
sig1_1 = ROOT.RooGaussian("sig1_1", "Signal component 1", x, mean1, sigma1_1)
sig1_2 = ROOT.RooCBShape("sig1_2", "Signal component 2", x, mean1, sigma1_2, alpha1, n_CB1)
sig1_3 = ROOT.RooGaussian("sig1_3", "Signal component 1", x, mean1, sigma1_3)
#sig1_3 = ROOT.RooNovosibirsk("sig1_3", "Signal component 3", x, mean1, Novo_width1, Novo_tail1)

sig1_1frac = ROOT.RooRealVar("sig1_1frac", "fraction of component 1 in signal", 0.2, 0.0, 1.0)
sig_sum1_1 = ROOT.RooAddPdf("sig_sum1_1", "Signal1", [sig1_1, sig1_2], sig1_1frac)
sig1_2frac = ROOT.RooRealVar("sig1_2frac", "fraction of component 2 in signal", 0.2, 0.0, 1.0)

sig1 = ROOT.RooAddPdf("sig1", "Signal", [sig1_3, sig_sum1_1], sig1_2frac)
#####
sig2_1 = ROOT.RooGaussian("sig2_1", "Signal component 1", x, mean1, sigma2_1)
sig2_2 = ROOT.RooCBShape("sig2_2", "Signal component 2", x, mean1, sigma2_2, alpha2, n_CB2)
sig2_3 = ROOT.RooGaussian("sig2_3", "Signal component 1", x, mean1, sigma2_3)
#sig2_3 = ROOT.RooNovosibirsk("sig2_3", "Signal component 3", x, mean2, Novo_width2, Novo_tail2)

sig2_1frac = ROOT.RooRealVar("sig2_1frac", "fraction of component 1 in signal", 0.2, 0.0, 1.0)
sig_sum2_1 = ROOT.RooAddPdf("sig_sum2_1", "Signal1", [sig2_1, sig2_2], sig2_1frac)
sig2_2frac = ROOT.RooRealVar("sig2_2frac", "fraction of component 2 in signal", 0.2, 0.0, 1.0)

sig2 = ROOT.RooAddPdf("sig2", "Signal", [sig2_3, sig_sum2_1], sig2_2frac)
#####
sig3_1 = ROOT.RooGaussian("sig3_1", "Signal component 1", x, mean1, sigma3_1)
sig3_2 = ROOT.RooCBShape("sig3_2", "Signal component 2", x, mean1, sigma3_2, alpha3, n_CB3)
sig3_3 = ROOT.RooGaussian("sig3_3", "Signal component 1", x, mean1, sigma3_3)
#sig3_3 = ROOT.RooNovosibirsk("sig3_3", "Signal component 3", x, mean3, Novo_width3, Novo_tail3)

sig3_1frac = ROOT.RooRealVar("sig3_1frac", "fraction of component 1 in signal", 0.2, 0.0, 1.0)
sig_sum3_1 = ROOT.RooAddPdf("sig_sum3_1", "Signal1", [sig3_1, sig3_2], sig3_1frac)
sig3_2frac = ROOT.RooRealVar("sig3_2frac", "fraction of component 2 in signal", 0.2, 0.0, 1.0)

sig3 = ROOT.RooAddPdf("sig3", "Signal", [sig3_3, sig_sum3_1], sig3_2frac)
#####
sig4_1 = ROOT.RooGaussian("sig4_1", "Signal component 1", x, mean1, sigma4_1)
sig4_2 = ROOT.RooCBShape("sig4_2", "Signal component 2", x, mean1, sigma4_2, alpha4, n_CB4)
sig4_3 = ROOT.RooGaussian("sig4_3", "Signal component 1", x, mean1, sigma4_3)
#sig4_3 = ROOT.RooNovosibirsk("sig4_3", "Signal component 3", x, mean4, Novo_width4, Novo_tail4)

sig4_1frac = ROOT.RooRealVar("sig4_1frac", "fraction of component 1 in signal", 0.2, 0.0, 1.0)
sig_sum4_1 = ROOT.RooAddPdf("sig_sum4_1", "Signal1", [sig4_1, sig4_2], sig4_1frac)
sig4_2frac = ROOT.RooRealVar("sig4_2frac", "fraction of component 2 in signal", 0.2, 0.0, 1.0)

sig4 = ROOT.RooAddPdf("sig4", "Signal", [sig4_3, sig_sum4_1], sig4_2frac)
#####
sig5_1 = ROOT.RooGaussian("sig5_1", "Signal component 1", x, mean1, sigma5_1)
sig5_2 = ROOT.RooCBShape("sig5_2", "Signal component 2", x, mean1, sigma5_2, alpha5, n_CB5)
sig5_3 = ROOT.RooGaussian("sig5_3", "Signal component 1", x, mean1, sigma5_3)
#sig5_3 = ROOT.RooNovosibirsk("sig5_3", "Signal component 3", x, mean5, Novo_width5, Novo_tail5)

sig5_1frac = ROOT.RooRealVar("sig5_1frac", "fraction of component 1 in signal", 0.2, 0.0, 1.0)
sig_sum5_1 = ROOT.RooAddPdf("sig_sum5_1", "Signal1", [sig5_1, sig5_2], sig5_1frac)
sig5_2frac = ROOT.RooRealVar("sig5_2frac", "fraction of component 2 in signal", 0.2, 0.0, 1.0)

sig5 = ROOT.RooAddPdf("sig5", "Signal", [sig5_3, sig_sum5_1], sig5_2frac)
#####
sig6_1 = ROOT.RooGaussian("sig6_1", "Signal component 1", x, mean1, sigma6_1)
sig6_2 = ROOT.RooCBShape("sig6_2", "Signal component 2", x, mean1, sigma6_2, alpha6, n_CB6)
sig6_3 = ROOT.RooGaussian("sig6_3", "Signal component 1", x, mean1, sigma6_3)
#sig6_3 = ROOT.RooNovosibirsk("sig6_3", "Signal component 3", x, mean6, Novo_width6, Novo_tail6)

sig6_1frac = ROOT.RooRealVar("sig6_1frac", "fraction of component 1 in signal", 0.2, 0.0, 1.0)
sig_sum6_1 = ROOT.RooAddPdf("sig_sum6_1", "Signal1", [sig6_1, sig6_2], sig6_1frac)
sig6_2frac = ROOT.RooRealVar("sig6_2frac", "fraction of component 2 in signal", 0.2, 0.0, 1.0)

sig6 = ROOT.RooAddPdf("sig6", "Signal", [sig6_3, sig_sum6_1], sig6_2frac)

# frac1 = ROOT.RooRealVar("frac1", "sig fraction1", 0.2, 0., 1.0)
# frac2 = ROOT.RooRealVar("frac2", "sig fraction2", 0.1, 0., 1.0)
# frac3 = ROOT.RooRealVar("frac3", "sig fraction3", 0.4, 0., 1.0)
# frac4 = ROOT.RooRealVar("frac4", "sig fraction4", 0.35, 0., 1.0)
# frac5 = ROOT.RooRealVar("frac5", "sig fraction5", 0.3, 0., 1.0)

sig1frac = ROOT.RooRealVar("sig1frac", "fraction of component 1 in signal", 0.22, 0.0, 1.0)
sig_sum1 = ROOT.RooAddPdf("sig_sum1", "Signal1", [sig1, sig2], sig1frac)

sig2frac = ROOT.RooRealVar("sig2frac", "fraction of component 1 in signal", 0.23, 0.0, 1.0)
sig_sum2 = ROOT.RooAddPdf("sig_sum2", "Signal2", [sig2, sig_sum1], sig2frac)

sig3frac = ROOT.RooRealVar("sig3frac", "fraction of component 1 in signal", 0.21, 0.0, 1.0)
sig_sum3 = ROOT.RooAddPdf("sig_sum3", "Signal1", [sig3, sig_sum2], sig3frac)

sig4frac = ROOT.RooRealVar("sig4frac", "fraction of component 1 in signal", 0.28, 0.0, 1.0)
sig_sum4 = ROOT.RooAddPdf("sig_sum4", "Signal1", [sig4, sig_sum3], sig4frac)

sig5frac = ROOT.RooRealVar("sig5frac", "fraction of component 1 in signal", 0.1, 0.0, 1.0)
sig_sum5 = ROOT.RooAddPdf("sig_sum5", "Signal1", [sig5, sig_sum4], sig5frac)

sig6frac = ROOT.RooRealVar("sig6frac", "fraction of component 1 in signal", 0.05, 0.0, 1.0)
sig_model = ROOT.RooAddPdf("sig", "Signal1", [sig6, sig_sum5], sig6frac)

# sig_model = ROOT.RooAddPdf("sig_model", "signal 6 functions", ROOT.RooArgList(sig1,sig2,sig3,sig4,sig5,sig6)
#                           , ROOT.RooArgList(frac1,frac2,frac3,frac4,frac5))

data = ROOT.RooDataSet.from_numpy({"M(D^{0})": np_data}, [x])

# data = rooDataSet

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
r = sig_model.fitTo(data,NumCPU=12, Range=(1.76,1.93))
#r = sig_model.fitTo(data,NumCPU=12, Range=(1.70,1.98))

# r.Print()
canv.cd(1) 
frame = x.frame(Title="D^{0} #rightarrow #bar{K}^{*0} #pi^{0}")
data.plotOn(frame,Name = "data1", XErrorSize=0)

# sig1.plotOn(frame, LineStyle="--", LineColor="r")
# sig2.plotOn(frame, LineStyle="--", LineColor="r")
sig_model.plotOn(frame, Name="fit1", Components=sig1, LineStyle=ROOT.kDashed, LineColor=593)
sig_model.plotOn(frame, Name="fit2", Components=sig2, LineStyle=ROOT.kDashed, LineColor=593)
sig_model.plotOn(frame, Name="fit3", Components=sig3, LineStyle=ROOT.kDashed, LineColor=593)
sig_model.plotOn(frame, Name="fit4", Components=sig4, LineStyle=ROOT.kDashed, LineColor=593)
sig_model.plotOn(frame, Name="fit5", Components=sig5, LineStyle=ROOT.kDashed, LineColor=593)
sig_model.plotOn(frame, Name="fit6", Components=sig6, LineStyle=ROOT.kDashed, LineColor=593)
# sig.plotOn(frame, Name="CB1", Components=sig2, LineStyle=ROOT.kDashed, LineColor=593)
# sig.plotOn(frame, Name="CB2", Components=sig3, LineStyle=ROOT.kDashed, LineColor=600)

sig_model.plotOn(frame, Name="fitting")


# sig.paramOn(frame)
frame.GetXaxis().SetTitleSize(0.047)
frame.GetXaxis().CenterTitle(True)
frame.GetYaxis().SetTitleSize(0.04)
frame.GetYaxis().SetTitleOffset(1.2)
frame.Draw("PE")


leg1 = ROOT.TLegend(0.75, 0.75, 0.9, 0.9)
leg1.SetFillColor(ROOT.kWhite)
# leg1.SetHeader("The Legend title","C")
leg1.AddEntry("data1", "data", "PE")
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
pullplot.SetMinimum(-5.)
pullplot.SetMaximum(5.)
pullplot.GetXaxis().SetLabelSize(0.1)
pullplot.GetYaxis().SetLabelSize(0.09)
canv.cd(2)
pullplot.Draw()

xmin1 = ctypes.c_double(1.70)
xmax1 = ctypes.c_double(1.98)
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
canv.SaveAs("test.png")
