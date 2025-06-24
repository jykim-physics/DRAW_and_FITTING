import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory
from ROOT.RooFit import Extended, FitOptions, Save, PrintEvalErrors, PrintLevel, Bins, FitGauss,    NumCPU, Strategy, Offset
import glob
import ctypes
import os
import argparse

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC16rd/MC16rd_pre_test_250609_v2_vg_nodelM"
cm_elements = ["16rd_vg_proc_4S_Budstau", "16rd_vg_proc_4S_ccbar"]
BDT_cut = 0.65
tree_name = "antiKstar"
file_list = []
for element in cm_elements:
    #pattern = f"{base_path}/{element}/{tree_name}/{args.train}/skimhad/*.BCS.root"
    #pattern = f"{base_path}/{element}/{tree_name}/train_Dp_dz/skimhad/*.BCS.root"
    #pattern = f"{base_path}/{element}/{tree_name}/train_Dp_dz/skimhad/new_FOM/*.BCS.root"
    pattern = f"{base_path}/{element}/{tree_name}/bdt_test_v0/{BDT_cut}/*.BCS.root"
    file_list += glob.glob(pattern)
mychain = ROOT.TChain(tree_name)
for i in file_list:
    mychain.Add(i)
print(file_list)
print(f"Numer of files: {len(file_list)}")

# Define variable and its range
fit_variable = "D0_M"
fit_var_name = "M(#bar{K}^{0}#gamma) [GeV/c^{2}]"
fit_range = (1.68, 2.05)

charge_var = "Pis_charge"
cuts = "D0_M>0"

x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
# x.setBins(200)
Pis_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)


full_var_set = ROOT.RooArgSet(x, Pis_charge)

#before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,Pip_charge,Dp_CMS_cosTheta), cuts_Dp)
before_data = ROOT.RooDataSet("data", "", mychain, full_var_set, cuts)

w_1 = ROOT.RooRealVar('w_1', 'w', 0,1)
#scale = 427.87/1000
#scale = 1/4
scale = 1
#scale = (1/4)*(427.87+54.3)/427.87
w_1.setVal(scale)
before_data.addColumn(w_1)
data = ROOT.RooDataSet(before_data.GetName(), before_data.GetTitle(),before_data, before_data.get(), '' ,  'w_1')

data.Print("v")
