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

base_file_loc =  './'

#loc_ccbar = base_file_loc + 'ccbar/tight_v2_240419_Kp_BCS_etapi0const_ccbar_output_02*.root'
loc_ccbar = base_file_loc + 'output_file.root'
# loc_ccbar = base_file_loc + 'topo/resultfile/result_antiKstar/standard.root'
loc_ccbar = base_file_loc + 'topo/resultfile/result_etapip_gg/standard.root'

loc_uubar = base_file_loc + 'uubar/*.root'
loc_ddbar = base_file_loc + 'ddbar/*.root'
loc_ssbar = base_file_loc + 'ssbar/*.root'
loc_charged = base_file_loc + 'charged/*.root'
loc_mixed = base_file_loc + 'mixed/*.root'
loc_taupair = base_file_loc + 'taupair/*.root'

file_list = [loc_ccbar,loc_uubar,loc_uubar,loc_ssbar,loc_charged,loc_mixed,loc_taupair]
#file_list = [loc_ccbar,loc_charged,loc_mixed]
file_list = [loc_ccbar]

input_file = ROOT.TFile.Open("output_file.root")
data = ROOT.gDirectory.Get("data")

#data
data.Print("v")


