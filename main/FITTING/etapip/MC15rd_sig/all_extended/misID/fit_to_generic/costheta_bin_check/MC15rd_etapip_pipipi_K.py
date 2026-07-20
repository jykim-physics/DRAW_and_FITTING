import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooGaussian, RooFormulaVar, RooSimultaneous, RooCategory, RooStats, TFile
from ROOT.RooFit import Extended, FitOptions, Save, PrintEvalErrors, PrintLevel, Bins, FitGauss,    NumCPU, Strategy, Offset
import glob
import ctypes
import os
import argparse

parser = argparse.ArgumentParser(description="Process Dp_CMS_sign argument")
parser.add_argument("-t","--train", required=True,
                    help="Specify train version")
parser.add_argument("-b","--bdt", required=True,
                    help="Specify BDT value")
parser.add_argument("-B","--bin", required=True,
                    help="Specify Bin")
args = parser.parse_args()


BDT_cut = str(args.bdt)
#BDT_cut = 0.91

N_scale = 1/6
if args.bin == 'a':
  Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta> -1 && Dp_CMS_cosTheta < -0.7 "
elif args.bin == 'b':
  Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta> -0.7 && Dp_CMS_cosTheta < -0.4 "
elif args.bin == 'c':
  Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta> -0.4 && Dp_CMS_cosTheta < 0 "
elif args.bin == 'd':
  Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta> 0 && Dp_CMS_cosTheta < 0.4 "
elif args.bin == 'e':
  Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta> 0.4 && Dp_CMS_cosTheta < 0.7 "
elif args.bin == 'f':
  Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta> 0.7 && Dp_CMS_cosTheta < 1.0 "

print(Dp_CMS_cosTheta_cut)

suffix = "only_true_KDE"
file_name_Dp = f"/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv12_bdt_{args.train}_Dp_CMS_{args.bin}_{BDT_cut}_{suffix}_weighted.png"
file_name_Dm = f"/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv12_bdt_{args.train}_Dm_CMS_{args.bin}_{BDT_cut}_{suffix}_weighted.png"
file_name_Dall = f"/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv12_bdt_{args.train}_Dall_CMS_{args.bin}_{BDT_cut}_{suffix}_weighted.pdf"
fitresult_name = f"/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv12_bdt_{args.train}_{args.bin}_{BDT_cut}_{suffix}_weighted.root"
fitresult_text = f"/share/storage/jykim/plots/MC15rd/etaKp/pipipi/generic/fitresult/MC15rd_etaKp_pipipi_fit_opt_loose_v7_fitv12_bdt_{args.train}_{args.bin}_{BDT_cut}_{suffix}_weighted.txt"
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

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto"
cm_elements = ["15rd_jae_e7_18_4S_v3", "15rd_jae_e20_b26_v1", "15rd_jae_e20_e26_4S_v2", "15rd_jae_e21_5S_scan_v1", "15rd_jae_mori_off_v1"]

tree_name = "etapip_pipipi_K"
file_list = []
for element in cm_elements:
    pattern = f"{base_path}/{element}/{tree_name}/min_unc_search/{BDT_cut}/weighted/*BDT.root"
    file_list += glob.glob(pattern)

print(file_list)
mychain = ROOT.TChain(tree_name)
for i in file_list:
    mychain.Add(i)
print(file_list)
print(f"Numer of files: {len(file_list)}")

# Define variable and its range
fit_variable = "Dp_M"
fit_var_name = "M(#eta_{3#pi}K^{+}) [GeV/c^{2}]"
import_range = (1.75, 2.045)
fit_range = (1.85, 2.045)

#padding = 0.05
#fit_range = (1.75, 2.045)
#fit_min, fit_max = fit_range[0], fit_range[1]
#x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_min - padding, fit_max + padding)
#x.setRange("fit_region", fit_min, fit_max)

truth_var = "Dp_isSignal"
charge_var = "Pip_charge"

cuts_Dp = ("Pip_charge==1 && rank_Dp_chiProb==1 && "
           "(etapip_Eta_isSignal == 1 && Pip_genMotherID == etapip_Eta_genMotherID && "
           "etapip_Eta_genMotherPDG == 411 && Pip_mcPDG == 211)")

