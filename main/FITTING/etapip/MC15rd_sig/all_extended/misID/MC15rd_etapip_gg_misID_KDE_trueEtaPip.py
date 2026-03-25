import ROOT
import glob
import ctypes
import os
import math

ROOT.gROOT.LoadMacro('/home/jykim/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()
file_name = "/share/storage/jykim/plots/MC15rd/etaKp/gg/MC15rd_6M_etapip_gg_Dp_M_v12_true_extended_train_Dp_CMS_p_0.86.png"
result_name = "/share/storage/jykim/plots/MC15rd/etaKp/gg/MC15rd_6M_etapip_gg_Dp_M_v12_result_true_extended_train_Dp_CMS_p_0.86.txt"
fitresult_root = "/share/storage/jykim/plots/MC15rd/etaKp/gg/MC15re_6M_etapip_gg_Dp_M_v12_result_true_extended_train_Dp_CMS_p.0.86.root"

file_dir = os.path.dirname(file_name)
result_dir = os.path.dirname(result_name)
os.makedirs(file_dir, exist_ok=True)
os.makedirs(result_dir, exist_ok=True)

tree_name = "etapip_gg_K"

fit_variable = "Dp_M"
fit_var_name = "M(D^{+}) [GeV/c^{2}]"
fit_var_name = "M(#eta_{#gamma#gamma}K^{+}) [GeV/c^{2}]"
padding = 0.05
fit_range = (1.75, 2.045)
fit_min, fit_max = fit_range[0], fit_range[1]
x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_min - padding, fit_max + padding)

x.setRange("fit_region", fit_min, fit_max)
rank_var = tree_name + "_rank"
truth_var = "Dp_isSignal"
charge_var = "Pip_charge"
cuts = rank_var + "==1"
cuts_Dp = ("Pip_charge==1 && rank_Dp_chiProb==1 && "
           "(etapip_Eta_isSignal == 1 && Pip_genMotherID == etapip_Eta_genMotherID && "
           "etapip_Eta_genMotherPDG == 411 && Pip_mcPDG == 211)")

cuts_Dm = ("Pip_charge==-1 && rank_Dp_chiProb==1 && "
           "(etapip_Eta_isSignal == 1 && Pip_genMotherID == etapip_Eta_genMotherID && "
           "etapip_Eta_genMotherPDG == -411 && Pip_mcPDG == -211)")

x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
chiProb_rank = ROOT.RooRealVar(rank_var, rank_var, 0, 30)
truth_var = ROOT.RooRealVar(truth_var, truth_var, 0, 30)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)
rank_Dp_chiProb = ROOT.RooRealVar("rank_Dp_chiProb", "rank_Dp_chiProb", 0, 1000)

etapip_Eta_isSignal = ROOT.RooRealVar("etapip_Eta_isSignal", "etapip_Eta_isSignal", -1e9, 1e9)
Pip_genMotherID = ROOT.RooRealVar("Pip_genMotherID", "Pip_genMotherID", -1e9, 1e9)
etapip_Eta_genMotherID = ROOT.RooRealVar("etapip_Eta_genMotherID", "etapip_Eta_genMotherID", -1e9, 1e9)
etapip_Eta_genMotherPDG = ROOT.RooRealVar("etapip_Eta_genMotherPDG", "etapip_Eta_genMotherPDG", -1e9, 1e9)
Pip_mcPDG = ROOT.RooRealVar("Pip_mcPDG", "Pip_mcPDG", -1e9, 1e9)


mychain = ROOT.TChain(tree_name)
mychain.Add("/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_gg/260107_loose_v7_less_vars_ntuple/etapip_gg_K/min_unc_search/0.86/*BDT.root")
tree_name_cc = "etapip_gg_K"
mychain_cc = ROOT.TChain(tree_name_cc)
mychain_cc.Add("/share/storage/jykim/storage_ghi/Ntuples_ghi_2/MC15rd_sigMC/Dptoetapip_gg_cc/260107_loose_v7_less_vars_ntuple/etapip_gg_K/min_unc_search/0.86/*BDT.root")

before_data = ROOT.RooDataSet("data","", mychain, ROOT.RooArgSet(x,truth_var, Pip_charge, rank_Dp_chiProb, etapip_Eta_isSignal, Pip_genMotherID, etapip_Eta_genMotherID, etapip_Eta_genMotherPDG, Pip_mcPDG), cuts_Dp)

w_1 = ROOT.RooRealVar('w_1', 'w', 0,1)
w_1.setVal(1)
before_data.addColumn(w_1)
data = ROOT.RooDataSet(before_data.GetName(), before_data.GetTitle(),before_data, before_data.get(), '' ,  'w_1')

