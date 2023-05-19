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
ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/Belle2Style.C')
ROOT.SetBelle2Style()
base_file_loc =  '/media/jykim/T7/storage/01_recon/massvetov2_sig_ext_1ab_sigbkg/'

# phigamma_ccbar = base_file_loc + 'topo/skim_1abinv_phi_D0_M/topoana.root'
phigamma_ccbar = base_file_loc + 'ccbar/recon_udst_*.root'
phigamma_uubar = base_file_loc + 'uubar/recon_udst_*.root'
phigamma_ddbar = base_file_loc + 'ddbar/recon_udst_*.root'
phigamma_ssbar = base_file_loc + 'ssbar/recon_udst_*.root'
phigamma_charged = base_file_loc + 'charged/recon_udst_*.root'
phigamma_mixed = base_file_loc + 'mixed/recon_udst_*.root'
phigamma_taupair = base_file_loc + 'taupair/recon_udst_*.root'


# base_filter=' Pi0_Prob<0.80 && Pis_charge==1 && D0_M>1.7 && D0_M<2.03 '
base_filter='Belle2Pi0Veto_75MeV > 0.022 && D0_M>1.67 && D0_M<2.06 '

# base_filter=' Pi0_Prob<0.90 && Pis_charge==-1 && D0_M>1.72 && D0_M<2.01 '

#base_filter='Pi0_Prob<0.90  && D0_M>1.67 && D0_M<2.06 '

# base_filter='Pi0_Prob<0.95 && phi_rank_Dstp==1 && D0_M>1.67 && D0_M<2.06'

#ccbar_filter='Pi0_Prob<0.9 && Pis_charge==1 && D0_M>1.67 && D0_M<2.06 && (iCascDcyBrP_Dst_0 !=1 && iCascDcyBrP_Dst_0 !=2)'
# ccbar_filter='Pi0_Prob<0.9 && Pis_charge==1 && D0_M>1.67 && D0_M<2.06 '


#ccbar_filter='Pi0_Prob<0.9 && D0_M>1.67 && D0_M<2.06 && (iCascDcyBrP_D0_0 !=0 ) && (phi_rank_Dstp ==1)'

variables=['D0_M','D0_cosHel_0']
tree='phi'

pd_phigamma_ccbar = get_pd(file=phigamma_ccbar, tree=tree,base_filter=base_filter,variables=variables)

pd_phigamma_uubar = get_pd(file=phigamma_uubar, tree=tree,base_filter=base_filter,variables=variables)
pd_phigamma_ddbar = get_pd(file=phigamma_ddbar, tree=tree,base_filter=base_filter,variables=variables)
pd_phigamma_ssbar = get_pd(file=phigamma_ssbar, tree=tree,base_filter=base_filter,variables=variables)
pd_phigamma_charged = get_pd(file=phigamma_charged, tree=tree,base_filter=base_filter,variables=variables)
pd_phigamma_mixed = get_pd(file=phigamma_mixed, tree=tree,base_filter=base_filter,variables=variables)
pd_phigamma_taupair = get_pd(file=phigamma_taupair, tree=tree,base_filter=base_filter,variables=variables)



phigamma_generic=pd.concat([pd_phigamma_ccbar,
                           pd_phigamma_uubar,
                           pd_phigamma_ddbar,
                           pd_phigamma_ssbar,
                           pd_phigamma_charged,
                           pd_phigamma_mixed,
                           pd_phigamma_taupair],ignore_index=True)


D0_M_pd_data = phigamma_generic['D0_M']
D0_cosHel_0_pd_data = phigamma_generic['D0_cosHel_0']

D0_M_np_data = D0_M_pd_data.to_numpy()
D0_cosHel_0_np_data = D0_cosHel_0_pd_data.to_numpy()


ROOT.RooClassFactory.makePdf("MyPdf_xsquared_nopara", "x", "", "x*x")
ROOT.gROOT.ProcessLineSync(".x MyPdf_xsquared_nopara.cxx+")

