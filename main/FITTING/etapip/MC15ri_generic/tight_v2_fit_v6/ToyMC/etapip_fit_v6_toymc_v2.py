import ROOT
from ROOT import RooFit
import glob
import ctypes
import os
import math
import numpy as np 
from ROOT import RooFit, RooRealVar, RooGaussian, RooDataSet, RooArgSet, RooAddPdf, RooRandom, RooArgList, RooDataHist, RooHistPdf, RooPolynomial

'''
file_name = "/share/storage/jykim/plots/MC15ri/etapip/gg/generic/MC15ri_1ab_etapip_gg_fit_tight_v2_fitv6.png"
fitresult_name = "/share/storage/jykim/plots/MC15ri/etapip/gg/generic/fitresult/MC15ri_1ab_etapip_gg_fit_tight_v2_fitv6.root"
dir_path = os.path.dirname(file_name)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)
dir_path = os.path.dirname(fitresult_name)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)

'''

#ROOT.gROOT.LoadMacro('/home/belle2/jaeyoung/workspace/git/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
#ROOT.SetBelle2Style()

'''
base_file_loc =  '/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15ri_generic/MC15ri_etaetapip_tight_v2_240419_Kp_BCS_etapi0const/'

loc_ccbar = base_file_loc + 'ccbar/tight_v2_240419_Kp_BCS_etapi0const_ccbar_output_02*.root'
#loc_ccbar = base_file_loc + 'ccbar/*.root'
# loc_ccbar = base_file_loc + 'topo/resultfile/result_antiKstar/standard.root'
#loc_ccbar = base_file_loc + 'topo/resultfile/result_etapip_gg/*.root'

loc_uubar = base_file_loc + 'uubar/*.root'
loc_ddbar = base_file_loc + 'ddbar/*.root'
loc_ssbar = base_file_loc + 'ssbar/*.root'
loc_charged = base_file_loc + 'charged/*.root'
loc_mixed = base_file_loc + 'mixed/*.root'
loc_taupair = base_file_loc + 'taupair/*.root'

file_list = [loc_ccbar,loc_uubar,loc_uubar,loc_ssbar,loc_charged,loc_mixed,loc_taupair]
#file_list = [loc_ccbar,loc_charged,loc_mixed]
#file_list = [loc_ccbar]
'''
base_file_loc = '/home/belle2/jaeyoung/storage_b2/storage/reduced_ntuples/MC15ri/etapip_eteeta/MC15ri_etaetapip_tight_v2_240708_Kp_BCS_etapi0const/MC15ri_etaetapip_tight_v2_240708_Kp_BCS_etapi0const'

# #loc_ccbar = base_file_loc + 'ccbar/tight_v2_240419_Kp_BCS_etapi0const_ccbar_output_02*.root'
loc_ccbar = base_file_loc + '_ccbar.root'
# # loc_ccbar = base_file_loc + 'topo/resultfile/result_etapip_gg'
# loc_ccbar = base_file_loc + 'topo/resultfile/result_etapip_gg/standard*.root'

loc_uubar = base_file_loc + '_uubar.root'
loc_ddbar = base_file_loc + '_ddbar.root'
loc_ssbar = base_file_loc + '_ssbar.root'
loc_charged = base_file_loc + '_charged.root'
loc_mixed = base_file_loc + '_mixed.root'
loc_taupair = base_file_loc + '_taupair.root'

file_list = [loc_ccbar,loc_uubar,loc_uubar,loc_ssbar,loc_charged,loc_mixed,loc_taupair]
#file_list = [loc_ccbar,loc_charged,loc_mixed]
# file_list = [base_file_loc]

# Get the tree from the file
tree_name = "etapip_gg"

mychain = ROOT.TChain(tree_name)

for i in file_list:
    mychain.Add(i)

print(file_list)


# Define variable and its range
fit_variable = "Dp_M"
fit_var_name = "M(D^{+}) [GeV/c^{2}]"
fit_range = (1.76, 2.05)
rank_var = tree_name + "_rank"
truth_var = "Dp_isSignal"
charge_var = "Pip_charge"

# Cuts
cuts = rank_var + "==1" 
cuts += " && " + charge_var + "==1"

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

#mean_johnson = ROOT.RooRealVar("mean_johnson", "mean of Johnson", 1.86, 1.8, 1.9)
#sigma_johnson = ROOT.RooRealVar("sigma_johnson", "sigma of Johnson", 0.01, 0.00001, 0.5)
#gamma = ROOT.RooRealVar("gamma", "gamma of Johnson", 0.1, 0.001, 1)
#delta = ROOT.RooRealVar("delta", "delta of Johnson", 0.1, 0.001, 1)
#mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0, -1, 1)
#sigma_gaussian = ROOT.RooRealVar("sigma_gaussian", "sigma of Gaussian", 0.01, 0.00001, 1)

