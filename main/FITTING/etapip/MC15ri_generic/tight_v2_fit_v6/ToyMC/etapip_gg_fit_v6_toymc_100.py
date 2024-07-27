import ROOT
from ROOT import RooFit
import glob
import ctypes
import os
import math
import numpy as np 
from ROOT import RooFit, RooRealVar, RooGaussian, RooDataSet, RooArgSet, RooAddPdf, RooRandom, RooArgList, RooDataHist, RooHistPdf, RooPolynomial
import sys
import json
import time

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
# ROOT.ROOT.EnableImplicitMT(16)


# file_name = "/share/storage/jykim/plots/MC15ri/etapip/gg/generic/MC15ri_1ab_etapip_gg_fit_tight_v2_fitv6.png"
# fitresult_name = "/share/storage/jykim/plots/MC15ri/etapip/gg/generic/fitresult/MC15ri_1ab_etapip_gg_fit_tight_v2_fitv6.root"
# dir_path = os.path.dirname(file_name)
# if not os.path.exists(dir_path):
#     os.makedirs(dir_path)
# print("Directory created:", dir_path)
# dir_path = os.path.dirname(fitresult_name)
# if not os.path.exists(dir_path):
#     os.makedirs(dir_path)
# print("Directory created:", dir_path)

# ROOT.gROOT.LoadMacro('/home/jykim/workspace/git/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
# ROOT.gROOT.LoadMacro('/home/belle2/jaeyoung/DRAW_and_FITTING/main/FITTING/Belle2Style.C')

# ROOT.SetBelle2Style()

# base_file_loc =  '/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15ri_generic/MC15ri_etaetapip_tight_v2_240419_Kp_BCS_etapi0const/'
# base_file_loc =  '/home/belle2/jaeyoung/storage_ghi/Ntuples_ghi_2/MC15ri_generic/MC15ri_etaetapip_tight_v2_240419_Kp_BCS_etapi0const/'

# base_file_loc = '/share/storage/jykim/storage_ghi/reduced_ntuples/MC15ri/etapip_eteeta/MC15ri_etaetapip_tight_v2_240708_Kp_BCS_etapi0const.root'
#base_file_loc = '/share/storage/jykim/storage_ghi/reduced_ntuples/MC15ri/etapip_eteeta/MC15ri_etaetapip_tight_v2_240708_Kp_BCS_etapi0const'
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
Pip_p_var = "Pip_p"

# Cuts
cuts = rank_var + "==1" 
cuts += " && Pip_p>0.8"

# cuts += " && " + charge_var + "==1"

# Create RooRealVar
x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
x.setBins(70)
chiProb_rank = ROOT.RooRealVar(rank_var, rank_var, 0, 30)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)
Pip_p = ROOT.RooRealVar(Pip_p_var, Pip_p_var, 0,100)


print(cuts)
before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,chiProb_rank,Pip_charge,Pip_p), cuts)
# before_data = ROOT.RooDataHist("data","", mychain, ROOT.RooArgSet(x,chiProb_rank,Pip_charge), cuts)


w_1 = ROOT.RooRealVar('w_1', 'w', 0,1)
w_1.setVal(1)
before_data.addColumn(w_1)
before_data_weighted = ROOT.RooDataSet(before_data.GetName(), before_data.GetTitle(),before_data, before_data.get(), '' ,  'w_1')
# data = ROOT.RooDataHist(before_data.GetName(), before_data.GetTitle(),before_data, before_data.get(), '' ,  'w_1')

cut_expression = "Pip_charge==1"
data = before_data_weighted.reduce(cut_expression)


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


#Gen_r#############################################################################
# True+false fixed 24.07.19
mean_johnson_gen = ROOT.RooRealVar("mean_johnson_gen", "mean of Johnson", 1.8805)
sigma_johnson_gen = ROOT.RooRealVar("sigma_johnson_gen", "sigma of Johnson", 0.0028028)
gamma_gen = ROOT.RooRealVar("gamma_gen", "gamma of Johnson", 0.32250)
delta_gen = ROOT.RooRealVar("delta_gen", "delta of Johnson", 0.59443 )

mean_gaussian_gen= ROOT.RooRealVar("mean_gaussian_gen", "mean of Gaussian", mean_gaussian.getVal(), -1, 1)
sigma_gaussian_gen = ROOT.RooRealVar("sigma_gaussian_gen", "sigma of Gaussian", sigma_gaussian.getVal(), 0.00001, 1)