ROOT.RooClassFactory.makePdf("MyPdf_one_minus_squared", "y", "", "1-y*y")
ROOT.gROOT.ProcessLineSync(".x MyPdf_one_minus_squared.cxx+")




####################
#D0_M
x = ROOT.RooRealVar("M(D^{0})", "M(D^{0}) [GeV/c^{2}]", 1.67, 2.06, "")
# x = ROOT.RooRealVar("M(D^{0})", "M(D^{0}) [GeV/c^{2}]", 1.72, 2.01, "")

# x.setBins(50)

#### Construct signal model for x
x_sig_mean = ROOT.RooRealVar("x_sig_mean", "mean of gaussians", 1.863,1.86, 1.88)
x_sig_sigma1 = ROOT.RooRealVar("x_sig_sigma1", "width of gaussians", 0.03,0,0.03)
x_sig_sigma2 = ROOT.RooRealVar("x_sig_sigma2", "width of gaussians", 0.01,0.005,0.02)
#x_sig_sigma3 = ROOT.RooRealVar("x_sig_sigma3", "width of gaussians", 0.03,0,0.7)

x_sig_alpha = ROOT.RooRealVar("x_sig_alpha", "width of gaussians", 5,2,10)
x_sig_n_CB = ROOT.RooRealVar("x_sig_n_CB", "width of gaussians", 5,1,10)

# x_sig_alpha = ROOT.RooRealVar("x_sig_alpha", "width of gaussians", 0.5,0.1,10)
# x_sig_n_CB = ROOT.RooRealVar("x_sig_n_CB", "width of gaussians", 3,0.1,5)

#Novo_peak = ROOT.RooRealVar("Novo_peak", "Novo peak", 1.83,1.73,1.93)    
#x_sig_Novo_width = ROOT.RooRealVar("x_sig_Novo_width", "Novo peak", 0.05,0,0.5)    
#x_sig_Novo_tail = ROOT.RooRealVar("x_sig_Novo_tail", "Novo peak", 0.5,0,10)    

# x_sig_1 = ROOT.RooGaussian("x_sig_1", "Signal component 1", x, x_sig_mean, x_sig_sigma1)
# x_sig_2 = ROOT.RooCBShape("x_sig_2", "Signal component 2", x, x_sig_mean, x_sig_sigma2, x_sig_alpha, x_sig_n_CB)
# # #x_sig_3 = ROOT.RooGaussian("x_sig_3", "Signal component 1", x, x_sig_mean, x_sig_sigma3)
# # #x_sig_3 = ROOT.RooNovosibirsk("x_sig_3", "Signal component 3", x, x_sig_mean, x_sig_Novo_width, x_sig_Novo_tail)

# x_sig1frac = ROOT.RooRealVar("x_sig1frac", "fraction of component 1 in signal", 0.2, 0.0, 1.0)
# # # x_sig_sum1 = ROOT.RooAddPdf("x_sig_sum1", "Signal1", [x_sig_2, x_sig_1], x_sig1frac)
# x_sig_model = ROOT.RooAddPdf("x_sig_model", "Signal1", [x_sig_2, x_sig_1], x_sig1frac)



#x_sig2frac = ROOT.RooRealVar("x_sig2frac", "fraction of component 2 in signal", 0.2, 0.0, 1.0)
#x_sig_model = ROOT.RooAddPdf("x_sig_model", "Signal", [x_sig_3, x_sig_sum1], x_sig2frac)
# 
#x_sig_1 = ROOT.RooCBShape("x_sig_1", "Signal component 2", x, x_sig_mean, x_sig_sigma2, x_sig_alpha, x_sig_n_CB)


#x_sig_2 = ROOT.RooGaussian("x_sig_2", "Signal component 2", x, x_sig_mean, x_sig_sigma1)

#x_sig1frac = ROOT.RooRealVar("x_sig1frac", "fraction of component 1 in signal", 0.5, 0.0, 1.0)
#x_sig_model = ROOT.RooAddPdf("x_sig_model", "Signal1", [x_sig_2, x_sig_1], x_sig1frac)



x_sig_model = ROOT.RooCBShape("x_sig_model", "Signal component 2", x, x_sig_mean, x_sig_sigma2, x_sig_alpha, x_sig_n_CB)