# True+false fixed 24.07.19
mean_johnson = ROOT.RooRealVar("mean_johnson", "mean of Johnson", 1.8805)
sigma_johnson = ROOT.RooRealVar("sigma_johnson", "sigma of Johnson", 0.0028028)
gamma = ROOT.RooRealVar("gamma", "gamma of Johnson", 0.32250)
delta = ROOT.RooRealVar("delta", "delta of Johnson", 0.59443 )


mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0, -1, 1)
sigma_gaussian = ROOT.RooRealVar("sigma_gaussian", "sigma of Gaussian", 0.01, 0.00001, 1)

# Create a Johnson distribution
johnson = ROOT.RooJohnson("johnson", "Johnson PDF", x, mean_johnson, sigma_johnson, gamma, delta)

# Create a Gaussian distribution
gaussian = ROOT.RooGaussian("gaussian", "Gaussian PDF", x, mean_gaussian, sigma_gaussian)

# Convolute the Johnson distribution with Gaussian
sig_model = ROOT.RooFFTConvPdf("sig_model", "Convolution of Johnson and Gaussian", x, johnson, gaussian)



#Ds_mean_johnson = ROOT.RooRealVar("Ds_mean_johnson", "mean of Johnson", 1.96, 1.91, 1.98)
#Ds_sigma_johnson = ROOT.RooRealVar("Ds_sigma_johnson", "sigma of Johnson", 0.01, 0.00001, 0.5)
#Ds_gamma = ROOT.RooRealVar("Ds_gamma", "gamma of Johnson", 0.1, 0.001, 1)
#Ds_delta = ROOT.RooRealVar("Ds_delta", "delta of Johnson", 0.1, 0.001, 1)

# True+false fixed 24.07.19
Ds_mean_johnson = ROOT.RooRealVar("Ds_mean_johnson", "mean of Johnson", 1.9934)
Ds_sigma_johnson = ROOT.RooRealVar("Ds_sigma_johnson", "sigma of Johnson",  0.0016496)
Ds_gamma = ROOT.RooRealVar("Ds_gamma", "gamma of Johnson",  0.35250)
Ds_delta = ROOT.RooRealVar("Ds_delta", "delta of Johnson", 0.47138)

Ds_mean_gaussian = ROOT.RooRealVar("Ds_mean_gaussian", "mean of Gaussian", 0, -1, 1)
Ds_sigma_gaussian = ROOT.RooRealVar("Ds_sigma_gaussian", "sigma of Gaussian", 0.01, 0.00001, 1)

# Create a Johnson distribution
Ds_johnson = ROOT.RooJohnson("Ds_johnson", "Johnson PDF", x, Ds_mean_johnson, Ds_sigma_johnson, Ds_gamma, Ds_delta)

# Create a Gaussian distribution
Ds_gaussian = ROOT.RooGaussian("Ds_gaussian", "Gaussian PDF", x, Ds_mean_gaussian, Ds_sigma_gaussian)

# Convolute the Johnson distribution with Gaussian
Ds_model = ROOT.RooFFTConvPdf("Ds_model", "Convolution of Johnson and Gaussian", x, Ds_johnson, Ds_gaussian)


rhopeta_mean = ROOT.RooRealVar("rhopeta_mean", "mean", 1.75, 1.65, 1.8)
rhopeta_sigma = ROOT.RooRealVar("rhopeta_sigma", "sigma", 0.03, 0.001, 0.05)
rhopeta_model = ROOT.RooGaussian("rhopeta_model", "gauss", x, rhopeta_mean, rhopeta_sigma)