# Create a Johnson distribution
johnson_gen = ROOT.RooJohnson("johnson_gen", "Johnson PDF", x, mean_johnson_gen, sigma_johnson_gen, gamma_gen, delta_gen)

# Create a Gaussian distribution
gaussian_gen = ROOT.RooGaussian("gaussian_gen", "Gaussian PDF", x, mean_gaussian_gen, sigma_gaussian_gen)

# Convolute the Johnson distribution with Gaussian
sig_model_gen = ROOT.RooFFTConvPdf("sig_model_gen", "Convolution of Johnson and Gaussian", x, johnson_gen, gaussian_gen)



#Ds_mean_johnson = ROOT.RooRealVar("Ds_mean_johnson", "mean of Johnson", 1.96, 1.91, 1.98)
#Ds_sigma_johnson = ROOT.RooRealVar("Ds_sigma_johnson", "sigma of Johnson", 0.01, 0.00001, 0.5)
#Ds_gamma = ROOT.RooRealVar("Ds_gamma", "gamma of Johnson", 0.1, 0.001, 1)
#Ds_delta = ROOT.RooRealVar("Ds_delta", "delta of Johnson", 0.1, 0.001, 1)

# True+false fixed 24.07.19
Ds_mean_johnson_gen = ROOT.RooRealVar("Ds_mean_johnson_gen", "mean of Johnson", 1.9934)
Ds_sigma_johnson_gen = ROOT.RooRealVar("Ds_sigma_johnson_gen", "sigma of Johnson",  0.0016496)
Ds_gamma_gen = ROOT.RooRealVar("Ds_gamma_gen", "gamma of Johnson",  0.35250)
Ds_delta_gen = ROOT.RooRealVar("Ds_delta_gen", "delta of Johnson", 0.47138)


Ds_mean_gaussian_gen = ROOT.RooRealVar("Ds_mean_gaussian_gen", "mean of Gaussian", Ds_mean_gaussian.getVal(), -1, 1)
Ds_sigma_gaussian_gen = ROOT.RooRealVar("Ds_sigma_gaussian_gen", "sigma of Gaussian",  Ds_sigma_gaussian.getVal(), 0.00001, 1)

# Create a Johnson distribution
Ds_johnson_gen = ROOT.RooJohnson("Ds_johnson_gen", "Johnson PDF", x, Ds_mean_johnson_gen, Ds_sigma_johnson_gen, Ds_gamma_gen, Ds_delta_gen)

# Create a Gaussian distribution
Ds_gaussian_gen = ROOT.RooGaussian("Ds_gaussian_gen", "Gaussian PDF", x, Ds_mean_gaussian_gen, Ds_sigma_gaussian_gen)

# Convolute the Johnson distribution with Gaussian
Ds_model_gen = ROOT.RooFFTConvPdf("Ds_model_gen", "Convolution of Johnson and Gaussian", x, Ds_johnson_gen, Ds_gaussian_gen)


rhopeta_mean_gen = ROOT.RooRealVar("rhopeta_mean_gen", "mean", rhopeta_mean.getVal(), 1.65, 1.8)
rhopeta_sigma_gen = ROOT.RooRealVar("rhopeta_sigma_gen", "sigma", rhopeta_sigma.getVal(), 0.001, 0.05)
rhopeta_model_gen = ROOT.RooGaussian("rhopeta_model_gen", "gauss", x, rhopeta_mean_gen, rhopeta_sigma_gen)