before_data_cc = ROOT.RooDataSet("data_cc","", mychain_cc, ROOT.RooArgSet(x,truth_var, Pip_charge,rank_Dp_chiProb, etapip_Eta_isSignal, Pip_genMotherID, etapip_Eta_genMotherID, etapip_Eta_genMotherPDG, Pip_mcPDG), cuts_Dm)
before_data_cc.addColumn(w_1)
data_cc = ROOT.RooDataSet(before_data_cc.GetName(), before_data_cc.GetTitle(),before_data_cc, before_data_cc.get(), '' ,  'w_1')

data.append(data_cc)

N_total = data.sumEntries()
print(N_total)
N_signal = ROOT.RooRealVar("N_signal", "Number of signal events", N_total, 0.8*N_total, 1.2*N_total)  # Initial guess and bounds

model = ROOT.RooKeysPdf(
    "model",
    "KDE Signal Model",
    x,
    data,
    ROOT.RooKeysPdf.MirrorBoth, #ROOT.RooKeysPdf.NoMirror,
    1.4
)
extended_signal_model = ROOT.RooAddPdf(
    "extended_signal_model",
    "Extended KDE Signal Model",
    ROOT.RooArgList(model),
    ROOT.RooArgList(N_signal)
)

result = extended_signal_model.fitTo(
    data,
    ROOT.RooFit.Extended(True),  # Enable extended likelihood fit
    ROOT.RooFit.Range("fit_region"),
    ROOT.RooFit.NumCPU(8),
    ROOT.RooFit.Save(),
    ROOT.RooFit.Offset(True),
    ROOT.RooFit.Strategy(1)
)
result.Print()

# --- SAVE WORKSPACE SECTION ---
# 1. Define the workspace file path (using your existing directory logic)
workspace_root = fitresult_root.replace(".root", "_workspace.root")

# 2. Create the Workspace
ws = ROOT.RooWorkspace("ws_kde", "Workspace for KDE Signal Model")

# 3. Import the Extended Model
# Note: Using getattr because 'import' is a reserved keyword in Python
getattr(ws, 'import')(extended_signal_model)

# 4. Save to File
ws_file = ROOT.TFile(workspace_root, "RECREATE")
ws.Write()
ws_file.Close()

print(f"Workspace saved successfully to: {workspace_root}")
# ------------------------------

f = ROOT.TFile(fitresult_root, "RECREATE")
result.Write("jykim")
f.Close()

fitted_N_signal = N_signal.getVal()
total_signal_events =  6*1e6
signal_efficiency = fitted_N_signal / total_signal_events

def calculate_sig_eff_err(eff, N_gen):

    error = math.sqrt(eff * (1 - eff) / N_gen)
    return error

with open(result_name, "w") as f:

    f.write("Full fit result summary:\n")
    result.Print("v")

    f.write("\nSpecific fit result details:\n")
    f.write(f"Status: {result.status()}\n")
    f.write(f"Covariance quality: {result.covQual()}\n")
    f.write(f"EDM (Estimated Distance to Minimum): {result.edm()}\n")
    f.write(f"Min NLL: {result.minNll()}\n")

    f.write("\nFitted Parameters:\n")
    params = result.floatParsFinal()
    for i in range(params.getSize()):
        param = params[i]
        f.write(f"{param.GetName()} = {param.getVal()} ± {param.getError()}, Err/Val = {param.getError()/param.getVal()*100:.4f}%\n")

    f.write(f"Fitted number of signal events: {fitted_N_signal}\n")
    f.write(f"Total number of signal events in dataset: {total_signal_events}\n")
    f.write(f"Signal efficiency: {signal_efficiency:.6f}\n")
    f.write(f"Signal efficiency stats. error: {calculate_sig_eff_err(signal_efficiency,total_signal_events):.8f}\n")

    f.write(f"Counting Signal efficiency: {N_total/total_signal_events:.6f}\n")

    f.write("\nFit result saved successfully.\n")

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

#model.plotOn(frame, ROOT.RooFit.Name("Signal"),ROOT.RooFit.Components("CB_left"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed))
model.plotOn(frame, ROOT.RooFit.Name("fitting"))

frame.Draw("PE")
frame.GetXaxis().CenterTitle(True)

leg1 = ROOT.TLegend(0.20, 0.65, 0.40, 0.9)
leg1.SetFillColor(0)
leg1.AddEntry("data1", "MC", "PE")
leg1.AddEntry("fitting", "Fit", "l")
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

pullplot.SetYTitle("Pull")
pullplot.GetXaxis().SetTitleSize(0)
pullplot.GetYaxis().SetTitleSize(0.22)
pullplot.GetYaxis().CenterTitle(True)
pullplot.GetYaxis().SetTitleOffset(0.2)
pullplot.SetMinimum(-4.)
pullplot.SetMaximum(4.)
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
