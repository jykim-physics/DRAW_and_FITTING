import ROOT
from ROOT import RooFit
import glob
import ctypes
import os
import math
import numpy as np 
from ROOT import RooFit, RooRealVar, RooGaussian, RooDataSet, RooArgSet, RooAddPdf, RooRandom, RooArgList, RooDataHist, RooHistPdf, RooPolynomial

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

ROOT.gROOT.LoadMacro('/home/jykim/workspace/git/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

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

# True+false fixed
#mean_johnson = ROOT.RooRealVar("mean_johnson", "mean of Johnson", 1.88082)
#sigma_johnson = ROOT.RooRealVar("sigma_johnson", "sigma of Johnson", 0.00197121 )
#gamma = ROOT.RooRealVar("gamma", "gamma of Johnson", 0.309290 )
#delta = ROOT.RooRealVar("delta", "delta of Johnson", 0.499782 )

# MC matched fixed
mean_johnson = ROOT.RooRealVar("mean_johnson", "mean of Johnson", 1.88371)
sigma_johnson = ROOT.RooRealVar("sigma_johnson", "sigma of Johnson", 0.0060692)
gamma = ROOT.RooRealVar("gamma", "gamma of Johnson", 0.339939)
delta = ROOT.RooRealVar("delta", "delta of Johnson", 0.890541 )


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

# ALL fixed
Ds_mean_johnson = ROOT.RooRealVar("Ds_mean_johnson", "mean of Johnson", 1.99327)
Ds_sigma_johnson = ROOT.RooRealVar("Ds_sigma_johnson", "sigma of Johnson", 0.00116443 )
Ds_gamma = ROOT.RooRealVar("Ds_gamma", "gamma of Johnson", 0.340494 )
Ds_delta = ROOT.RooRealVar("Ds_delta", "delta of Johnson", 0.404213 )

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
r = extended_model.fitTo(data,  RooFit.Extended(True), RooFit.PrintLevel(3), RooFit.Save(1),RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4))
#D-####################################################
mychain_cc = ROOT.TChain(tree_name)

for i in file_list:
    mychain_cc.Add(i)

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
cuts += " && " + charge_var + "==-1"

# Create RooRealVar
y = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
y.setBins(70)
chiProb_rank_cc = ROOT.RooRealVar(rank_var, rank_var, 0, 30)
Pip_charge_cc = ROOT.RooRealVar(charge_var, charge_var, -1, 1)


print(cuts)
before_data_cc = ROOT.RooDataSet("data","", mychain_cc, ROOT.RooArgSet(y,chiProb_rank_cc,Pip_charge_cc), cuts)


w_1_cc = ROOT.RooRealVar('w_1', 'w', 0,1)
w_1_cc.setVal(1)
before_data_cc.addColumn(w_1_cc)
data_cc = ROOT.RooDataSet(before_data_cc.GetName(), before_data_cc.GetTitle(),before_data_cc, before_data_cc.get(), '' ,  'w_1')
N_total = data_cc.sumEntries()
print(N_total)

#mean_johnson = ROOT.RooRealVar("mean_johnson", "mean of Johnson", 1.86, 1.8, 1.9)
#sigma_johnson = ROOT.RooRealVar("sigma_johnson", "sigma of Johnson", 0.01, 0.00001, 0.5)
#gamma = ROOT.RooRealVar("gamma", "gamma of Johnson", 0.1, 0.001, 1)
#delta = ROOT.RooRealVar("delta", "delta of Johnson", 0.1, 0.001, 1)

# True+false fixed
#mean_johnson = ROOT.RooRealVar("mean_johnson", "mean of Johnson", 1.88082)
#sigma_johnson = ROOT.RooRealVar("sigma_johnson", "sigma of Johnson", 0.00197121 )
#gamma = ROOT.RooRealVar("gamma", "gamma of Johnson", 0.309290 )
#delta = ROOT.RooRealVar("delta", "delta of Johnson", 0.499782 )