cuts_Dm = ("Pip_charge==-1 && rank_Dp_chiProb==1 && "
           "(etapip_Eta_isSignal == 1 && Pip_genMotherID == etapip_Eta_genMotherID && "
           "etapip_Eta_genMotherPDG == -411 && Pip_mcPDG == -211)")

cuts_Dp += " && " + Dp_CMS_cosTheta_cut
cuts_Dm += " && " + Dp_CMS_cosTheta_cut

x = ROOT.RooRealVar(fit_variable, fit_var_name, import_range[0], import_range[1])
x.setRange("fit_region", fit_range[0], fit_range[1])
#x.setBins(200)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)
Dp_CMS_cosTheta = ROOT.RooRealVar("Dp_CMS_cosTheta", "Dp_CMS_cosTheta", -1, 1)
BDT = ROOT.RooRealVar("BDT", "BDT", 0, 1)
Pip_dr = ROOT.RooRealVar("Pip_dr", "Pip_dr", -10000, 10000)
Dp_dz = ROOT.RooRealVar("Dp_dz", "Dp_dz", -10000, 10000)
Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane = ROOT.RooRealVar("Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane", "Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane'", -1,1)
Dp_cosHelicityAngleMomentum = ROOT.RooRealVar("Dp_cosHelicityAngleMomentum", "Dp_cosHelicityAngleMomentum", -1, 1)
Dp_CMS_p = ROOT.RooRealVar("Dp_CMS_p", "Dp_CMS_p", 0, 100)
ds_weight = ROOT.RooRealVar("ds_weight", "ds_weight", -1000, 1000)
rank_Dp_chiProb = ROOT.RooRealVar("rank_Dp_chiProb", "rank_Dp_chiProb", 0, 1000)

etapip_Eta_isSignal = ROOT.RooRealVar("etapip_Eta_isSignal", "etapip_Eta_isSignal", -1e9, 1e9)
Pip_genMotherID = ROOT.RooRealVar("Pip_genMotherID", "Pip_genMotherID", -1e9, 1e9)
etapip_Eta_genMotherID = ROOT.RooRealVar("etapip_Eta_genMotherID", "etapip_Eta_genMotherID", -1e9, 1e9)
etapip_Eta_genMotherPDG = ROOT.RooRealVar("etapip_Eta_genMotherPDG", "etapip_Eta_genMotherPDG", -1e9, 1e9)
Pip_mcPDG = ROOT.RooRealVar("Pip_mcPDG", "Pip_mcPDG", -1e9, 1e9)

full_var_set = ROOT.RooArgSet(x, Pip_charge, Dp_CMS_cosTheta, BDT, Pip_dr, Dp_dz,
                              Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane,
                              Dp_cosHelicityAngleMomentum,
                              Dp_CMS_p,rank_Dp_chiProb,ds_weight,
                              etapip_Eta_isSignal, Pip_genMotherID, etapip_Eta_genMotherID, etapip_Eta_genMotherPDG, Pip_mcPDG)

before_data = ROOT.RooDataSet("before_data","Data before weighting",full_var_set,ROOT.RooFit.Import(mychain),ROOT.RooFit.Cut(cuts_Dp))
scale = 1
w_scaled = ROOT.RooFormulaVar("w_scaled", "Scaled Weight", f"{scale}*ds_weight", ROOT.RooArgList(ds_weight))
before_data.addColumn(w_scaled)
data = ROOT.RooDataSet("data_weighted","Weighted Data",before_data,before_data.get(),"","w_scaled")
# Verify the weight is applied
print(f"Unweighted events: {before_data.sumEntries()}")
print(f"Weighted events: {data.sumEntries()}")

mychain_cc = ROOT.TChain(tree_name)
for i in file_list:
    mychain_cc.Add(i)
before_data_cc = ROOT.RooDataSet("before_data_cc","Data CC before weighting",full_var_set,ROOT.RooFit.Import(mychain_cc),ROOT.RooFit.Cut(cuts_Dm))
before_data_cc.addColumn(w_scaled)
data_cc = ROOT.RooDataSet("data_weighted_cc","Weighted Data CC",before_data_cc,before_data_cc.get(),"","w_scaled")
# Verify the weight is applied
print(f"Unweighted events: {before_data_cc.sumEntries()}")
print(f"Weighted events: {data_cc.sumEntries()}")