#### Construct bkg model for x
#phi pi0
x_bkg1_mean = ROOT.RooRealVar("x_bkg1_mean", "mean of gaussians", 1.835,1.83, 1.85)
x_bkg1_sigma1 = ROOT.RooRealVar("x_bkg1_sigma1", "width of gaussians", 0.03,0,0.5)
x_bkg1_sigma2 = ROOT.RooRealVar("x_bkg1_sigma2", "width of gaussians",0.05,0,0.1)
# x_bkg1_sigma3 = ROOT.RooRealVar("x_bkg1_sigma3", "width of gaussians", 0.02,0,0.5)

x_bkg1_alpha = ROOT.RooRealVar("x_bkg1_alpha", "width of gaussians",  0.2,0.,5)
x_bkg1_n_CB = ROOT.RooRealVar("x_bkg1_n_CB", "width of gaussians", 3,0,10)
    
x_bkg1_1 = ROOT.RooGaussian("x_bkg1_1", "Signal component 1", x, x_bkg1_mean, x_bkg1_sigma1)
x_bkg1_2 = ROOT.RooCBShape("x_bkg1_2", "Signal component 2", x, x_bkg1_mean, x_bkg1_sigma2, x_bkg1_alpha, x_bkg1_n_CB)

#x_bkg1frac = ROOT.RooRealVar("x_bkg1frac", "fraction of component 1 in signal", 0.5, 0.0, 1.0)
#x_bkg1_model = ROOT.RooAddPdf("x_bkg1_model", "Signal1", [x_bkg1_2, x_bkg1_1], x_bkg1frac)

# #x_bkg1_model = ROOT.RooCBShape("x_bkg1_model", "Signal component 2", x, x_bkg1_mean, x_bkg1_sigma2, x_bkg1_alpha, x_bkg1_n_CB)

# x_bkg1_mean = ROOT.RooRealVar("x_bkg1_mean", "mean of gaussians", 1.83,1.82, 1.85)

# x_bkg1_sigma2 = ROOT.RooRealVar("x_bkg1_sigma2", "width of gaussians", 0.05,0,0.1)
# x_bkg1_alpha = ROOT.RooRealVar("x_bkg1_alpha", "width of gaussians", 0.5,0,1)
# x_bkg1_n_CB = ROOT.RooRealVar("x_bkg1_n_CB", "width of gaussians", 3,0,10)
 
# x_bkg1_Novo_peak = ROOT.RooRealVar("x_bkg1_Novo_peak", "Novo peak", 1.83,1.67,1.93)    
# x_bkg1_Novo_width = ROOT.RooRealVar("x_bkg1_Novo_widh", "Novo peak", 0.05,0,0.5)    
# x_bkg1_Novo_tail = ROOT.RooRealVar("x_bkg1_Novo_tail", "Novo peak", 0.5,0,10)    

#x_bkg1_1 = ROOT.RooCBShape("x_bkg1_1", "Signal component 2", x, x_bkg1_mean, x_bkg1_sigma2, x_bkg1_alpha, x_bkg1_n_CB)

#x_bkg1_1 = ROOT.RooGaussian("x_bkg1_1", "Signal component 2", x, x_bkg1_mean, x_bkg1_sigma1)
#x_bkg1_2 = ROOT.RooNovosibirsk("x_bkg1_2", "Signal component 3", x, x_bkg1_mean, x_bkg1_Novo_width, x_bkg1_Novo_tail)
#x_bkg1_2 = ROOT.RooCBShape("x_bkg1_2", "Signal component 2", x, x_bkg1_mean, x_bkg1_sigma2, x_bkg1_alpha, x_bkg1_n_CB)


x_bkg1frac1 = ROOT.RooRealVar("x_bkg1frac1", "fraction of component 1 in signal", 0.5,  0.0, 1.0)
x_bkg1_model = ROOT.RooAddPdf("x_bkg1_model", "Signal1", [x_bkg1_2, x_bkg1_1], x_bkg1frac1)