x_bkg1_Cheby_c0 = ROOT.RooRealVar("x_bkg1_Cheby_c0", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c1 = ROOT.RooRealVar("x_bkg1_Cheby_c1", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c2 = ROOT.RooRealVar("x_bkg1_Cheby_c2", "c0",0.0, -1.0, 1.0)
x_bkg1_tau = ROOT.RooRealVar("x_bkg1_tau", "c0",-0.5, -20, 0)

#bkg_model = ROOT.RooPolynomial("bkg_model", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1))
bkg_model = ROOT.RooExponential("bkg_model", "x_bkg1", x, x_bkg1_tau)


nsig = ROOT.RooRealVar("nsig","# signal events",N_total*0.01,0,N_total*0.8)
nbkg1 = ROOT.RooRealVar("nbkg1","# bkg events",N_total*0.8,0, N_total)
nbkg2 = ROOT.RooRealVar("nbkg2","# bkg events",N_total*0.2,0, N_total)
nDs = ROOT.RooRealVar("nDs","# bkg events",N_total*0.8,0, N_total)

extended_model = ROOT.RooAddPdf("extended_model", "x_model", ROOT.RooArgSet(sig_model,bkg_model, Ds_model, rhopeta_model), ROOT.RooArgSet(nsig, nbkg1, nDs, nbkg2))

#r = extended_model.fitTo(data,NumCPU=4, Extended=ROOT.kTRUE,PrintLevel=-1, Save=1,SumW2Error=True)
r = extended_model.fitTo(data,  RooFit.Extended(True), RooFit.PrintLevel(3), RooFit.Save(1),RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(15))
r.Print()
#r = extended_model.fitTo(data, ROOT.RooFit.PrintLevel(-1), Save=1,SumW2Error=True)

# Parameters for the simulation
#n_iterations = 10000

    #nsig.setVal(N_Input)

mcstudy = ROOT.RooMCStudy(
    extended_model,
    #{x,y},
    ROOT.RooArgSet(x),
    RooFit.Binned(True),
    RooFit.Silence(True),
    RooFit.Extended(True),
    RooFit.FitOptions(RooFit.Save(True), RooFit.PrintEvalErrors(0), RooFit.NumCPU(15)),
)

# Generate and fit events
# ---------------------------------------------

# Generate and fit 1000 samples of Poisson(nExpected) events
mcstudy.generateAndFit(10000)

# Explore results of study
# ------------------------------------------------
# ------------------------------------------------

# Make plots of the distributions of mean, error on mean and the pull of
# mean
frame1 = mcstudy.plotParam(nsig, RooFit.Bins(20))
frame2 = mcstudy.plotError(nsig,RooFit.Bins(20))
frame3 = mcstudy.plotPull(nsig, RooFit.Bins(20),RooFit.FitGauss(False))
pullMean = ROOT.RooRealVar("pullMean","",0,-10,10)
pullSigma = ROOT.RooRealVar("pullSigma","",1,0.1,5)
#pullMean.setPlotLabel("pull #mu")   # // optional (to get nicer plot labels if you want)
#pullSigma.setPlotLabel("pull #sigma")
pullMean.setPlotLabel("#mu")   # // optional (to get nicer plot labels if you want)
pullSigma.setPlotLabel("#sigma")

pullGauss = ROOT.RooGaussian("pullGauss", "", frame3.getPlotVar() , pullMean, pullSigma)
r_pull = pullGauss.fitTo(mcstudy.fitParDataSet(),RooFit.NumCPU(11),RooFit.PrintLevel(-1))
# Plot distribution of minimized likelihood
frame4 = mcstudy.plotNLL(RooFit.Bins(20))

# Make some histograms from the parameter dataset
# hh_cor_a0_s1f = mcstudy.fitParDataSet().createHistogram("hh", x_sig_sigma2, YVar=x_sig_mean)
# hh_cor_a0_a1 = mcstudy.fitParDataSet().createHistogram("hh", x_sig_mean, YVar=x_sig_sigma2)

# Access some of the saved fit results from individual toys
# corrHist000 = mcstudy.fitResult(0).correlationHist("c000")
# corrHist127 = mcstudy.fitResult(1).correlationHist("c001")
# corrHist953 = mcstudy.fitResult(2).correlationHist("c002")

# Draw all plots on a canvas
# ROOT.gStyle.SetPalette(1)
# ROOT.gStyle.SetOptStat(0)
c = ROOT.TCanvas("Canvas", "ToyMCstudy", 1500, 500)
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
N_Input = data.sumEntries()

nsig_Mean = ROOT.RooRealVar("nsig_Mean","", N_Input,0.5*N_Input,1.5*N_Input)
nsig_Sigma = ROOT.RooRealVar("nsig_Sigma","",N_Input*0.5,N_Input*0.001,N_Input*0.8)
nsig_Mean.setPlotLabel("#mu")   # // optional (to get nicer plot labels if you want)
nsig_Sigma.setPlotLabel("#sigma")

nsig_Gauss = ROOT.RooGaussian("nsig_Gauss", "", frame1.getPlotVar() , nsig_Mean, nsig_Sigma)

r_nsig = nsig_Gauss.fitTo(mcstudy.fitParDataSet(),RooFit.NumCPU(12),RooFit.PrintLevel(-1))

nsig_Gauss.plotOn(frame1)
#pullGauss.paramOn(frame3,xmin=0.55, xmax=0.75, ymax=0.9, sigDigits=3)
nsig_Gauss.paramOn(frame1, ROOT.RooFit.Layout(0.60, 0.80, 0.9), ROOT.RooFit.Format("NE",ROOT.RooFit.AutoPrecision(1)))


frame1.Draw("PE")
c.cd(3)
# ROOT.gPad.SetLeftMargin(0.15)
# frame2.GetYaxis().SetTitleOffset(1.4)
frame2.Draw("PE")
# c.cd(4)
# #ROOT.gPad.SetLeftMargin(0.15)
# frame4.GetYaxis().SetTitleOffset(1.4)
# frame4.Draw("PE")
#file_name="/media/jykim/T7/saved_plots/fitting/linearity/antiKstarg/ToyMC_10000_230807.png" 
file_name="ToyMC_10000_240722_Dp.png" 
c.SaveAs(file_name)

# Make ROOT.RooMCStudy object available on command line after
# macro finishes
# ROOT.gDirectory.Add(mcstudy)