# MC matched fixed
mean_johnson_cc = ROOT.RooRealVar("mean_johnson_cc", "mean of Johnson", 1.88371)
sigma_johnson_cc = ROOT.RooRealVar("sigma_johnson_cc", "sigma of Johnson", 0.0060692)
gamma_cc = ROOT.RooRealVar("gamma_cc", "gamma of Johnson", 0.339939)
delta_cc = ROOT.RooRealVar("delta_cc", "delta of Johnson", 0.890541 )

mean_gaussian_cc = ROOT.RooRealVar("mean_gaussian_cc", "mean of Gaussian", 0, -1, 1)
sigma_gaussian_cc = ROOT.RooRealVar("sigma_gaussian_cc", "sigma of Gaussian", 0.01, 0.00001, 1)

# Create a Johnson distribution
johnson_cc = ROOT.RooJohnson("johnson_cc", "Johnson PDF", y, mean_johnson_cc, sigma_johnson_cc, gamma_cc, delta_cc)

# Create a Gaussian distribution
gaussian_cc = ROOT.RooGaussian("gaussian_cc", "Gaussian PDF", y, mean_gaussian_cc, sigma_gaussian_cc)

# Convolute the Johnson distribution with Gaussian
sig_model_cc = ROOT.RooFFTConvPdf("sig_model_cc", "Convolution of Johnson and Gaussian", y, johnson_cc, gaussian_cc)

#CB = ROOT.RooCrystalBall("CB", "CB", x, mean, sigma, alphaL, nL)


# sigma_gauss = ROOT.RooRealVar("sigma_gauss", "sigma", 0.02, 0.001, 0.1)
# gauss = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma_gauss)

# sig_fraction = ROOT.RooRealVar("sig_fraction", "fraction", 0.5, 0.0, 1.0)
# sig_model = ROOT.RooAddPdf("sig_model", "sig_model", ROOT.RooArgList(CB, gauss),ROOT.RooArgList(sig_fraction))


#Ds_mean_johnson = ROOT.RooRealVar("Ds_mean_johnson", "mean of Johnson", 1.96, 1.91, 1.98)
#Ds_sigma_johnson = ROOT.RooRealVar("Ds_sigma_johnson", "sigma of Johnson", 0.01, 0.00001, 0.5)
#Ds_gamma = ROOT.RooRealVar("Ds_gamma", "gamma of Johnson", 0.1, 0.001, 1)
#Ds_delta = ROOT.RooRealVar("Ds_delta", "delta of Johnson", 0.1, 0.001, 1)

# ALL fixed
Ds_mean_johnson_cc = ROOT.RooRealVar("Ds_mean_johnson_cc", "mean of Johnson", 1.99327)
Ds_sigma_johnson_cc = ROOT.RooRealVar("Ds_sigma_johnson_cc", "sigma of Johnson", 0.00116443 )
Ds_gamma_cc = ROOT.RooRealVar("Ds_gamma_cc", "gamma of Johnson", 0.340494 )
Ds_delta_cc = ROOT.RooRealVar("Ds_delta_cc", "delta of Johnson", 0.404213 )

Ds_mean_gaussian_cc = ROOT.RooRealVar("Ds_mean_gaussian_cc", "mean of Gaussian", 0, -1, 1)
Ds_sigma_gaussian_cc = ROOT.RooRealVar("Ds_sigma_gaussian_cc", "sigma of Gaussian", 0.01, 0.00001, 1)

# Create a Johnson distribution
Ds_johnson_cc = ROOT.RooJohnson("Ds_johnson_cc", "Johnson PDF", y, Ds_mean_johnson_cc, Ds_sigma_johnson_cc, Ds_gamma_cc, Ds_delta_cc)

# Create a Gaussian distribution
Ds_gaussian_cc = ROOT.RooGaussian("Ds_gaussian_cc", "Gaussian PDF", y, Ds_mean_gaussian_cc, Ds_sigma_gaussian_cc)

# Convolute the Johnson distribution with Gaussian
Ds_model_cc = ROOT.RooFFTConvPdf("Ds_model_cc", "Convolution of Johnson and Gaussian", x, Ds_johnson_cc, Ds_gaussian_cc)

