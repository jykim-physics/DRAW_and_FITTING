import ROOT
#import pandas as pd

root_file = ROOT.TFile("output_file_gg.root", "READ")
data_combined = root_file.Get("sweight")
data_combined.Print()

MC_root_file = ROOT.TFile("output_file_gg_MC15rd.root", "READ")
MC_combined =  MC_root_file.Get("sweight")
MC_combined.Print()
