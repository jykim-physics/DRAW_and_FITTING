import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory
from ROOT.RooFit import Extended, FitOptions, Save, PrintEvalErrors, PrintLevel, Bins, FitGauss,    NumCPU, Strategy, Offset
import glob
import ctypes
import os
import numpy as np

file_name_Dp = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/MC15rd_etapip_gg_K_fit_opt_loose_v7_fitv2_Dp.png"
file_name_Dm = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/MC15rd_etapip_gg_K_fit_opt_loose_v7_fitv2_Dm.png"
fitresult_name = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etapip_gg_K_fit_opt_loose_v7_fitv2.root"
fitresult_text = "/share/storage/jykim/plots/MC15rd/etaKp/gg/generic/fitresult/MC15rd_etapip_gg_K_fit_opt_loose_v7_fitv2.txt"
dir_path = os.path.dirname(file_name_Dp)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)
dir_path = os.path.dirname(fitresult_name)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
print("Directory created:", dir_path)

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

#file_list = ['/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15ri/etapip_eteeta/MC15ri_etaetapip_loose_v2_241106_yespi0veto/etapip_gg/MC15ri*.root']
base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/etapip_eteeta/MC15rd_etaetapip_loose_v7_241213_temp"
cm_elements = ["15rd_eta_e7_18_4S_v3", "15rd_eta_e20_b26_v1", "15rd_eta_e20_e26_4S_v2", "15rd_eta_e21_5S_scan_v1", "15rd_eta_mori_off_v1"]

tree_name = "etapip_gg_K"
file_list = []
for element in cm_elements:
    pattern = f"{base_path}/{element}/{tree_name}/*.BCS.root"
    file_list += glob.glob(pattern)

print(file_list)
mychain = ROOT.TChain(tree_name)
for i in file_list:
    mychain.Add(i)
print(file_list)

# Define variable and its range
fit_variable = "Dp_M"
fit_var_name = "M(D^{+}) [GeV/c^{2}]"
#fit_range = (1.66, 2.06)
#fit_range = (1.70, 2.06)
fit_range = (1.75, 2.045)
#fit_range = (1.78, 2.03)
truth_var = "Dp_isSignal"
charge_var = "Pip_charge"
Dp_CMS_cosTheta_var = "Dp_CMS_cosTheta"

cuts_Dp = charge_var + "==1 "
cuts_Dm = charge_var + "==-1 "
#cuts_Dp = charge_var + "==1 & Dp_CMS_cosTheta<0"
#cuts_Dm = charge_var + "==-1 & Dp_CMS_cosTheta<0"

x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
#x.setBins(200)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)
Dp_CMS_cosTheta = ROOT.RooRealVar(Dp_CMS_cosTheta_var, Dp_CMS_cosTheta_var, -1, 1)

before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,Pip_charge, Dp_CMS_cosTheta), cuts_Dp)

w_1 = ROOT.RooRealVar('w_1', 'w', 0,1)
#scale = 1
#scale = 427.87/1000
scale = 1/4
CMS_scale = 1
w_1.setVal(scale)
before_data.addColumn(w_1)
data = ROOT.RooDataSet(before_data.GetName(), before_data.GetTitle(),before_data, before_data.get(), '' ,  'w_1')
Num_total = data.sumEntries()
print(Num_total)

mychain_cc = ROOT.TChain(tree_name)
for i in file_list:
    mychain_cc.Add(i)
before_data_cc = ROOT.RooDataSet("data","", mychain_cc, ROOT.RooArgSet(x,Pip_charge, Dp_CMS_cosTheta), cuts_Dm)
before_data_cc.addColumn(w_1)
data_cc = ROOT.RooDataSet(before_data_cc.GetName(), before_data_cc.GetTitle(),before_data_cc, before_data_cc.get(), '' ,  'w_1')

#data.append(data_cc)
Num_total_cc = data_cc.sumEntries()
print(Num_total_cc)