# x_bkg1_model = ROOT.RooCBShape("x_bkg1_model", "Signal component 2", x, x_bkg1_mean, x_bkg1_sigma2, x_bkg1_alpha, x_bkg1_n_CB)

####BKG2
# remaining
#x_bkg2_tau = ROOT.RooRealVar("x_bkg2_tau", "tau",-10, -50,0)


# x_bkg2_mean = ROOT.RooRealVar("x_bkg2_mean", "mean of gaussians", 1.83,1.81, 1.84)
# x_bkg2_sigma1 = ROOT.RooRealVar("x_bkg2_sigma1", "width of gaussians", 0.04,0.01,0.05)

#x_bkg2_mean = ROOT.RooRealVar("x_bkg2_mean", "mean of gaussians", 1.65,1.58, 1.68)
#x_bkg2_sigma1 = ROOT.RooRealVar("x_bkg2_sigma1", "width of gaussians", 0.015,0.008,0.2)
#
#x_bkg2_mean = ROOT.RooRealVar("x_bkg2_mean", "mean of gaussians", 1.83,1.81, 1.85)
#x_bkg2_sigma1 = ROOT.RooRealVar("x_bkg2_sigma1", "width of gaussians", 0.01,0.001,0.05)

# x_bkg2_mean = ROOT.RooRealVar("x_bkg2_mean", "mean of gaussians", 1.83,1.80, 1.85)
# x_bkg2_sigma1 = ROOT.RooRealVar("x_bkg2_sigma1", "width of gaussians", 0.05,0.03,0.08)


#x_bkg2_sigma2 = ROOT.RooRealVar("x_bkg2_sigma2", "width of gaussians", 0.05,0.01,0.5)

#x_bkg2_mean2 = ROOT.RooRealVar("x_bkg2_mean2", "mean of gaussians", 1.83,1.81, 1.84)

#x_bkg2_sigma2 = ROOT.RooRealVar("x_bkg2_sigma2", "width of gaussians", 0.03,0.01,0.05)


# x_bkg2_mean2 = ROOT.RooRealVar("x_bkg2_mean", "mean of gaussians", 1.6,1.4, 1.7)
# x_bkg2_sigma2 = ROOT.RooRealVar("x_bkg2_sigma1", "width of gaussians", 0.05,0.03,0.5)
# 

x_bkg2_c0 = ROOT.RooRealVar("x_bkg2_c0", "c0",0.2, -1,1)
x_bkg2_c1 = ROOT.RooRealVar("x_bkg2_c1", "c1",0.2, -1,1)
# x_bkg2_c2 = ROOT.RooRealVar("x_bkg2_c2", "c1",0.2, -1,1)
#x_bkg2_c3 = ROOT.RooRealVar("x_bkg2_c3", "c1",0.3, -1,1)

#x_bkg2_mu =  ROOT.RooRealVar("x_bkg2_mu", "mean of gaussians", 1.81,1.78, 1.83)
#x_bkg2_lambda1 = ROOT.RooRealVar("x_bkg2_lambda1", "Novo peak", 0.2, 0.02, 2) 
#x_bkg2_gamma = ROOT.RooRealVar("x_bkg2_gamma", "Novo peak", 1, 0.5, 5) 
#x_bkg2_delta  = ROOT.RooRealVar("x_bkg2_delta", "Novo peak", 0.1, 0, 5) 


# x_bkg2_mean2 =  ROOT.RooRealVar("x_bkg2_mean2", "mean of gaussians", 1.82,1.80, 1.84)
# x_bkg2_sigmaL = ROOT.RooRealVar("x_bkg2_sigmaL", "Novo peak", 0.05, 0.02, 0.5) 
# x_bkg2_sigmaR = ROOT.RooRealVar("x_bkg2_sigmaR", "Novo peak", 0.05, 0.02, 0.5) 