N_total = RooRealVar("N_total", "N_total (N_D+ + N_D-)", 1000*scale*N_scale, 0*scale*N_scale, 10000*scale*N_scale)  # N_total = N_D+ + N_D-
Acp = RooRealVar("Acp", "Acp", 0, -1, 1)  # A_Cp as a fit parameter

# Use Acp and N_total to define the expected signal yields for D+ and D-
Nsig_D_plus = RooFormulaVar("Nsig_D_plus",
    "0.5 * N_total * (1 + Acp)",
    RooArgList(N_total, Acp))

Nsig_D_minus = RooFormulaVar("Nsig_D_minus",
    "0.5 * N_total * (1 - Acp)",
    RooArgList(N_total, Acp))

# Open the workspace file
f_in = ROOT.TFile("/share/storage/jykim/plots/MC15rd/etaKp/pipipi/MC15re_6M_etapip_pipipi_Dp_M_v12_result_true_extended_train_Dp_CMS_p.0.77_workspace.root", "READ")
ws = f_in.Get("ws_kde")

# 1. Retrieve the model
#loaded_model = ws.pdf("extended_signal_model")
kde_model = ws.pdf("model")

# 2. Retrieve and Rename the variables
# This changes the internal name so the PDF now points to the new names
#x_new = ws.var("Dp_M")
#x_new.SetName("mass_D")

#n_sig_new = ws.var("N_signal")
#n_sig_new.SetName("N_total")

# Define extended PDFs for D+ and D-
model_D_plus = ROOT.RooAddPdf("model_D_plus", "D+ model",
                              ROOT.RooArgList(kde_model),
                              ROOT.RooArgList(Nsig_D_plus))
model_D_minus = ROOT.RooAddPdf("model_D_minus", "D- model",
                              ROOT.RooArgList(kde_model),
                              ROOT.RooArgList(Nsig_D_minus))

# Create a category to distinguish between D+ and D-
cat = RooCategory("sample", "sample")
cat.defineType("D_plus")
cat.defineType("D_minus")

# Create a simultaneous PDF using the category
sim_model = RooSimultaneous("sim_model", "Simultaneous model", cat)
sim_model.addPdf(model_D_plus, "D_plus")
sim_model.addPdf(model_D_minus, "D_minus")

#data_combined = RooDataSet("data_combined", "Combined data", RooArgList(x, w_1), RooFit.Index(cat),
data_combined = RooDataSet("data_combined", "Combined data", full_var_set,RooFit.Index(cat),
                           RooFit.Import("D_plus", data),
                           RooFit.Import("D_minus", data_cc),
                           RooFit.WeightVar('w_scaled'))

fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(8), RooFit.Strategy(1), ROOT.RooFit.Offset(True), ROOT.RooFit.Range("fit_region"))
#fit_result = sim_model.fitTo(data_combined, RooFit.Save(), RooFit.Extended(True), RooFit.SumW2Error(True), ROOT.RooFit.NumCPU(8), RooFit.Strategy(1), ROOT.RooFit.Offset(True))

# Print fit results
fit_result.Print()

# Output the Acp value and its error
Acp_value = Acp.getVal()
Acp_error = Acp.getError()

print(f"Acp = {Acp_value:.3f} ± {Acp_error:.3f}")

# Output N_total
N_total_value = N_total.getVal()
N_total_error = N_total.getError()

print(f"N_total = {N_total_value:.0f} ± {N_total_error:.3f}")

# Create plots for D+ and D-
canvas_D_plus = ROOT.TCanvas("canvas_D_plus", "D+ fit", 800, 600)
xlow = ctypes.c_double()
ylow = ctypes.c_double()
xup = ctypes.c_double()
yup = ctypes.c_double()
canvas_D_plus.GetPad(0).GetPadPar(xlow, ylow, xup, yup)
canvas_D_plus.Divide(1,2)

xlow = xlow.value
ylow = ylow.value
xup = xup.value
yup = yup.value

upPad = canvas_D_plus.GetPad(1)
upPad.SetPad(xlow, ylow+0.25*(yup-ylow),xup,yup)

dwPad = canvas_D_plus.GetPad(2)
dwPad.SetPad(xlow, ylow,xup,ylow+0.25*(yup-ylow))