rhopeta_mean_cc = ROOT.RooRealVar("rhopeta_mean", "mean", 1.75, 1.65, 1.8)
rhopeta_sigma_cc = ROOT.RooRealVar("rhopeta_sigma", "sigma", 0.03, 0.001, 0.05)
rhopeta_model_cc = ROOT.RooGaussian("rhopeta_model", "gauss", y, rhopeta_mean_cc, rhopeta_sigma_cc)

x_bkg1_Cheby_c0_cc = ROOT.RooRealVar("x_bkg1_Cheby_c0", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c1_cc = ROOT.RooRealVar("x_bkg1_Cheby_c1", "c0",0.0, -1.0, 1.0)
x_bkg1_Cheby_c2_cc = ROOT.RooRealVar("x_bkg1_Cheby_c2", "c0",0.0, -1.0, 1.0)
x_bkg1_tau_cc = ROOT.RooRealVar("x_bkg1_tau", "c0",-0.5, -20, 0)

#bkg_model = ROOT.RooPolynomial("bkg_model", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1))
bkg_model_cc = ROOT.RooExponential("bkg_model_cc", "x_bkg1", y, x_bkg1_tau_cc)


nsig_cc = ROOT.RooRealVar("nsig","# signal events",N_total*0.01,0,N_total*0.8)
nbkg1_cc = ROOT.RooRealVar("nbkg1","# bkg events",N_total*0.8,0, N_total)
nbkg2_cc = ROOT.RooRealVar("nbkg2","# bkg events",N_total*0.2,0, N_total)
nDs_cc = ROOT.RooRealVar("nDs","# bkg events",N_total*0.8,0, N_total)

extended_model_cc = ROOT.RooAddPdf("extended_model", "x_model", ROOT.RooArgSet(sig_model_cc,bkg_model_cc, Ds_model_cc, rhopeta_model_cc), ROOT.RooArgSet(nsig_cc, nbkg1_cc, nDs_cc, nbkg2_cc))

#r = extended_model.fitTo(data,NumCPU=4, Extended=ROOT.kTRUE,PrintLevel=-1, Save=1,SumW2Error=True)
r_cc = extended_model_cc.fitTo(data_cc,  RooFit.Extended(True), RooFit.PrintLevel(3), RooFit.Save(1),RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4))

###################################################
#r = extended_model.fitTo(data, ROOT.RooFit.PrintLevel(-1), Save=1,SumW2Error=True)

# Parameters for the simulation
n_iterations = 10000
N_total_input_Dp = nsig.getVal() + nbkg1.getVal() +  nbkg2.getVal() + nDs.getVal()
N_total_input_Dm = nsig_cc.getVal() + nbkg1_cc.getVal() +  nbkg2_cc.getVal() + nDs_cc.getVal()

# Arrays to store the results
n_gen_Dp = []
n_gen_Dm = []
nsig_Dp_values = []
nsig_Dp_errors = []
nsig_Dm_values = []
nsig_Dm_errors = []

n_gen_Acp = []
n_recon_Acp = []
n_recon_err_Acp = []

def Acp_error_cal(Nsig, Nsig_cc, Nsig_err, Nsig_cc_err):
    Z = (Nsig - Nsig_cc)/(Nsig + Nsig_cc)
    dsig = Z * (2*Nsig_cc/ (Nsig**2 - Nsig_cc*2) ) * Nsig_err
    dsig_cc = Z * (2*Nsig/ (Nsig**2 - Nsig_cc*2) ) * Nsig_cc_err
    
    dZ_square = dsig**2 + dsig_cc**2
    return math.sqrt(dZ_square)