# x_bkg2_3 = ROOT.RooJohnson("x_bkg2_3", "Signal component 1", x, x_bkg2_mu, x_bkg2_lambda1, x_bkg2_gamma, x_bkg2_delta)
#x_bkg2_1 = ROOT.RooExponential("x_bkg2_1", "Signal component 1", x, x_bkg2_tau)
#x_bkg2_2 = ROOT.RooPolynomial("x_bkg2_2", "Signal component 1", x, ROOT.RooArgList(x_bkg2_c1,x_bkg2_c2), lowestOrder=2)

# x_bkg2_1 = ROOT.RooExponential("x_bkg2_1", "Signal component 1", x, x_bkg2_tau)
# x_bkg2_1 = ROOT.RooGaussian("x_bkg2_1", "Signal component 1", x, x_bkg2_mean, x_bkg2_sigma1)
# x_bkg2_2 = ROOT.RooPolynomial("x_bkg2_2", "Signal component 1", x, ROOT.RooArgList(x_bkg2_c0), lowestOrder=1)


# x_bkg2_m0  =  ROOT.RooRealVar("x_bkg2_m0", "mean of gaussians", 1.8, 1.78, 1.83)
# x_bkg2_k =  ROOT.RooRealVar("x_bkg2_k", "mean of gaussians", 0.5, 0, 1)
# x_bkg2_3 = ROOT.RooLognormal("x_bkg2_3", "Signal component 3", x, x_bkg2_m0,x_bkg2_k)


# x_bkg2_1 = ROOT.RooGaussian("x_bkg2_1", "Signal component 1", x, x_bkg2_mean, x_bkg2_sigma1)
# x_bkg2_2 = ROOT.RooPolynomial("x_bkg2_2", "Signal component 1", x, ROOT.RooArgList(x_bkg2_c0, x_bkg2_c1), lowestOrder=2)
# x_bkg2_2 = ROOT.RooGaussian("x_bkg2_3", "Signal component 3", x, x_bkg2_mean2, x_bkg2_sigma2)

#x_bkg2_3 = ROOT.RooBifurGauss("x_bkg2_3", "Signal component 3", x, x_bkg2_mean2, x_bkg2_sigmaL, x_bkg2_sigmaR)

# x_bkg2_3 = ROOT.RooGaussian("x_bkg2_3", "Signal component 1", x, x_bkg2_mean, x_bkg2_sigma2)



# x_bkg2frac1 = ROOT.RooRealVar("x_bkg2frac1", "fraction of component 1 in signal", 0.5, 0.0, 1.0)
# x_bkg2_model = ROOT.RooAddPdf("x_bkg2_model", "Signal1", [x_bkg2_2, x_bkg2_1], x_bkg2frac1)


# x_bkg2_sum1 = ROOT.RooAddPdf("x_bkg2_sum1", "Signal1", [x_bkg2_2, x_bkg2_1], x_bkg2frac1)
# x_bkg2_model = ROOT.RooAddPdf("x_bkg2_model", "Signal1", [x_bkg2_3, x_bkg2_2], x_bkg2frac1)


# x_bkg2frac2 = ROOT.RooRealVar("x_bkg2frac2", "fraction of component 1 in signal", 0.9, 0.0, 1.0)
# x_bkg2_model = ROOT.RooAddPdf("x_bkg2_model", "Signal1", [x_bkg2_3, x_bkg2_sum1], x_bkg2frac2)

# x_bkg2_tau = ROOT.RooRealVar("x_bkg2_tau", "tau",-2, -5,0)
# x_bkg2_model = ROOT.RooExponential("x_bkg2_model", "Signal component 1", x, x_bkg2_tau)

x_bkg2_model = ROOT.RooPolynomial("x_bkg2_model", "Signal component 1", x, ROOT.RooArgList(x_bkg2_c0, x_bkg2_c1))


# x_bkg2_model = ROOT.RooChebychev("x_bkg2_model", "Signal component 1", x, ROOT.RooArgList(x_bkg2_c0, x_bkg2_c1))
#


# x_bkg2_1 = ROOT.RooExponential("x_bkg2_1", "Signal component 1", x, x_bkg2_tau)