canvas_D_plus.cd(1)
#frame_D_plus = x.frame(ROOT.RooFit.Title("D+ fit"))
frame_D_plus = x.frame(ROOT.RooFit.Title("D+ fit"), ROOT.RooFit.Range("fit_region"))
#simPdf.plotOn(frame1, Slice(sample, "plus"), Components("bkg"), ProjWData(sample, combData), LineStyle(kDashed));
#simPdf.plotOn(frame1, Slice(sample, "plus"), ProjWData(sample, combData));
slicedData_Dp = data_combined.reduce(Cut="sample==sample::D_plus")
slicedData_Dp.plotOn(frame_D_plus, Name="data")

#sim_model.plotOn(frame_D_plus, Name="Background", Components="model_bkg", ProjWData=(cat, slicedData_Dp),LineColor=ROOT.kGreen+2)
sim_model.plotOn(frame_D_plus, Name="Fitting",ProjWData=(cat, slicedData_Dp))
frame_D_plus.Draw("PE")
frame_D_plus.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.2, 0.65, 0.4, 0.90)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)
leg1.AddEntry("data", "#scale[1]{#font[42]{MC}}", "PE")
leg1.AddEntry("Fitting", "#scale[1]{#font[42]{Fit}}", "l")
#leg1.AddEntry("Background", "#scale[1.33]{#font[42]{Combinatorial}}", "l")
leg1.SetBorderSize(0)
leg1.Draw()

hpull = frame_D_plus.pullHist()
hpull.SetFillStyle(1001)
hpull.SetFillColor(1);
for i in range(0,hpull.GetN()):#(int i=0;i<hpull.GetN();++i):
    hpull.SetPointError(i,0.0,0.0,0.0,0.0)
pullplot = x.frame(ROOT.RooFit.Range("fit_region"))
pullplot.SetTitle("")
pullplot.addPlotable(hpull,"BE")
    # pullplot.addPlotable(hpull,"PE")

pullplot.SetYTitle("Pull")
pullplot.GetXaxis().SetTitleSize(0)
pullplot.GetYaxis().SetTitleSize(0.22)
pullplot.GetYaxis().CenterTitle(True)
pullplot.GetYaxis().SetTitleOffset(0.2)
pullplot.SetMinimum(-5.)
pullplot.SetMaximum(5.)
pullplot.GetXaxis().SetLabelSize(0.15)
pullplot.GetYaxis().SetLabelSize(0.105)
canvas_D_plus.cd(2)
pullplot.Draw()

xmin1 = ctypes.c_double(fit_range[0])
xmax1 = ctypes.c_double(fit_range[1])
line = ROOT.TLine(xmin1,0.0,xmax1,0.0)
line1 = ROOT.TLine(xmin1,3.0,xmax1,3.0)
line2 = ROOT.TLine(xmin1,-3.0,xmax1,-3.0)

line.SetLineColor(ROOT.kGray+1)
line.SetLineWidth(3)
line1.SetLineColor(ROOT.kBlack)
line2.SetLineColor(ROOT.kGray+1)
line1.SetLineStyle(2)
line2.SetLineStyle(2)
line.Draw("SAME")
line1.Draw("SAME")
line2.Draw("SAME")

canvas_D_plus.Update()
canvas_D_plus.SaveAs(file_name_Dp)


canvas_D_minus = ROOT.TCanvas("canvas_D_minus", "D- fit", 800, 600)
xlow = ctypes.c_double()
ylow = ctypes.c_double()
xup = ctypes.c_double()
yup = ctypes.c_double()
canvas_D_minus.GetPad(0).GetPadPar(xlow, ylow, xup, yup)
canvas_D_minus.Divide(1,2)

xlow = xlow.value
ylow = ylow.value
xup = xup.value
yup = yup.value

upPad = canvas_D_minus.GetPad(1)
upPad.SetPad(xlow, ylow+0.25*(yup-ylow),xup,yup)

dwPad = canvas_D_minus.GetPad(2)
dwPad.SetPad(xlow, ylow,xup,ylow+0.25*(yup-ylow))

