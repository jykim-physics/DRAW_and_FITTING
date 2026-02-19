import ROOT
import glob
import ctypes
import os
import math

ROOT.gROOT.LoadMacro('/home/jykim/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()
file_name = "/share/storage/jykim/plots/MC15rd/etaKp/gg/MC15rd_etapip_gg_K_Dp_M_v12_combinatorial.0.86.png"
result_name = "/share/storage/jykim/plots/MC15rd/etaKp/gg//MC15rd_etapip_gg_K_Dp_M_v12_combinatorial_result.0.86.txt"
fitresult_root = "/share/storage/jykim/plots/MC15rd/etaKp/gg//MC15rd_etapip_gg_K_Dp_M_v12_combinatorial_result.0.86.root"

file_dir = os.path.dirname(file_name)
result_dir = os.path.dirname(result_name)
os.makedirs(file_dir, exist_ok=True)
os.makedirs(result_dir, exist_ok=True)

# Get the tree from the file
tree_name = "etapip_gg_K"

# Define fitting variable and its range
fit_variable = "Dp_M"
fit_var_name = "M(D^{+}) [GeV/c^{2}]"
fit_var_name = "M(#eta_{#gamma#gamma}K^{+}) [GeV/c^{2}]"
fit_range = (1.75, 2.045)

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto"
cm_elements = ["15rd_jae_e7_18_4S_v3", "15rd_jae_e20_b26_v1", "15rd_jae_e20_e26_4S_v2", "15rd_jae_e21_5S_scan_v1", "15rd_jae_mori_off_v1"]

tree_name = "etapip_gg_K"
file_list = []
#for element in cm_elements:
#    pattern = f"{base_path}/{element}/{tree_name}/min_unc_search/0.86/weighted/*BDT.root"
#    file_list += glob.glob(pattern)

for element in cm_elements:
    pattern = f"{base_path}/{element}/{tree_name}/min_unc_search/0.86/weighted/*BDT.root"
    matched_files = glob.glob(pattern)

    for f in matched_files:
        if "ccbar" not in f:
            file_list.append(f)

#print(file_list)
mychain = ROOT.TChain(tree_name)
for i in file_list:
    mychain.Add(i)
print(file_list)
print(f"Numer of files: {len(file_list)}")

fit_variable = "Dp_M"
fit_var_name = "M(#eta_{#gamma#gamma}K^{+}) [GeV/c^{2}]"
fit_range = (1.75, 2.045)
#fit_range = (1.755, 2.045)
truth_var = "Dp_isSignal"
charge_var = "Pip_charge"

cuts_Dp = charge_var + "==1 && rank_Dp_chiProb==1"
cuts_Dm = charge_var + "==-1 && rank_Dp_chiProb==1"

#cuts_Dp += " && " + Dp_CMS_cosTheta_cut
#cuts_Dm += " && " + Dp_CMS_cosTheta_cut


x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
#x.setBins(200)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)
Dp_CMS_cosTheta = ROOT.RooRealVar("Dp_CMS_cosTheta", "Dp_CMS_cosTheta", -1, 1)
BDT = ROOT.RooRealVar("BDT", "BDT", 0, 1)
Pip_dr = ROOT.RooRealVar("Pip_dr", "Pip_dr", -10000, 10000)
Dp_dz = ROOT.RooRealVar("Dp_dz", "Dp_dz", -10000, 10000)
Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane = ROOT.RooRealVar("Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane", "Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane'", -1,1)
etapip_Eta_Easym = ROOT.RooRealVar("etapip_Eta_Easym", "etapip_Eta_Easym", 0, 1)
Dp_cosHelicityAngleMomentum = ROOT.RooRealVar("Dp_cosHelicityAngleMomentum", "Dp_cosHelicityAngleMomentum", -1, 1)
Dp_CMS_p = ROOT.RooRealVar("Dp_CMS_p", "Dp_CMS_p", 0, 100)
ds_weight = ROOT.RooRealVar("ds_weight", "ds_weight", -1000, 1000)
rank_Dp_chiProb = ROOT.RooRealVar("rank_Dp_chiProb", "rank_Dp_chiProb", 0, 1000)

full_var_set = ROOT.RooArgSet(x, Pip_charge, Dp_CMS_cosTheta, BDT, Pip_dr, Dp_dz,
                              Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane,
                              etapip_Eta_Easym, Dp_cosHelicityAngleMomentum,
                              Dp_CMS_p,rank_Dp_chiProb,ds_weight)

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

nAllSigCascDcyBr_9 = ROOT.RooRealVar("nAllSigCascDcyBr_9", "nAllSigCascDcyBr_9", -1E9, 1E9)
nAllSigCascDcyBr_13 = ROOT.RooRealVar("nAllSigCascDcyBr_13", "nAllSigCascDcyBr_13", -1E9, 1E9)
full_var_set_topo = ROOT.RooArgSet(x, Pip_charge, Dp_CMS_cosTheta, BDT, Pip_dr, Dp_dz,
                              Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane,
                              etapip_Eta_Easym, Dp_cosHelicityAngleMomentum,
                              Dp_CMS_p,rank_Dp_chiProb,ds_weight, nAllSigCascDcyBr_9, nAllSigCascDcyBr_13)
# Create a TChain and add all ROOT files
mychain_ccbar = ROOT.TChain(tree_name)
mychain_ccbar.Add("/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto/topo_basic/15rd_jae_e7_18_4S_v3/resultfile/result_etapip_gg_K/standard.root")
mychain_ccbar.Add("/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto/topo_basic/15rd_jae_e20_b26_v1/resultfile/result_etapip_gg_K/standard.root")
mychain_ccbar.Add("/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto/topo_basic/15rd_jae_e20_e26_4S_v2/resultfile/result_etapip_gg_K/standard.root")
mychain_ccbar.Add("/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto/topo_basic/15rd_jae_e21_5S_scan_v1/resultfile/result_etapip_gg_K/standard.root")
mychain_ccbar.Add("/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto/topo_basic/15rd_jae_mori_off_v1/resultfile/result_etapip_gg_K/standard.root")
before_data_ccbar = ROOT.RooDataSet("before_data_ccbar","Data before weighting",full_var_set_topo,ROOT.RooFit.Import(mychain_ccbar),ROOT.RooFit.Cut(cuts_Dp + ' && nAllSigCascDcyBr_9 <= 0 && nAllSigCascDcyBr_13 <= 0'))
before_data_ccbar.addColumn(w_scaled)
data_ccbar = ROOT.RooDataSet("data_weighted","Weighted Data",before_data_ccbar,before_data_ccbar.get(),"","w_scaled")

mychain_ccbar_cc= ROOT.TChain(tree_name)
mychain_ccbar_cc.Add("/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto/topo_basic/15rd_jae_e7_18_4S_v3/resultfile/result_etapip_gg_K/standard.root")
mychain_ccbar_cc.Add("/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto/topo_basic/15rd_jae_e20_b26_v1/resultfile/result_etapip_gg_K/standard.root")
mychain_ccbar_cc.Add("/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto/topo_basic/15rd_jae_e20_e26_4S_v2/resultfile/result_etapip_gg_K/standard.root")
mychain_ccbar_cc.Add("/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto/topo_basic/15rd_jae_e21_5S_scan_v1/resultfile/result_etapip_gg_K/standard.root")
mychain_ccbar_cc.Add("/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/EtaHp/MC15rd_loose_v7_260108_nopi0veto/topo_basic/15rd_jae_mori_off_v1/resultfile/result_etapip_gg_K/standard.root")
before_data_ccbar_cc = ROOT.RooDataSet("before_data_ccbar_cc","Data before weighting",full_var_set_topo,ROOT.RooFit.Import(mychain_ccbar_cc),ROOT.RooFit.Cut(cuts_Dm + ' && nAllSigCascDcyBr_9 <= 0 && nAllSigCascDcyBr_13 <= 0'))
before_data_ccbar_cc.addColumn(w_scaled)
data_ccbar_cc = ROOT.RooDataSet("data_weighted_cc","Weighted Data",before_data_ccbar_cc,before_data_ccbar_cc.get(),"","w_scaled")

data.append(data_cc)
data.append(data_ccbar)
data.append(data_ccbar_cc)

N_total = data.sumEntries()
#print(N_total)

N_signal = ROOT.RooRealVar("N_signal", "Number of signal events", N_total, 0.7*N_total, 1.2*N_total)  # Initial guess and bounds
x_bkg1_tau = ROOT.RooRealVar("x_bkg1_tau", "c0",-5, -20, 5)
model = ROOT.RooExponential("model", "x_bkg1", x, x_bkg1_tau)

extended_signal_model = ROOT.RooAddPdf(
    "extended_signal_model",
    "Extended Signal Model",
    ROOT.RooArgList(model),
    ROOT.RooArgList(N_signal)
)


result = extended_signal_model.fitTo(
    data,
    ROOT.RooFit.Extended(True),  # Enable extended likelihood fit
    ROOT.RooFit.Range(fit_range[0], fit_range[1]),
    ROOT.RooFit.NumCPU(8),
    ROOT.RooFit.Save(),
    ROOT.RooFit.Offset("initial"),
    ROOT.RooFit.Strategy(1)
)
result.Print()

f = ROOT.TFile(fitresult_root, "RECREATE")
result.Write("jykim")
f.Close()

fitted_N_signal = N_signal.getVal()

# Open a text file in write mode
with open(result_name, "w") as f:

    # Print the full fit result to the file
    f.write("Full fit result summary:\n")
    result.Print("v")  # Verbose print (prints more details)

    # Alternatively, write specific attributes to the file
    f.write("\nSpecific fit result details:\n")
    f.write(f"Status: {result.status()}\n")
    f.write(f"Covariance quality: {result.covQual()}\n")
    f.write(f"EDM (Estimated Distance to Minimum): {result.edm()}\n")
    f.write(f"Min NLL: {result.minNll()}\n")

    # Access and write parameter values and errors to the file
    f.write("\nFitted Parameters:\n")
    params = result.floatParsFinal()  # This returns the final fitted parameters
    for i in range(params.getSize()):
        param = params[i]
        f.write(f"{param.GetName()} = {param.getVal()} ± {param.getError()}, Err/Val = {param.getError()/param.getVal()*100:.4f}%\n")

    # Optionally print a completion message
    f.write("\nFit result saved successfully.\n")

# Plot the result
#canvas = ROOT.TCanvas("canvas", "canvas", 800, 555)
canv = ROOT.TCanvas("canvas", "canvas", 700, 640)
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

canv.cd(1)
frame = x.frame()

#frame.GetYaxis().SetTitleOffset(0.2)

data.plotOn(frame, ROOT.RooFit.Name("data1"), ROOT.RooFit.XErrorSize(0))


model.plotOn(frame, ROOT.RooFit.Name("fitting"))

frame.Draw("PE")
frame.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.68, 0.65, 0.93, 0.9)
# leg1.SetFillColor(ROOT.kWhite)
leg1.SetFillColor(0)

    # leg1.SetHeader("The Legend title","C")
leg1.AddEntry("data1", "Bkg", "PE")
leg1.AddEntry("fitting", "Fit", "l")
#leg1.AddEntry("Signal", "Signal", "l")
# leg1.AddEntry("fitx_bkg3", "bkg3", "l")

# leg1.SetTextSize(0.05)
# leg1.SetTextAlign(13)

leg1.SetBorderSize(0)
leg1.Draw()

hpull = frame.pullHist()
hpull.SetFillStyle(1001)
hpull.SetFillColor(1);
for i in range(0,hpull.GetN()):#(int i=0;i<hpull.GetN();++i):
    hpull.SetPointError(i,0.0,0.0,0.0,0.0)
pullplot = x.frame()
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
canv.cd(2)
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

canv.Update()

canv.Draw()
canv.SaveAs(file_name)

# Save the final figure as .png
#canv.SaveAs("fit_result_with_pull.png")
