import ROOT
from ROOT import RooFit
import glob
import ctypes
import os

file_name = "/share/storage/jykim/plots/MC15ri/etapip/gg/generic/MC15ri_1ab_etapip_gg_fit_tight_v2_fitv10.png"
fitresult_name = "/share/storage/jykim/plots/MC15ri/etapip/gg/generic/fitresult/MC15ri_1ab_etapip_gg_fit_tight_v2_fitv10.root"
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

#loc_ccbar = base_file_loc + 'ccbar/tight_v2_240419_Kp_BCS_etapi0const_ccbar_output_02*.root'
loc_ccbar = base_file_loc + 'ccbar/*.root'
# loc_ccbar = base_file_loc + 'topo/resultfile/result_antiKstar/standard.root'
#loc_ccbar = base_file_loc + 'topo/resultfile/result_etapip_gg/standard.root'

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
cuts += " && " + charge_var + "==-1"

# Create RooRealVar
x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
x.setRange("fitRange", fit_range[0], fit_range[1])
#x.setBins(200)
chiProb_rank = ROOT.RooRealVar(rank_var, rank_var, 0, 30)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)


print(cuts)
before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,chiProb_rank,Pip_charge), cuts)


w_1 = ROOT.RooRealVar('w_1', 'w', 0,1)
w_1.setVal(1)
before_data.addColumn(w_1)
data = ROOT.RooDataSet(before_data.GetName(), before_data.GetTitle(),before_data, before_data.get(), '' ,  'w_1')
N_total = data.sumEntries()


# Open a ROOT TFile to save the data
output_file = ROOT.TFile("roodataset_MC15ri_etapip_gg_tight_v2_Dm.root", "RECREATE")

# Convert RooDataSet to TTree
#data_tree = data.tree()
#data_tree = data.convertToTreeStore()

# Write the TTree to the output file
data.Write()

# Close the output file
output_file.Close()