# x_bkg2_2 = ROOT.RooPolynomial("x_bkg2_2", "Signal component 1", x, ROOT.RooArgList(x_bkg2_c0))
# x_bkg2frac1 = ROOT.RooRealVar("x_bkg2frac1", "fraction of component 1 in signal", 0.5, 0.0, 1.0)
# x_bkg2_model = ROOT.RooAddPdf("x_bkg2_model", "Signal1", [x_bkg2_2, x_bkg2_1], x_bkg2frac1)

#phipi0,Kshort K+k-
####BKG3
# x_bkg3_mean = ROOT.RooRealVar("x_bkg3_mean", "mean of gaussians", 1.65,1.58, 1.68)
# x_bkg3_sigma1 = ROOT.RooRealVar("x_bkg3_sigma1", "width of gaussians", 0.01,0,0.08)

# x_bkg3_model = ROOT.RooGaussian("x_bkg3_model", "Signal component 1", x,x_bkg3_mean, x_bkg3_sigma1)
#x_bkg3_mean = ROOT.RooRealVar("x_bkg3_mean", "mean of gaussians", 1.65,1.58, 1.7)
#x_bkg3_sigma1 = ROOT.RooRealVar("x_bkg3_sigma1", "width of gaussians", 0.01,0,0.07)


# x_bkg3_c0 = ROOT.RooRealVar("x_bkg3_c0", "c0",0.1, 0,1.)
# # c1 = ROOT.RooRealVar("c1", "c1",0.5, 0,1.)
# # c2 = ROOT.RooRealVar("c2", "c2",-0.3, -1.,0.)
# x_bkg3_1 = ROOT.RooPolynomial("x_bkg3_1", "Signal component 1", x, ROOT.RooArgList(x_bkg3_c0), lowestOrder=1)
    
# x_bkg3_tau = ROOT.RooRealVar("x_bkg3_tau", "tau",-2, -20,0)
# x_bkg3_2 = ROOT.RooExponential("x_bkg3_2", "Signal component 1", x, x_bkg3_tau)    

#x_bkg3_2 = ROOT.RooGaussian("x_bkg3_2", "Signal component 1", x, x_bkg3_mean, x_bkg3_sigma1)


# x_bkg3frac1  = ROOT.RooRealVar("x_bkg3frac1", "fraction of component 1 in signal", 0.5, 0.0, 1.0)
# x_bkg3_model = ROOT.RooAddPdf("x_bkg3_model", "Signal1", [x_bkg3_1, x_bkg3_2], x_bkg3frac1)

################
#D0_cosHel_0
yrange=(-1,1)
y = ROOT.RooRealVar("cos#theta_{H}", "cos#theta_{H}", yrange[0], yrange[1], "")
# y.setBins(50)

y_sig_model = ROOT.MyPdf_one_minus_squared("y_sig_model", "y_sig", y)




#### Construct bkg model for y
#phi pi0
y_bkg1_model = ROOT.MyPdf_xsquared_nopara("y_bkg1_model", "y_bkg1", y)

#remaining
y_bkg2_c0 = ROOT.RooRealVar("y_bkg2_c0", "c0",0.5, -1,1)
y_bkg2_c1 = ROOT.RooRealVar("y_bkg2_c1", "c1",0.2, -1,1)
# y_bkg2_c2 = ROOT.RooRealVar("y_bkg2_c2", "c2",0.3, -1,1)
#y_bkg2_model= ROOT.RooChebychev("y_bkg2_model", "Signal component 1", y, ROOT.RooArgList(y_bkg2_c0, y_bkg2_c1, y_bkg2_c2))
# y_bkg2_model= ROOT.RooChebychev("y_bkg2_model", "Signal component 1", y, ROOT.RooArgList(y_bkg2_c0, y_bkg2_c1))
y_bkg2_model= ROOT.RooPolynomial("y_bkg2_model", "Signal component 1", y, ROOT.RooArgList(y_bkg2_c0, y_bkg2_c1))
# y_bkg2_model= ROOT.RooChebychev("y_bkg2_model", "Signal component 1", y, ROOT.RooArgList(y_bkg2_c0, y_bkg2_c1,y_bkg2_c2))

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
# bkg3_xy_model = ROOT.RooProdPdf("bkg3_xy_model","bkg3_xy_model",ROOT.RooArgSet(x_bkg3_model,y_bkg3_model))