plot_x_range = (1.75, 2.05)
canvas_D_minus.cd(1)
frame_D_minus = x.frame(ROOT.RooFit.Title("D+ fit"), ROOT.RooFit.Range("fit_region"))
slicedData_Dm = data_combined.reduce(Cut="sample==sample::D_minus")
slicedData_Dm.plotOn(frame_D_minus, Name="data")
#sim_model.plotOn(frame_D_minus, Name="Background", Components="model_bkg", ProjWData=(cat, slicedData_Dm),LineColor=ROOT.kGreen+2)
sim_model.plotOn(frame_D_minus, Name="Fitting",ProjWData=(cat, slicedData_Dm))
frame_D_minus.Draw("PE")
frame_D_minus.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.2, 0.65, 0.4, 0.90)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)
leg1.AddEntry("data", "#scale[1]{#font[42]{MC}}", "PE")
leg1.AddEntry("Fitting", "#scale[1]{#font[42]{Fit}}", "l")
#leg1.AddEntry("Background", "#scale[1.33]{#font[42]{Combinatorial}}", "l")
leg1.SetBorderSize(0)
leg1.Draw()

hpull = frame_D_minus.pullHist()
hpull.SetFillStyle(1001)
hpull.SetFillColor(1);
for i in range(0,hpull.GetN()):#(int i=0;i<hpull.GetN();++i):
    hpull.SetPointError(i,0.0,0.0,0.0,0.0)
pullplot = x.frame(ROOT.RooFit.Range("fit_region"))
pullplot.SetTitle("")
pullplot.addPlotable(hpull,"BE")
    # pullplot.addPlotable(hpull,"PE")

pullplot.SetYTitle("Pull")
pullplot.GetXaxis().SetTitleSize(0)
pullplot.GetYaxis().SetTitleSize(0.22)
pullplot.GetYaxis().CenterTitle(True)
pullplot.GetYaxis().SetTitleOffset(0.2)
pullplot.SetMinimum(-5.)
pullplot.SetMaximum(5.)
pullplot.GetXaxis().SetLabelSize(0.15)
pullplot.GetYaxis().SetLabelSize(0.105)
canvas_D_minus.cd(2)
pullplot.Draw()

xmin1 = ctypes.c_double(fit_range[0])
xmax1 = ctypes.c_double(fit_range[1])
# xmin1 = ctypes.c_double(plot_x_range[0])
# xmax1 = ctypes.c_double(plot_x_range[1])
line = ROOT.TLine(xmin1,0.0,xmax1,0.0)
line1 = ROOT.TLine(xmin1,3.0,xmax1,3.0)
line2 = ROOT.TLine(xmin1,-3.0,xmax1,-3.0)

line.SetLineColor(ROOT.kGray+1)
line.SetLineWidth(3)
line1.SetLineColor(ROOT.kBlack)
line2.SetLineColor(ROOT.kGray+1)
line1.SetLineStyle(2)
line2.SetLineStyle(2)
line.Draw("SAME")
line1.Draw("SAME")
line2.Draw("SAME")

canvas_D_minus.Update()
canvas_D_minus.SaveAs(file_name_Dm)

canvas_D_all = ROOT.TCanvas("canvas_D_all", "D+ fit", 800, 600)
xlow = ctypes.c_double()
ylow = ctypes.c_double()
xup = ctypes.c_double()
yup = ctypes.c_double()
canvas_D_all.GetPad(0).GetPadPar(xlow, ylow, xup, yup)
canvas_D_all.Divide(1,2)

xlow = xlow.value
ylow = ylow.value
xup = xup.value
yup = yup.value

upPad = canvas_D_all.GetPad(1)
upPad.SetPad(xlow, ylow+0.25*(yup-ylow),xup,yup)

dwPad = canvas_D_all.GetPad(2)
dwPad.SetPad(xlow, ylow,xup,ylow+0.25*(yup-ylow))

canvas_D_all.cd(1)

frame_D_all = x.frame(ROOT.RooFit.Title("D+ fit"), ROOT.RooFit.Range("fit_region"))
frame_D_all.GetXaxis().SetTitle("M(#eta_{3#pi}K^{+}) [GeV/c^{2}]")

data_combined.plotOn(frame_D_all, Name="data")
#sim_model.plotOn(frame_D_all, Name="Background", Components="model_bkg", ProjWData=(cat, data_combined),LineColor=ROOT.kGreen+2)
sim_model.plotOn(frame_D_all, Name="Fitting",ProjWData=(cat, data_combined))
frame_D_all.Draw("PE")
frame_D_all.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.2, 0.65, 0.4, 0.90)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)
leg1.AddEntry("data", "#scale[1]{#font[42]{MC}}", "PE")
leg1.AddEntry("Fitting", "#scale[1]{#font[42]{Fit}}", "l")
#leg1.AddEntry("Background", "#scale[1.33]{#font[42]{Combinatorial}}", "l")
leg1.SetBorderSize(0)
leg1.Draw()