x_bkg1_Cheby_c0_gen = ROOT.RooRealVar("x_bkg1_Cheby_c0_gen", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c1_gen = ROOT.RooRealVar("x_bkg1_Cheby_c1_gen", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c2_gen = ROOT.RooRealVar("x_bkg1_Cheby_c2_gen", "c0",0.0, -1.0, 1.0)
x_bkg1_tau_gen = ROOT.RooRealVar("x_bkg1_tau_gen", "c0",x_bkg1_tau.getVal(), -20, 0)

#bkg_model = ROOT.RooPolynomial("bkg_model", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1))
bkg_model_gen = ROOT.RooExponential("bkg_model_gen", "x_bkg1", x, x_bkg1_tau_gen)

nsig_gen = ROOT.RooRealVar("nsig_gen","# signal events",nsig.getVal(),0,N_total*0.8)
nbkg1_gen = ROOT.RooRealVar("nbkg1_gen","# bkg events", nbkg1.getVal(),0, N_total)
nbkg2_gen = ROOT.RooRealVar("nbkg2_gen","# bkg events", nbkg2.getVal(),0, N_total)
nDs_gen = ROOT.RooRealVar("nDs_gen","# bkg events",     nDs.getVal(),0, N_total)

extended_model_gen = ROOT.RooAddPdf("extended_model_gen", "x_model", ROOT.RooArgSet(sig_model_gen,bkg_model_gen, Ds_model_gen, rhopeta_model_gen), ROOT.RooArgSet(nsig_gen, nbkg1_gen, nDs_gen, nbkg2_gen))

#r = extended_model.fitTo(data,NumCPU=4, Extended=ROOT.kTRUE,PrintLevel=-1, Save=1,SumW2Error=True)
r_gen = extended_model_gen.fitTo(data,  RooFit.Extended(True), RooFit.PrintLevel(3), RooFit.Save(1),RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4))




#D-####################################################
# mychain_cc = ROOT.TChain(tree_name)

# for i in file_list:
#     mychain_cc.Add(i)

# print(file_list)


# # Define variable and its range
# fit_variable = "Dp_M"
# fit_var_name = "M(D^{+}) [GeV/c^{2}]"
# fit_range = (1.76, 2.05)
# rank_var = tree_name + "_rank"
# truth_var = "Dp_isSignal"
# charge_var = "Pip_charge"

# # Cuts
# cuts = rank_var + "==1" 
# cuts += " && " + charge_var + "==-1"

# # Create RooRealVar
# y = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
# y.setBins(70)
# chiProb_rank_cc = ROOT.RooRealVar(rank_var, rank_var, 0, 30)
# Pip_charge_cc = ROOT.RooRealVar(charge_var, charge_var, -1, 1)


# print(cuts)
# before_data_cc = ROOT.RooDataSet("data","", mychain_cc, ROOT.RooArgSet(y,chiProb_rank_cc,Pip_charge_cc), cuts)
# # before_data_cc = ROOT.RooDataHist("data","", mychain_cc, ROOT.RooArgSet(y,chiProb_rank_cc,Pip_charge_cc), cuts)


# w_1_cc = ROOT.RooRealVar('w_1', 'w', 0,1)
# w_1_cc.setVal(1)
# before_data_cc.addColumn(w_1_cc)
# data_cc = ROOT.RooDataSet(before_data_cc.GetName(), before_data_cc.GetTitle(),before_data_cc, before_data_cc.get(), '' ,  'w_1')
# data_cc = ROOT.RooDataHist(before_data_cc.GetName(), before_data_cc.GetTitle(),before_data_cc, before_data_cc.get(), '' ,  'w_1')

cut_expression = "Pip_charge==-1"
data_cc = before_data_weighted.reduce(cut_expression)



N_total_cc = data_cc.sumEntries()
print(N_total_cc)

#mean_johnson = ROOT.RooRealVar("mean_johnson", "mean of Johnson", 1.86, 1.8, 1.9)
#sigma_johnson = ROOT.RooRealVar("sigma_johnson", "sigma of Johnson", 0.01, 0.00001, 0.5)
#gamma = ROOT.RooRealVar("gamma", "gamma of Johnson", 0.1, 0.001, 1)
#delta = ROOT.RooRealVar("delta", "delta of Johnson", 0.1, 0.001, 1)

# True+false fixed 24.07.19
mean_johnson_cc = ROOT.RooRealVar("mean_johnson_cc", "mean of Johnson", 1.8805)
sigma_johnson_cc = ROOT.RooRealVar("sigma_johnson_cc", "sigma of Johnson", 0.0028028)
gamma_cc = ROOT.RooRealVar("gamma_cc", "gamma of Johnson", 0.32250)
delta_cc = ROOT.RooRealVar("delta_cc", "delta of Johnson", 0.59443 )

mean_gaussian_cc = ROOT.RooRealVar("mean_gaussian_cc", "mean of Gaussian", 0, -1, 1)
sigma_gaussian_cc = ROOT.RooRealVar("sigma_gaussian_cc", "sigma of Gaussian", 0.01, 0.00001, 1)

# Create a Johnson distribution
johnson_cc = ROOT.RooJohnson("johnson_cc", "Johnson PDF", x, mean_johnson_cc, sigma_johnson_cc, gamma_cc, delta_cc)

# Create a Gaussian distribution
gaussian_cc = ROOT.RooGaussian("gaussian_cc", "Gaussian PDF", x, mean_gaussian_cc, sigma_gaussian_cc)

# Convolute the Johnson distribution with Gaussian
sig_model_cc = ROOT.RooFFTConvPdf("sig_model_cc", "Convolution of Johnson and Gaussian", x, johnson_cc, gaussian_cc)

#CB = ROOT.RooCrystalBall("CB", "CB", x, mean, sigma, alphaL, nL)


# sigma_gauss = ROOT.RooRealVar("sigma_gauss", "sigma", 0.02, 0.001, 0.1)
# gauss = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma_gauss)

# sig_fraction = ROOT.RooRealVar("sig_fraction", "fraction", 0.5, 0.0, 1.0)
# sig_model = ROOT.RooAddPdf("sig_model", "sig_model", ROOT.RooArgList(CB, gauss),ROOT.RooArgList(sig_fraction))


#Ds_mean_johnson = ROOT.RooRealVar("Ds_mean_johnson", "mean of Johnson", 1.96, 1.91, 1.98)
#Ds_sigma_johnson = ROOT.RooRealVar("Ds_sigma_johnson", "sigma of Johnson", 0.01, 0.00001, 0.5)
#Ds_gamma = ROOT.RooRealVar("Ds_gamma", "gamma of Johnson", 0.1, 0.001, 1)
#Ds_delta = ROOT.RooRealVar("Ds_delta", "delta of Johnson", 0.1, 0.001, 1)

# True+false fixed 24.07.19
Ds_mean_johnson_cc = ROOT.RooRealVar("Ds_mean_johnson_cc", "mean of Johnson", 1.9934)
Ds_sigma_johnson_cc = ROOT.RooRealVar("Ds_sigma_johnson_cc", "sigma of Johnson",  0.0016496)
Ds_gamma_cc = ROOT.RooRealVar("Ds_gamma_cc", "gamma of Johnson",  0.35250)
Ds_delta_cc = ROOT.RooRealVar("Ds_delta_cc", "delta of Johnson", 0.47138)


Ds_mean_gaussian_cc = ROOT.RooRealVar("Ds_mean_gaussian_cc", "mean of Gaussian", 0, -1, 1)
Ds_sigma_gaussian_cc = ROOT.RooRealVar("Ds_sigma_gaussian_cc", "sigma of Gaussian", 0.01, 0.00001, 1)

# Create a Johnson distribution
Ds_johnson_cc = ROOT.RooJohnson("Ds_johnson_cc", "Johnson PDF", x, Ds_mean_johnson_cc, Ds_sigma_johnson_cc, Ds_gamma_cc, Ds_delta_cc)

# Create a Gaussian distribution
Ds_gaussian_cc = ROOT.RooGaussian("Ds_gaussian_cc", "Gaussian PDF", x, Ds_mean_gaussian_cc, Ds_sigma_gaussian_cc)

# Convolute the Johnson distribution with Gaussian
Ds_model_cc = ROOT.RooFFTConvPdf("Ds_model_cc", "Convolution of Johnson and Gaussian", x, Ds_johnson_cc, Ds_gaussian_cc)

rhopeta_mean_cc = ROOT.RooRealVar("rhopeta_mean_cc", "mean", 1.75, 1.65, 1.8)
rhopeta_sigma_cc = ROOT.RooRealVar("rhopeta_sigma_cc", "sigma", 0.03, 0.001, 0.05)
rhopeta_model_cc = ROOT.RooGaussian("rhopeta_model_cc", "gauss", x, rhopeta_mean_cc, rhopeta_sigma_cc)

x_bkg1_Cheby_c0_cc = ROOT.RooRealVar("x_bkg1_Cheby_c0_cc", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c1_cc = ROOT.RooRealVar("x_bkg1_Cheby_c1_cc", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c2_cc = ROOT.RooRealVar("x_bkg1_Cheby_c2_cc", "c0",0.0, -1.0, 1.0)
x_bkg1_tau_cc = ROOT.RooRealVar("x_bkg1_tau_cc", "c0",-0.5, -20, 0)

#bkg_model = ROOT.RooPolynomial("bkg_model", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1))
bkg_model_cc = ROOT.RooExponential("bkg_model_cc", "x_bkg1", x, x_bkg1_tau_cc)


nsig_cc = ROOT.RooRealVar("nsig_cc","# signal events",N_total_cc*0.01,0,N_total_cc*0.8)
nbkg1_cc = ROOT.RooRealVar("nbkg1_cc","# bkg events",N_total_cc*0.8,0, N_total_cc)
nbkg2_cc = ROOT.RooRealVar("nbkg2_cc","# bkg events",N_total_cc*0.2,0, N_total_cc)
nDs_cc = ROOT.RooRealVar("nDs_cc","# bkg events",N_total_cc*0.8,0, N_total_cc)


extended_model_cc = ROOT.RooAddPdf("extended_model", "x_model", ROOT.RooArgSet(sig_model_cc,bkg_model_cc, Ds_model_cc, rhopeta_model_cc), ROOT.RooArgSet(nsig_cc, nbkg1_cc, nDs_cc, nbkg2_cc))

#r = extended_model.fitTo(data,NumCPU=4, Extended=ROOT.kTRUE,PrintLevel=-1, Save=1,SumW2Error=True)
r_cc = extended_model_cc.fitTo(data_cc,  RooFit.Extended(True), RooFit.PrintLevel(3), RooFit.Save(1),RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(15))

###################################################
#Gen_D-####################################################
# True+false fixed 24.07.19
mean_johnson_cc_gen = ROOT.RooRealVar("mean_johnson_cc_gen", "mean of Johnson", 1.8805)
sigma_johnson_cc_gen = ROOT.RooRealVar("sigma_johnson_cc_gen", "sigma of Johnson", 0.0028028)
gamma_cc_gen = ROOT.RooRealVar("gamma_cc_gen", "gamma of Johnson", 0.32250)
delta_cc_gen = ROOT.RooRealVar("delta_cc_gen", "delta of Johnson", 0.59443 )



#Wrong before 24.07.22
#mean_gaussian_cc_gen = ROOT.RooRealVar("mean_gaussian_cc_gen", "mean of Gaussian", 0, -1, 1)
#sigma_gaussian_cc_gen = ROOT.RooRealVar("sigma_gaussian_cc_gen", "sigma of Gaussian", 0.01, 0.00001, 1)
mean_gaussian_cc_gen = ROOT.RooRealVar("mean_gaussian_cc_gen", "mean of Gaussian", mean_gaussian_cc.getVal(), -1, 1)
sigma_gaussian_cc_gen = ROOT.RooRealVar("sigma_gaussian_cc_gen", "sigma of Gaussian", sigma_gaussian_cc.getVal(), 0.00001, 1)

# Create a Johnson distribution
johnson_cc_gen = ROOT.RooJohnson("johnson_cc_gen", "Johnson PDF", x, mean_johnson_cc_gen, sigma_johnson_cc_gen, gamma_cc_gen, delta_cc_gen)

# Create a Gaussian distribution
gaussian_cc_gen = ROOT.RooGaussian("gaussian_cc_gen", "Gaussian PDF", x, mean_gaussian_cc_gen, sigma_gaussian_cc_gen)

# Convolute the Johnson distribution with Gaussian
sig_model_cc_gen = ROOT.RooFFTConvPdf("sig_model_cc_gen", "Convolution of Johnson and Gaussian", x, johnson_cc_gen, gaussian_cc_gen)

# True+false fixed 24.07.19
Ds_mean_johnson_cc_gen = ROOT.RooRealVar("Ds_mean_johnson_cc_gen", "mean of Johnson", 1.9934)
Ds_sigma_johnson_cc_gen = ROOT.RooRealVar("Ds_sigma_johnson_cc_gen", "sigma of Johnson",  0.0016496)
Ds_gamma_cc_gen = ROOT.RooRealVar("Ds_gamma_cc_gen", "gamma of Johnson",  0.35250)
Ds_delta_cc_gen = ROOT.RooRealVar("Ds_delta_cc_gen", "delta of Johnson", 0.47138)

Ds_mean_gaussian_cc_gen = ROOT.RooRealVar("Ds_mean_gaussian_cc_gen", "mean of Gaussian", Ds_mean_gaussian_cc.getVal(), -1, 1)
Ds_sigma_gaussian_cc_gen = ROOT.RooRealVar("Ds_sigma_gaussian_cc_gen", "sigma of Gaussian", Ds_sigma_gaussian_cc.getVal(), 0.00001, 1)

# Create a Johnson distribution
Ds_johnson_cc_gen = ROOT.RooJohnson("Ds_johnson_cc_gen", "Johnson PDF", x, Ds_mean_johnson_cc_gen, Ds_sigma_johnson_cc_gen, Ds_gamma_cc_gen, Ds_delta_cc_gen)

# Create a Gaussian distribution
Ds_gaussian_cc_gen = ROOT.RooGaussian("Ds_gaussian_cc_gen", "Gaussian PDF", x, Ds_mean_gaussian_cc_gen, Ds_sigma_gaussian_cc_gen)

# Convolute the Johnson distribution with Gaussian
Ds_model_cc_gen = ROOT.RooFFTConvPdf("Ds_model_cc_gen", "Convolution of Johnson and Gaussian", x, Ds_johnson_cc_gen, Ds_gaussian_cc_gen)

rhopeta_mean_cc_gen = ROOT.RooRealVar("rhopeta_mean_cc_gen", "mean", rhopeta_mean_cc.getVal(), 1.65, 1.8)
rhopeta_sigma_cc_gen = ROOT.RooRealVar("rhopeta_sigma_cc_gen", "sigma", rhopeta_sigma_cc.getVal(), 0.001, 0.05)
rhopeta_model_cc_gen = ROOT.RooGaussian("rhopeta_model_cc_gen", "gauss", x, rhopeta_mean_cc_gen, rhopeta_sigma_cc_gen)

x_bkg1_Cheby_c0_cc_gen = ROOT.RooRealVar("x_bkg1_Cheby_c0_cc_gen", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c1_cc_gen = ROOT.RooRealVar("x_bkg1_Cheby_c1_cc_gen", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c2_cc_gen = ROOT.RooRealVar("x_bkg1_Cheby_c2_cc_gen", "c0",0.0, -1.0, 1.0)
x_bkg1_tau_cc_gen = ROOT.RooRealVar("x_bkg1_tau_cc_gen", "c0",x_bkg1_tau_cc.getVal(), -20, 0)

#bkg_model = ROOT.RooPolynomial("bkg_model", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1))
bkg_model_cc_gen = ROOT.RooExponential("bkg_model_cc_gen", "x_bkg1", x, x_bkg1_tau_cc_gen)


nsig_cc_gen = ROOT.RooRealVar("nsig_cc_gen","# signal events",nsig_cc.getVal(),0,N_total_cc*0.8)
nbkg1_cc_gen = ROOT.RooRealVar("nbkg1_cc_gen","# bkg events", nbkg1_cc.getVal(),0, N_total_cc)
nbkg2_cc_gen = ROOT.RooRealVar("nbkg2_cc_gen","# bkg events", nbkg2_cc.getVal(),0, N_total_cc)
nDs_cc_gen = ROOT.RooRealVar("nDs_cc_gen","# bkg events",     nDs_cc.getVal() ,0, N_total_cc)


extended_model_cc_gen = ROOT.RooAddPdf("extended_model_gen", "x_model", ROOT.RooArgSet(sig_model_cc_gen,bkg_model_cc_gen, Ds_model_cc_gen, rhopeta_model_cc_gen), ROOT.RooArgSet(nsig_cc_gen, nbkg1_cc_gen, nDs_cc_gen, nbkg2_cc_gen))

#r = extended_model.fitTo(data,NumCPU=4, Extended=ROOT.kTRUE,PrintLevel=-1, Save=1,SumW2Error=True)
r_cc_gen = extended_model_cc_gen.fitTo(data_cc,  RooFit.Extended(True), RooFit.PrintLevel(3), RooFit.Save(1),RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(15))

###################################################



#r = extended_model.fitTo(data, ROOT.RooFit.PrintLevel(-1), Save=1,SumW2Error=True)

# Parameters for the simulation
n_iterations = 100
N_total_input_Dp = nsig.getVal() + nbkg1.getVal() +  nbkg2.getVal() + nDs.getVal()
N_total_input_Dm = nsig_cc.getVal() + nbkg1_cc.getVal() +  nbkg2_cc.getVal() + nDs_cc.getVal()

# Arrays to store the results
n_gen_Dp = []
n_gen_Dm = []
n_gen_Dp_after = []
n_gen_Dm_after = []
nsig_Dp_values = []
nsig_Dp_errors = []
nsig_Dm_values = []
nsig_Dm_errors = []
pull_Dp = []
pull_Dm = []

n_gen_Acp = []
n_recon_Acp = []
n_recon_err_Acp = []
pull_Acp = []

def Acp_error_cal(Nsig, Nsig_cc, Nsig_err, Nsig_cc_err):
    Z = (Nsig - Nsig_cc)/(Nsig + Nsig_cc)
    dsig = Z * (2*Nsig_cc/ (Nsig**2 - Nsig_cc**2) ) * Nsig_err
    dsig_cc = Z * (2*Nsig/ (Nsig**2 - Nsig_cc**2) ) * Nsig_cc_err
    
    dZ_square = dsig**2 + dsig_cc**2
    return math.sqrt(dZ_square)

# Perform multiple fits
for i in range(n_iterations):
    print("for loop:" + str(i))
    # Generate the number of signal and background events based on the fixed total number of events
    #poisson_nsig = int(N_total * frac_sig)
    #poisson_nbkg = N_total - poisson_nsig
    n_gen_Dp.append(nsig_gen.getVal())
    n_gen_Dm.append(nsig_cc_gen.getVal())

    seed = int(time.time())
    RooRandom.randomGenerator().SetSeed(seed)
    
    #N_total_Dp = RooRandom.randomGenerator().Poisson(N_total_input_Dp)
    #N_total_Dm = RooRandom.randomGenerator().Poisson(N_total_input_Dm)
    N_total_Dp = N_total_input_Dp
    N_total_Dm = N_total_input_Dm

    # Generate a dataset from the extended model
    # data_Dp = extended_model.generate(RooArgSet(x), N_total_Dp)  # Generate data with the fixed total number of events
    # data_Dm = extended_model_cc.generate(RooArgSet(y), N_total_Dm)  # Generate data with the fixed total number of events
    data_Dp = extended_model_gen.generateBinned(RooArgSet(x), RooFit.Extended(True), RooFit.NumEvents(N_total_Dp))  # Generate data with the fixed total number of events
    data_Dm = extended_model_cc_gen.generateBinned(RooArgSet(x),RooFit.Extended(True), RooFit.NumEvents(N_total_Dm))  # Generate data with the fixed total number of events
    #toy_data = model.generate(ROOT.RooArgSet(mass), RooFit.Extended(True), RooFit.NumEvents(nEvents))

    n_gen_Dp_after.append(nsig_gen.getVal())
    n_gen_Dm_after.append(nsig_cc_gen.getVal())
    n_gen_Acp.append( (nsig_gen.getVal()-nsig_cc_gen.getVal())/(nsig_gen.getVal()+nsig_cc_gen.getVal()) )


    # Fit the extended PDF to the dataset
    result_Dp = extended_model.fitTo(data_Dp, RooFit.Extended(True), RooFit.Save(True), RooFit.PrintLevel(-1), ROOT.RooFit.NumCPU(15))
    result_Dm = extended_model_cc.fitTo(data_Dm, RooFit.Extended(True), RooFit.Save(True), RooFit.PrintLevel(-1) , ROOT.RooFit.NumCPU(15))

    # Save the fitted number of signal and background events and their errors
    nsig_Dp_values.append(nsig.getVal())
    nsig_Dp_errors.append(nsig.getError())
    nsig_Dm_values.append(nsig_cc.getVal())
    nsig_Dm_errors.append(nsig_cc.getError())
    n_recon_Acp.append( (nsig.getVal()-nsig_cc.getVal())/(nsig.getVal()+nsig_cc.getVal()) )
    n_recon_err_Acp.append( Acp_error_cal(nsig.getVal(), nsig_cc.getVal(), nsig.getError(), nsig_cc.getError()) )

# Calculate the pull distribution for signal and background
# pulls_Acp = [(val - Ngen) / err for Ngen, val, err in zip(n_gen_Acp, n_recon_Acp, n_recon_Acp_errors)]
#pulls_Acp = [(val - Ngen) / err for Ngen, val, err in zip(n_gen_Acp, n_recon_Acp, n_recon_err_Acp)]

# Save to a file
# output_json_file='v6_100_' + str(sys.argv[1]) + '.json'
# with open(output_json_file, 'w') as f:
#     json.dump({'n_gen_Acp': n_gen_Acp, 'n_recon_Acp': n_recon_Acp, 'n_recon_err_Acp': n_recon_err_Acp, 'n_gen_Dp': n_gen_Dp, 'n_gen_Dm': n_gen_Dm, 'n_gen_Dp_after': n_gen_Dp_after, 'n_gen_Dm_after': n_gen_Dm_after, 'nsig_Dp_values': nsig_Dp_values, 'nsig_Dp_errors': nsig_Dp_errors, 'nsig_Dm_values': nsig_Dm_values, 'nsig_Dm_errors': nsig_Dm_errors}, f)

pulls_Acp = [(val - Ngen) / err for Ngen, val, err in zip(n_gen_Acp, n_recon_Acp, n_recon_err_Acp)]
pulls_Dp = [(val - Ngen) / err for Ngen, val, err in zip(n_gen_Dp_after, nsig_Dp_values, nsig_Dp_errors)]
pulls_Dm = [(val - Ngen) / err for Ngen, val, err in zip(n_gen_Dm_after, nsig_Dm_values, nsig_Dm_errors)]

# Create a new ROOT file
root_file_name='v6_100_' + str(sys.argv[1]) + '.root'

root_file = ROOT.TFile(root_file_name, "RECREATE")

# Create a TTree
tree = ROOT.TTree("toymc", "Toy MC Tree")

# Define arrays to hold the data for each branch
n_gen_Dp_val = ROOT.std.vector('double')()
n_gen_Dm_val = ROOT.std.vector('double')()
n_gen_Dp_after_val = ROOT.std.vector('double')()
n_gen_Dm_after_val = ROOT.std.vector('double')()
nsig_Dp_values_val = ROOT.std.vector('double')()
nsig_Dp_errors_val = ROOT.std.vector('double')()
nsig_Dm_values_val = ROOT.std.vector('double')()
nsig_Dm_errors_val = ROOT.std.vector('double')()
pulls_Dp_val = ROOT.std.vector('double')()
pulls_Dm_val = ROOT.std.vector('double')()

n_gen_Acp_val = ROOT.std.vector('double')()
n_recon_Acp_val = ROOT.std.vector('double')()
n_recon_err_Acp_val = ROOT.std.vector('double')()
pulls_Acp_val = ROOT.std.vector('double')()

# Create branches
tree.Branch("n_gen_Dp", n_gen_Dp_val)
tree.Branch("n_gen_Dm", n_gen_Dm_val)
tree.Branch("n_gen_Dp_after", n_gen_Dp_after_val)
tree.Branch("n_gen_Dm_after", n_gen_Dm_after_val)
tree.Branch("nsig_Dp_values", nsig_Dp_values_val)
tree.Branch("nsig_Dp_errors", nsig_Dp_errors_val)
tree.Branch("nsig_Dm_values", nsig_Dm_values_val)
tree.Branch("nsig_Dm_errors", nsig_Dm_errors_val)
tree.Branch("pulls_Dp", pulls_Dp_val)
tree.Branch("pulls_Dm", pulls_Dm_val)

tree.Branch("n_gen_Acp", n_gen_Acp_val)
tree.Branch("n_recon_Acp", n_recon_Acp_val)
tree.Branch("n_recon_err_Acp", n_recon_err_Acp_val)
tree.Branch("pulls_Acp", pulls_Acp_val)

# Fill the tree with data
for i in range(len(n_gen_Dp)):
    n_gen_Dp_val.clear()
    n_gen_Dm_val.clear()
    n_gen_Dp_after_val.clear()
    n_gen_Dm_after_val.clear()
    nsig_Dp_values_val.clear()
    nsig_Dp_errors_val.clear()
    nsig_Dm_values_val.clear()
    nsig_Dm_errors_val.clear()
    pulls_Dp_val.clear()
    pulls_Dm_val.clear()

    n_gen_Acp_val.clear()
    n_recon_Acp_val.clear()
    n_recon_err_Acp_val.clear()
    pulls_Acp_val.clear()

    n_gen_Dp_val.push_back(n_gen_Dp[i])
    n_gen_Dm_val.push_back(n_gen_Dm[i])
    n_gen_Dp_after_val.push_back(n_gen_Dp_after[i])
    n_gen_Dm_after_val.push_back(n_gen_Dm_after[i])
    nsig_Dp_values_val.push_back(nsig_Dp_values[i])
    nsig_Dp_errors_val.push_back(nsig_Dp_errors[i])
    nsig_Dm_values_val.push_back(nsig_Dm_values[i])
    nsig_Dm_errors_val.push_back(nsig_Dm_errors[i])
    pulls_Dp_val.push_back(pulls_Dp[i])
    pulls_Dm_val.push_back(pulls_Dm[i])

    n_gen_Acp_val.push_back(n_gen_Acp[i])
    n_recon_Acp_val.push_back(n_recon_Acp[i])
    n_recon_err_Acp_val.push_back(n_recon_err_Acp[i])
    pulls_Acp_val.push_back(pulls_Acp[i])

    tree.Fill()

# Write the tree to the file
tree.Write()

# Close the file
root_file.Close()