sig_model = ROOT.RooProdPdf("sig_model","sig_xy_model",ROOT.RooArgSet(x_sig_model, y_sig_model))


####################################
# construct signal + bkg pdf
nsig = ROOT.RooRealVar("nsig","# signal events",100,0,len(D0_M_np_data))
nbkg1 = ROOT.RooRealVar("nbkg1","# bkg events",600,0, len(D0_M_np_data))
nbkg2 = ROOT.RooRealVar("nbkg2","# bkg events",300,0, len(D0_M_np_data))
# nbkg3 = ROOT.RooRealVar("nbkg3","# bkg events",100,0, len(D0_M_np_data))

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

data = ROOT.RooDataSet.from_numpy({"M(D^{0})": D0_M_np_data, "cos#theta_{H}": D0_cosHel_0_np_data}, [x,y])

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
# r = extended_model.fitTo(data,NumCPU=12, Extended=ROOT.kTRUE)
r = extended_model.fitTo(data,NumCPU=12, Extended=ROOT.kTRUE,PrintLevel=-1, Save=1)

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
mcstudy.generateAndFit(1000)
 
# Explore results of study
# ------------------------------------------------
 
# Make plots of the distributions of mean, error on mean and the pull of
# mean
frame1 = mcstudy.plotParam(nsig, Bins=25)
frame2 = mcstudy.plotError(nsig, Bins=25)
frame3 = mcstudy.plotPull(nsig, Bins=25, FitGauss=False)
pullMean = ROOT.RooRealVar("pullMean","",0,-10,10)
pullSigma = ROOT.RooRealVar("pullSigma","",1,0.1,5)
pullMean.setPlotLabel("pull #mu")   # // optional (to get nicer plot labels if you want)
pullSigma.setPlotLabel("pull #sigma")

pullGauss = ROOT.RooGaussian("pullGauss", "", frame3.getPlotVar() , pullMean, pullSigma)
r_pull = pullGauss.fitTo(mcstudy.fitParDataSet(),NumCPU=12,PrintLevel=-1)
# Plot distribution of minimized likelihood
frame4 = mcstudy.plotNLL(Bins=25)
 
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
c = ROOT.TCanvas("rf801_mcstudy", "rf801_mcstudy", 2000, 500)
c.Divide(4, 1)
c.cd(1)
# ROOT.gPad.SetLeftMargin(0.15)
# frame3.GetYaxis().SetTitleOffset(1.4)
pullGauss.plotOn(frame3) ;
pullGauss.paramOn(frame3, ROOT.RooFit.Layout(0.55, 0.75, 0.9))

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
c.cd(4)
#ROOT.gPad.SetLeftMargin(0.15)
#frame4.GetYaxis().SetTitleOffset(1.4)
frame4.Draw("PE")
#c.cd(5)
#ROOT.gPad.SetLeftMargin(0.15)
# hh_cor_a0_s1f.GetYaxis().SetTitleOffset(1.4)
# hh_cor_a0_s1f.Draw("box")
#c.cd(6)
#ROOT.gPad.SetLeftMargin(0.15)
# hh_cor_a0_a1.GetYaxis().SetTitleOffset(1.4)
# hh_cor_a0_a1.Draw("box")
#c.cd(7)
#ROOT.gPad.SetLeftMargin(0.15)
#corrHist000.GetYaxis().SetTitleOffset(1.4)
#corrHist000.Draw("colz")
#c.cd(8)
#ROOT.gPad.SetLeftMargin(0.15)
#corrHist127.GetYaxis().SetTitleOffset(1.4)
#corrHist127.Draw("colz")
#c.cd(9)
#ROOT.gPad.SetLeftMargin(0.15)
#corrHist953.GetYaxis().SetTitleOffset(1.4)
#corrHist953.Draw("colz")
 
c.SaveAs("test_mcstudy.png")
 
# Make ROOT.RooMCStudy object available on command line after
# macro finishes
ROOT.gDirectory.Add(mcstudy)