hpull = frame_D_all.pullHist()
hpull.SetFillStyle(1001)
hpull.SetFillColor(1);
for i in range(0,hpull.GetN()):#(int i=0;i<hpull.GetN();++i):
    hpull.SetPointError(i,0.0,0.0,0.0,0.0)
pullplot = x.frame(ROOT.RooFit.Range("fit_region"))
pullplot.SetTitle("")
pullplot.addPlotable(hpull,"BE")
pullplot.SetYTitle("Pull")
pullplot.GetXaxis().SetTitleSize(0)
pullplot.GetYaxis().SetTitleSize(0.22)
pullplot.GetYaxis().CenterTitle(True)
pullplot.GetYaxis().SetTitleOffset(0.2)
pullplot.SetMinimum(-5.)
pullplot.SetMaximum(5.)
pullplot.GetXaxis().SetLabelSize(0.15)
pullplot.GetYaxis().SetLabelSize(0.105)
canvas_D_all.cd(2)
pullplot.Draw()

xmin1 = ctypes.c_double(fit_range[0])
xmax1 = ctypes.c_double(fit_range[1])
line = ROOT.TLine(xmin1,0.0,xmax1,0.0)
line1 = ROOT.TLine(xmin1,3.0,xmax1,3.0)
line2 = ROOT.TLine(xmin1,-3.0,xmax1,-3.0)

line.SetLineColor(ROOT.kGray+1)
line.SetLineWidth(3)
line1.SetLineColor(ROOT.kBlack)
line2.SetLineColor(ROOT.kGray+1)
line1.SetLineStyle(2)
line2.SetLineStyle(2)
line.Draw("SAME")
line1.Draw("SAME")
line2.Draw("SAME")

canvas_D_all.Update()
canvas_D_all.SaveAs(file_name_Dall)


f = ROOT.TFile(fitresult_name, "RECREATE")
fit_result.Write("jykim")
f.Close()

# Open a text file in write mode
with open(fitresult_text, "w") as f:

    # Print the full fit result to the file
    f.write("Full fit result summary:\n")
    fit_result.Print("v")  # Verbose print (prints more details)

    # Alternatively, write specific attributes to the file
    f.write("\nSpecific fit result details:\n")
    f.write(f"Status: {fit_result.status()}\n")
    f.write(f"Covariance quality: {fit_result.covQual()}\n")
    f.write(f"EDM (Estimated Distance to Minimum): {fit_result.edm()}\n")
    f.write(f"Min NLL: {fit_result.minNll()}\n")

    # Access and write parameter values and errors to the file
    f.write("\nFitted Parameters:\n")
    params = fit_result.floatParsFinal()  # This returns the final fitted parameters
    for i in range(params.getSize()):
        param = params[i]
        f.write(f"{param.GetName()} = {param.getVal()} ± {param.getError()}\n")

    # Retrieve the values and errors of N_total and Acp
    N_total_val = N_total.getVal()
    N_total_err = N_total.getError()

    Acp_val = Acp.getVal()
    Acp_err = Acp.getError()

    # Calculate Nsig_D_plus and its error
    Nsig_D_plus_val = 0.5 * N_total_val * (1 + Acp_val)
    Nsig_D_plus_err = 0.5 * ((1 + Acp_val) * N_total_err + N_total_val * Acp_err)

    # Calculate Nsig_D_minus and its error
    Nsig_D_minus_val = 0.5 * N_total_val * (1 - Acp_val)
    Nsig_D_minus_err = 0.5 * ((1 - Acp_val) * N_total_err + N_total_val * Acp_err)

    # Print the results
    f.write(f"Nsig_D_plus: Value = {Nsig_D_plus_val}, Error = {Nsig_D_plus_err}\n")
    f.write(f"Nsig_D_minus: Value = {Nsig_D_minus_val}, Error = {Nsig_D_minus_err}\n")

    # Optionally print a completion message
    f.write("\nFit result saved successfully.\n")