# Perform multiple fits
for i in range(n_iterations):
    print("for loop:" + i)
    # Generate the number of signal and background events based on the fixed total number of events
    #poisson_nsig = int(N_total * frac_sig)
    #poisson_nbkg = N_total - poisson_nsig
    n_gen_Dp.append(nsig.getVal())
    n_gen_Dm.append(nsig_cc.getVal())

    n_gen_Acp.append( (nsig.getVal()-nsig_cc.getVal())/(nsig.getVal()+nsig_cc.getVal()) )
    
    N_total_Dp = RooRandom.randomGenerator().Poisson(N_total_input_Dp)
    N_total_Dm = RooRandom.randomGenerator().Poisson(N_total_input_Dm)

    # Generate a dataset from the extended model
    data_Dp = extended_model.generate(RooArgSet(x), N_total_Dp)  # Generate data with the fixed total number of events
    data_Dm = extended_model_cc.generate(RooArgSet(y), N_total_Dm)  # Generate data with the fixed total number of events

    # Fit the extended PDF to the dataset
    result_Dp = extended_model.fitTo(data_Dp, RooFit.Extended(True), RooFit.Save(), RooFit.PrintLevel(-1), ROOT.RooFit.NumCPU(4))
    result_Dm = extended_model_cc.fitTo(data_Dm, RooFit.Extended(True), RooFit.Save(), RooFit.PrintLevel(-1) , ROOT.RooFit.NumCPU(4))

    # Save the fitted number of signal and background events and their errors
    nsig_Dp_values.append(nsig.getVal())
    nsig_Dp_errors.append(nsig.getError())
    nsig_Dm_values.append(nsig_cc.getVal())
    nsig_Dm_errors.append(nsig_cc.getError())
    n_recon_Acp.append( (nsig.getVal()-nsig_cc.getVal())/(nsig.getVal()+nsig_cc.getVal()) )
    n_recon_err_Acp.append( Acp_error_cal(nsig.getVal(), nsig_cc.getVal(), nsig.getError(), nsig_cc.getError()) )

# Calculate the pull distribution for signal and background
# pulls_Acp = [(val - Ngen) / err for Ngen, val, err in zip(n_gen_Acp, n_recon_Acp, n_recon_Acp_errors)]
pulls_Acp = [(val - Ngen) / err for Ngen, val, err in zip(n_gen_Acp, n_recon_Acp, n_recon_err_Acp)]

# Convert to numpy arrays for convenience
pulls_Acp = np.array(pulls_Acp)

# Plot the pull distribution for signal
c_sig = ROOT.TCanvas("c_sig", "c_sig", 800, 600)
pull_hist_sig = ROOT.TH1F("pull_hist_sig", "Signal Pull Distribution", 100, -10,10)

for pull in pulls_sig:
    pull_hist_sig.Fill(pull)

pull_hist_sig.Draw()
pull_hist_sig.GetXaxis().SetTitle("Pull (Signal)")
pull_hist_sig.GetYaxis().SetTitle("Entries")

# Define the observable for the pull distribution
pull_sig = RooRealVar("pull_sig", "pull_sig", -5, 5)

# Define the parameters for the Gaussian fit
pull_mean_sig = RooRealVar("pull_mean_sig", "mean of signal pull distribution", 0, -5, 5)
pull_sigma_sig = RooRealVar("pull_sigma_sig", "width of signal pull distribution", 1, 0.1, 5)

# Define the Gaussian PDF for the signal pull distribution
pull_gauss_sig = RooGaussian("pull_gauss_sig", "Gaussian PDF for signal pull", pull_sig, pull_mean_sig, pull_sigma_sig)

# Create a RooDataHist from the signal pull histogram
pull_data_hist_sig = RooDataHist("pull_data_hist_sig", "Signal Pull Data Hist", RooArgList(pull_sig), pull_hist_sig)

# Fit the Gaussian PDF to the RooDataHist
pull_gauss_sig.fitTo(pull_data_hist_sig, RooFit.Save())

# Plot the fit result for signal pull distribution
pull_frame_sig = pull_sig.frame()
pull_data_hist_sig.plotOn(pull_frame_sig)
pull_gauss_sig.plotOn(pull_frame_sig)

# Draw the fit result for signal pull distribution
pull_frame_sig.Draw()
c_sig.SaveAs("Acp_pull_distribution_10000_all_numcpu4.png")

# Print the mean and sigma of the signal pull distribution
mean_pull_sig = pull_mean_sig.getVal()
sigma_pull_sig = pull_sigma_sig.getVal()
print(f"Acp pull distribution mean: {mean_pull_sig:.3f}")
print(f"Acp pull distribution sigma: {sigma_pull_sig:.3f}")