N_total = RooRealVar("N_total", "N_total (N_D+ + N_D-)", 1800*scale*CMS_scale, 500*scale*CMS_scale, 4000*scale*CMS_scale)  # N_total = N_D+ + N_D-
Acp = RooRealVar("Acp", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

# Use Acp and N_total to define the expected signal yields for D+ and D-
Nsig_D_plus = RooFormulaVar("Nsig_D_plus",
    "0.5 * N_total * (1 + Acp)",
    RooArgList(N_total, Acp))

Nsig_D_minus = RooFormulaVar("Nsig_D_minus",
    "0.5 * N_total * (1 - Acp)",
    RooArgList(N_total, Acp))

N_total_Ds = RooRealVar("N_total_Ds", "N_total (N_Ds+ + N_Ds-)",  8000*scale*CMS_scale, 2000*scale*CMS_scale,16000*scale*CMS_scale)  # N_total = N_D+ + N_D-
Acp_Ds = RooRealVar("Acp_Ds", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

# Use Acp and N_total to define the expected signal yields for D+ and D-
Nsig_Ds_plus = RooFormulaVar("Nsig_Ds_plus",
    "0.5 * N_total_Ds * (1 + Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))

Nsig_Ds_minus = RooFormulaVar("Nsig_Ds_minus",
    "0.5 * N_total_Ds * (1 - Acp_Ds)",
    RooArgList(N_total_Ds, Acp_Ds))

#Nbkg_D_plus = ROOT.RooRealVar("Nbkg_D_plus", "Number of background events for D+", 10000*scale, 8000*scale, 16000*scale)
#Nbkg_D_minus = ROOT.RooRealVar("Nbkg_D_minus", "Number of background events for D-", 10000*scale, 8000*scale, 16000*scale)
Nbkg_total = ROOT.RooRealVar("Nbkg_total", "Number of background events for D+", 20000*scale*CMS_scale, 10000*scale*CMS_scale,36000*scale*CMS_scale)
Acp_bkg = RooRealVar("Acp_bkg", "Acp", 0, -1, 1)  # A_Cp as a fit parameter
Nbkg_D_plus = RooFormulaVar("Nbkg_D_plus",
    "0.5 * Nbkg_total * (1 + Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))

Nbkg_D_minus = RooFormulaVar("Nbkg_D_minus",
    "0.5 * Nbkg_total * (1 - Acp_bkg)",
    RooArgList(Nbkg_total, Acp_bkg))

mean = ROOT.RooRealVar("mean", "mean", 1.869553651, 1.85, 1.89)
#sigma = ROOT.RooRealVar("sigma", "sigma",  0.00335350988)
sigmaL = ROOT.RooRealVar("sigmaL", "sigma",  0.00010000161832845217)
sigmaR = ROOT.RooRealVar("sigmaR", "sigma",  0.00014146387437137935)
alphaL = ROOT.RooRealVar("alphaL", "alphaL", 0.02457393270005916)
nL = ROOT.RooRealVar("nL", "nL", 4.48823490355655)
alphaR = ROOT.RooRealVar("alphaR", "alphaR", 0.07644301960947571)
nR = ROOT.RooRealVar("nR", "nR", 2.886536618282026)

# Create double-sided Crystal Ball PDF
#CB = ROOT.RooCrystalBall("CB", "CB_left", x, mean, sigma, alphaL, nL, alphaR, nR)
CB = ROOT.RooCrystalBall("CB", "CB_left", x, mean, sigmaL, sigmaR, alphaL, nL, alphaR, nR)

#mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0, -0.1, 0.1)
mean_gaussian = ROOT.RooRealVar("mean_gaussian", "mean of Gaussian", 0)
#sigma_gaussian = ROOT.RooRealVar("sigma_gaussian", "sigma of Gaussian", 0.001, 0.00001, 0.1)
sigma_gaussian = ROOT.RooRealVar("sigma_gaussian", "sigma of Gaussian", 0.007694428298890234)
gaussian = ROOT.RooGaussian("gaussian", "Gaussian PDF", x, mean_gaussian, sigma_gaussian)

# Convolute the Johnson distribution with Gaussian
sig_model = ROOT.RooFFTConvPdf("sig_model", "Convolution of Johnson and Gaussian", x, CB, gaussian)

Ds_mean = ROOT.RooRealVar("Ds_mean", "mean", 1.968164749, 1.94, 1.98)
#Ds_sigma = ROOT.RooRealVar("Ds_sigma", "sigma", 0.00421516866)
Ds_sigmaL = ROOT.RooRealVar("Ds_sigmaL", "sigma",  0.001989936730176138 )
Ds_sigmaR = ROOT.RooRealVar("Ds_sigmaR", "sigma", 0.0041510952277050255)
Ds_alphaL = ROOT.RooRealVar("Ds_alphaL", "alphaL", 0.44996565266032984)
Ds_nL = ROOT.RooRealVar("Ds_nL", "nL",  3.9252587704791613 )
Ds_alphaR = ROOT.RooRealVar("Ds_alphaR", "alphaR", 1.5529998271778207)
Ds_nR = ROOT.RooRealVar("Ds_nR", "nR", 2.379836901252171)

# Create double-sided Crystal Ball PDF
#Ds_CB = ROOT.RooCrystalBall("Ds_CB", "CB_left", x, Ds_mean, Ds_sigma, Ds_alphaL, Ds_nL, Ds_alphaR, Ds_nR)
Ds_CB = ROOT.RooCrystalBall("Ds_CB", "CB_left", x, Ds_mean, Ds_sigmaL, Ds_sigmaR, Ds_alphaL, Ds_nL, Ds_alphaR, Ds_nR)

#Ds_mean_gaussian = ROOT.RooRealVar("Ds_mean_gaussian", "mean of Gaussian", 0, -0.1, 0.1)
Ds_mean_gaussian = ROOT.RooRealVar("Ds_mean_gaussian", "mean of Gaussian", 0)
#Ds_sigma_gaussian = ROOT.RooRealVar("Ds_sigma_gaussian", "sigma of Gaussian", 0.001, 0.00001, 0.1)
Ds_sigma_gaussian = ROOT.RooRealVar("Ds_sigma_gaussian", "sigma of Gaussian",  0.008233169478590395)

# Create a Gaussian distribution
Ds_gaussian = ROOT.RooGaussian("Ds_gaussian", "Gaussian PDF", x, Ds_mean_gaussian, Ds_sigma_gaussian)

# Convolute the Johnson distribution with Gaussian
Ds_model = ROOT.RooFFTConvPdf("Ds_model", "Convolution of Johnson and Gaussian", x, Ds_CB, Ds_gaussian)

x_bkg1_Cheby_c0 = ROOT.RooRealVar("x_bkg1_Cheby_c0", "c0",0.1, -1.0, 1.0)
x_bkg1_Cheby_c1 = ROOT.RooRealVar("x_bkg1_Cheby_c1", "c0",0.2, -1.0, 1.0)
x_bkg1_Cheby_c2 = ROOT.RooRealVar("x_bkg1_Cheby_c2", "c0",0.3, -1.0, 1.0)
x_bkg1_tau = ROOT.RooRealVar("x_bkg1_tau", "c0",-5, -20, 5)

#novo_mean_gaussian = ROOT.RooRealVar("novo_mean_gaussian", "mean of Gaussian", 0, -0.5, 0.5)
#novo_sigma_gaussian = ROOT.RooRealVar("novo_sigma_gaussian", "sigma of Gaussian", 0.01, 0.000001, 0.1)
#novo_gaussian = ROOT.RooGaussian("novo_gaussian", "Gaussian PDF", x, novo_mean_gaussian, novo_sigma_gaussian)
#rhopeta = ROOT.RooFFTConvPdf("rhopeta", "Convolution of Novosibirsk and Gaussian", x, novo, novo_gaussian)

#bkg_comb = ROOT.RooExponential("bkg_comb", "x_bkg1", x, x_bkg1_tau)
#model_bkg = ROOT.RooPolynomial("model_bkg", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1, x_bkg1_Cheby_c2))
#model_bkg = ROOT.RooPolynomial("model_bkg", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0, x_bkg1_Cheby_c1))
#model_bkg = ROOT.RooPolynomial("model_bkg", "x_bkg1", x, ROOT.RooArgList(x_bkg1_Cheby_c0))

#bkg_frac = ROOT.RooRealVar("bkg_frac", "fraction of Gaussian in BKG", 0.25, 0.1, 1)

#model_bkg = ROOT.RooAddPdf("model_bkg", "Gaus + Exp", RooArgList(rhopeta, bkg_comb), bkg_frac)


model_bkg = ROOT.RooExponential("model_bkg", "x_bkg1", x, x_bkg1_tau)


# Define extended PDFs for D+ and D-
model_D_plus = ROOT.RooAddPdf("model_D_plus", "D+ model",
                              ROOT.RooArgList(sig_model, Ds_model, model_bkg),
                              ROOT.RooArgList(Nsig_D_plus, Nsig_Ds_plus, Nbkg_D_plus))
model_D_minus = ROOT.RooAddPdf("model_D_minus", "D- model",
                              ROOT.RooArgList(sig_model, Ds_model, model_bkg),
                              ROOT.RooArgList(Nsig_D_minus, Nsig_Ds_minus, Nbkg_D_minus))

# Create a category to distinguish between D+ and D-
cat = RooCategory("sample", "sample")
cat.defineType("D_plus")
cat.defineType("D_minus")

# Create a simultaneous PDF using the category
sim_model = RooSimultaneous("sim_model", "Simultaneous model", cat)
sim_model.addPdf(model_D_plus, "D_plus")
sim_model.addPdf(model_D_minus, "D_minus")

data_combined = RooDataSet("data_combined", "Combined data", RooArgList(x, w_1), RooFit.Index(cat),
                           RooFit.Import("D_plus", data),
                           RooFit.Import("D_minus", data_cc),
                           RooFit.WeightVar('w_1'))

# Fit the model to the combined data
#fit_result = sim_model.fitTo(data_combined, RooFit.Save())
#fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4), RooFit.Strategy(2), RooFit.Minos(0), RooFit.Hesse(1))
#fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(4), RooFit.Strategy(0), RooFit.Minos(0), RooFit.Hesse(1))
nll = sim_model.createNLL(data_combined, ROOT.RooFit.Extended(True), ROOT.RooFit.NumCPU(15), RooFit.SumW2Error(True),  ROOT.RooFit.Offset(True))

# Step 2: Perform the Migrad minimization
minimizer = ROOT.RooMinimizer(nll)
minimizer.setStrategy(2)
#minimizer.setStrategy(0)
#minimizer.setPrintLevel(3)
minimizer.setPrintLevel(0)
status = minimizer.migrad()

# Check the status of Migrad
if status != 0:
    print(f"Migrad failed with status: {status}")

# Step 3: Perform the Hesse minimization
status = minimizer.hesse()

# Check the status of Hesse
if status != 0:
    print(f"Hesse failed with status: {status}")

# Save the fit result
fit_result  = minimizer.save()
#r.Print("v")

# Print fit results
fit_result.Print()

# Output the Acp value and its error
Acp_value = Acp.getVal()
Acp_error = Acp.getError()

print(f"Acp = {Acp_value:.3f} ± {Acp_error:.3f}")

# Output N_total
N_total_value = N_total.getVal()
N_total_error = N_total.getError()
N_total_value_Ds = N_total_Ds.getVal()
N_total_error_Ds = N_total_Ds.getError()

print(f"N_total = {N_total_value:.0f} ± {N_total_error:.3f}")


# The file is automatically closed after the 'with' block


# mcstudy1 = ROOT.RooMCStudy(sim_model, ROOT.RooArgSet(x), ROOT.RooFit.Extended(True),
#                             ROOT.RooFit.Binned(False), ROOT.RooFit.Silence(),
#                             ROOT.RooFit.FitOptions(ROOT.RooFit.Save(True),
#                                                    ROOT.RooFit.PrintEvalErrors(0),
#                                                    ROOT.RooFit.PrintLevel(-1)))

# # Generate and fit 10 toys
# mcstudy1.generateAndFit(10)

def Linearity_test(sim_model, cat, N_Input=100, N_gen=500, N_total=N_total):
  N_total_Ds.setVal(N_Input)
  ToyMC_all = ROOT.RooMCStudy(sim_model, {x,cat}, Extended(True), FitOptions(Save(True),PrintEvalErrors(0),PrintLevel(0), NumCPU(6), Offset(True)))
  ToyMC_all.generateAndFit(N_gen)

  toyMC_frame_N_total_pull = ToyMC_all.plotPull(N_total_Ds, Bins(20))
  pullMean = ROOT.RooRealVar("pullMean","",0,-10,10)
  pullSigma = ROOT.RooRealVar("pullSigma","",1,0.1,5)
  pullMean.setPlotLabel("#mu")
  pullSigma.setPlotLabel("#sigma")

  pullGauss = ROOT.RooGaussian("pullGauss", "", toyMC_frame_N_total_pull.getPlotVar() , pullMean, pullSigma)
  r_pull = pullGauss.fitTo(ToyMC_all.fitParDataSet(),NumCPU=6,PrintLevel=-1)

  pullGauss.plotOn(toyMC_frame_N_total_pull)
  pullGauss.paramOn(toyMC_frame_N_total_pull, ROOT.RooFit.Layout(0.60, 0.80, 0.9), ROOT.RooFit.Format("NE",ROOT.RooFit.AutoPrecision(1)))
  toyMC_canvas = ROOT.TCanvas("toyMC_canvas", "D+ fit", 1600, 600)
  toyMC_canvas.Divide(2,1)
  toyMC_canvas.cd(1)
  toyMC_frame_N_total_pull.Draw("PE")

  toyMC_frame_N_total = ToyMC_all.plotParam(N_total_Ds, Bins(20))
  Mean = ROOT.RooRealVar("Mean","",N_Input, 0.5*N_Input, 1.5*N_Input)
  Sigma = ROOT.RooRealVar("Sigma","",N_Input**0.5, N_Input**0.5/4, N_Input*0.8)
  Mean.setPlotLabel("#mu")
  Sigma.setPlotLabel("#sigma")

  Gauss = ROOT.RooGaussian("Gauss", "", toyMC_frame_N_total.getPlotVar() , Mean, Sigma)
  r_N_total_pull = Gauss.fitTo(ToyMC_all.fitParDataSet(),NumCPU=6,PrintLevel=-1)

  Gauss.plotOn(toyMC_frame_N_total)
  Gauss.paramOn(toyMC_frame_N_total, ROOT.RooFit.Layout(0.60, 0.80, 0.9), ROOT.RooFit.Format("NE",ROOT.RooFit.AutoPrecision(1)))
  toyMC_canvas.cd(2)
  toyMC_frame_N_total.Draw("PE")
  toyMC_canvas.SaveAs(f"toy_Acp_{tree_name}_{N_Input}.Ds.png")

  Nsig_mean = Mean.getVal()
  Nsig_mean_error = Mean.getError()

  return Nsig_mean, Nsig_mean_error


expected_values = np.linspace(N_total_value_Ds-N_total_error_Ds*3, N_total_value_Ds+N_total_error_Ds*3, 27)
N_input = list()
N_predict = list()
Fit_error = list()
for i in expected_values:
    N_input.append(i)

    N_fit, temp_fit_error = Linearity_test(sim_model, cat, N_Input=i,N_gen=1000)
    N_predict.append(N_fit)
    Fit_error.append(temp_fit_error)

    print(f'Prediction: {N_fit}, Input: {i}, Error: {temp_fit_error}')


import matplotlib.pyplot as plt
# everything in iminuit is done through the Minuit object, so we import it
from iminuit import Minuit

# we also need a cost function to fit and import the LeastSquares function
from iminuit.cost import LeastSquares

# display iminuit version
import iminuit
print("iminuit version:", iminuit.__version__)

# our line model, unicode parameter names are supported :)
def line(x, c0, c1):
    return c0 + x * c1

least_squares = LeastSquares(N_input, N_predict, Fit_error, line)

m = Minuit(least_squares, c0=0, c1=0)  # starting values for α and β

m.migrad()  # finds minimum of least_squares function
m.hesse()


# # plt.scatter(N_input, N_predict)



plt.errorbar(N_input, N_predict, yerr=Fit_error, fmt="o",label='Data')

# N_input = np.array(N_input)
N_start = N_input[0]
N_end = N_input[-1]
np_N_input = np.linspace(N_start*0.97,N_end*1.03,101)

plt.plot(np_N_input, line(np_N_input, *m.values), label=r"Fit($y=c_0+c_1x$)")
# plt.plot([N_start*0.9,N_end*1.05], line([N_start*0.9,N_end*1.05], *m.values), label=r"Fit($y=c_0+c_1x$)")




# plt.xlim(N_start*0.9,N_end*1.05)
# plt.ylim(N_start*0.9,N_end*1.05)
plt.plot([N_start*0.97,N_end*1.03], [N_start*0.97,N_end*1.03], label='y=x')

# plt.plot([N_start,N_end], [N_start,N_end], label='y=x')


# plt.legend()
# plt.show()


# display legend with some fit info
fit_info = [
    f"$\\chi^2$/$n_\\mathrm{{dof}}$ = {m.fval:.1f} / {m.ndof:.0f} = {m.fmin.reduced_chi2:.1f}",
]
for p, v, e in zip(m.parameters, m.values, m.errors):
    if p=='c0':
        p = r'$c_0$'
    elif p=='c1':
        p = r'$c_1$'
    fit_info.append(f"{p} = ${v:.3f} \\pm {e:.3f}$")

plt.legend(title="\n".join(fit_info), frameon=False, fontsize=13)

plt.xlabel("Input")
plt.ylabel("Prediction")
plt.xlim(N_start*0.97,N_end*1.03)
plt.ylim(N_start*0.97,N_end*1.03)
# plt.xlim(N_start,N_end)
# plt.ylim(N_start,N_end)
plt.tight_layout()
plt.savefig(f"Linearity_{tree_name}_fit_Ds.png")
plt.show();
