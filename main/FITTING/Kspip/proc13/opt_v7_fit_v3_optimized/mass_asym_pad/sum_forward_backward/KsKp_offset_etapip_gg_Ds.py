import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooFormulaVar
import glob
import ctypes
import os
import argparse
import math

ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser(
    description="Plot combined sign-plus/sign-minus result using existing RooFitResult files. No refit is performed. Central curves only."
)
parser.add_argument("-t", "--train", required=True, help="Specify train version, same as in the fit scripts")
parser.add_argument("--nbins", type=int, default=100, help="Number of bins for data histograms")
parser.add_argument("--n-curve-points", type=int, default=500, help="Number of points used for smooth fitted curves")
parser.add_argument("--fit-object-name", default="jykim", help="Object name of RooFitResult saved in the fit-result ROOT files")
parser.add_argument("--output", default="", help="Output PDF path. If empty, use the default /share/storage/... path")
args = parser.parse_args()

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
BDT_cut = "0.86"
suffix = "sumw2fixed_mass_asym_pad_filled_bkg"
base_plot_dir = "/share/storage/jykim/plots/proc13/KsKp/gg/generic"
base_fit_dir = f"{base_plot_dir}/fitresult"

fitresult_name_plus = (
    f"{base_fit_dir}/proc13_Kspip_gg_K_fit_opt_loose_v7_fitv3_Ds_{args.train}_Dp_CMS_plus_{suffix}.root"
)
fitresult_name_minus = (
    f"{base_fit_dir}/proc13_Kspip_gg_K_fit_opt_loose_v7_fitv3_Ds_{args.train}_Dp_CMS_minus_{suffix}.root"
)

if args.output:
    file_name_out = args.output
else:
    file_name_out = (
        f"{base_plot_dir}/proc13_Kspip_gg_K_fit_opt_loose_v7_fitv3_Ds_Dall_{args.train}_Dp_CMS_signAvg_{suffix}.pdf"
    )

for path in [file_name_out, fitresult_name_plus, fitresult_name_minus]:
    print(path)

out_dir = os.path.dirname(file_name_out)
if out_dir and not os.path.exists(out_dir):
    os.makedirs(out_dir)

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

# Input ntuples: kept identical to the fit script
base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/proc13/proc13_KsHp_loose_v7"
cm_elements = [
    "KsHp_13_4S_off_v1",
    "KsHp_13_4S_v3",
    "KsHp_23_4S_off_v1",
    "KsHp_23_4S_v1",
    "KsHp_23_5Sscan_10657_v1",
    "KsHp_23_5Sscan_10706_v1",
    "KsHp_23_5Sscan_10751_v1",
    "KsHp_23_5Sscan_10810_v1",
]
ref_tree = "etapip_gg_K"
tree_name = "Ks_K"

file_list = []
for element in cm_elements:
    pattern = f"{base_path}/{element}/{ref_tree}/{tree_name}/{BDT_cut}/*.BDT.root"
    file_list += glob.glob(pattern)
print(file_list)
print(f"Number of files: {len(file_list)}")

mychain = ROOT.TChain(tree_name)
for fname in file_list:
    mychain.Add(fname)

fit_variable = "Dp_M"
fit_var_name = "M(K_{S}^{0}K^{+}) [GeV/c^{2}]"
fit_range = (1.9, 2.03)
charge_var = "Pip_charge"

x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)
Dp_CMS_cosTheta = ROOT.RooRealVar("Dp_CMS_cosTheta", "Dp_CMS_cosTheta", -1, 1)
BDT = ROOT.RooRealVar("BDT", "BDT", 0, 1)
Pip_dr = ROOT.RooRealVar("Pip_dr", "Pip_dr", -10000, 10000)
Dp_dz = ROOT.RooRealVar("Dp_dz", "Dp_dz", -10000, 10000)
Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane = ROOT.RooRealVar("Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane","Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane",-1,1)
etapip_Eta_Easym = ROOT.RooRealVar("etapip_Eta_Easym", "etapip_Eta_Easym", 0, 1)
Dp_cosHelicityAngleMomentum = ROOT.RooRealVar("Dp_cosHelicityAngleMomentum", "Dp_cosHelicityAngleMomentum", -1, 1)
Dp_CMS_p = ROOT.RooRealVar("Dp_CMS_p", "Dp_CMS_p", 0, 100)
rank_Dp_chiProb = ROOT.RooRealVar("rank_Dp_chiProb", "rank_Dp_chiProb", 0, 1000)

varset = ROOT.RooArgSet(
    x,
    Pip_charge,
    Dp_CMS_cosTheta,
    BDT,
    Pip_dr,
    Dp_dz,
    Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane,
    etapip_Eta_Easym,
    Dp_cosHelicityAngleMomentum,
    Dp_CMS_p,
    rank_Dp_chiProb,
)

# -----------------------------------------------------------------------------
# Data import. Same logic as the original code.
# -----------------------------------------------------------------------------
def make_dataset(name, sign_name, charge):
    if sign_name == "plus":
        sign_cut = "Dp_CMS_cosTheta>0"
    elif sign_name == "minus":
        sign_cut = "Dp_CMS_cosTheta<0"
    else:
        raise ValueError(sign_name)

    cut = f"{charge_var}=={charge} && rank_Dp_chiProb==1 && {sign_cut}"
    print(f"{name}: {cut}")
    return ROOT.RooDataSet(name, name, mychain, varset, cut)

data_sp_Dp = make_dataset("data_signPlus_Dp", "plus", 1)
data_sp_Dm = make_dataset("data_signPlus_Dm", "plus", -1)
data_sm_Dp = make_dataset("data_signMinus_Dp", "minus", 1)
data_sm_Dm = make_dataset("data_signMinus_Dm", "minus", -1)

print("Entries:")
print("  sign plus,  D+:", data_sp_Dp.sumEntries())
print("  sign plus,  D-:", data_sp_Dm.sumEntries())
print("  sign minus, D+:", data_sm_Dp.sumEntries())
print("  sign minus, D-:", data_sm_Dm.sumEntries())

# -----------------------------------------------------------------------------
# Model definition. Same PDF structure as the original fit.
# -----------------------------------------------------------------------------
scale = 1 / 4

def build_model(tag):
    N_total = RooRealVar(f"N_total_{tag}", "N_total", 200000 * scale, 20000 * scale, 1000000 * scale)
    Acp = RooRealVar(f"Acp_{tag}", "Acp", 0, -1, 1)

    Nsig_D_plus = RooFormulaVar(
        f"Nsig_D_plus_{tag}",
        "0.5*@0*(1+@1)",
        RooArgList(N_total, Acp),
    )
    Nsig_D_minus = RooFormulaVar(
        f"Nsig_D_minus_{tag}",
        "0.5*@0*(1-@1)",
        RooArgList(N_total, Acp),
    )

    Nbkg_total = RooRealVar(
        f"Nbkg_total_{tag}",
        "Nbkg_total",
        100000 * scale,
        500 * scale,
        2000000 * scale,
    )
    Acp_bkg = RooRealVar(f"Acp_bkg_{tag}", "Acp_bkg", 0, -1, 1)

    Nbkg_D_plus = RooFormulaVar(
        f"Nbkg_D_plus_{tag}",
        "0.5*@0*(1+@1)",
        RooArgList(Nbkg_total, Acp_bkg),
    )
    Nbkg_D_minus = RooFormulaVar(
        f"Nbkg_D_minus_{tag}",
        "0.5*@0*(1-@1)",
        RooArgList(Nbkg_total, Acp_bkg),
    )

    mean = ROOT.RooRealVar(f"mean_{tag}", "mean", 1.96, 1.94, 1.98)
    sigma = ROOT.RooRealVar(f"sigma_{tag}", "sigma", 0.002, 0.0001, 0.01)
    gamma = ROOT.RooRealVar(f"gamma_{tag}", "gamma", 0.01, -2.0, 2.0)
    delta = ROOT.RooRealVar(f"delta_{tag}", "delta", 0.6, 0.001, 3.0)

    johnson = ROOT.RooJohnson(f"johnson_{tag}", "Johnson SU", x, mean, sigma, gamma, delta)
    mean_gauss = ROOT.RooRealVar(f"mean_gauss_{tag}", "mean_gauss", 0.0)
    sigma_gauss = ROOT.RooRealVar(f"sigma_gauss_{tag}", "sigma_gauss", 0.002, 0.00001, 0.01)
    gauss = ROOT.RooGaussian(f"gauss_{tag}", "Gaussian PDF", x, mean_gauss, sigma_gauss)
    sig_model = ROOT.RooFFTConvPdf(f"sig_model_{tag}", "Johnson SU #otimes Gaussian", x, johnson, gauss)

    x_bkg1_tau = ROOT.RooRealVar(f"x_bkg1_tau_{tag}", "x_bkg1_tau", -0.5, -20, 10)
    model_bkg = ROOT.RooExponential(f"model_bkg_{tag}", "background", x, x_bkg1_tau)

    model_D_plus = RooAddPdf(
        f"model_D_plus_{tag}",
        "D+ model",
        ROOT.RooArgList(sig_model, model_bkg),
        ROOT.RooArgList(Nsig_D_plus, Nbkg_D_plus),
    )
    model_D_minus = RooAddPdf(
        f"model_D_minus_{tag}",
        "D- model",
        ROOT.RooArgList(sig_model, model_bkg),
        ROOT.RooArgList(Nsig_D_minus, Nbkg_D_minus),
    )

    params = {
        "N_total": N_total,
        "Acp": Acp,
        "Nbkg_total": Nbkg_total,
        "Acp_bkg": Acp_bkg,
        "mean": mean,
        "sigma": sigma,
        "gamma": gamma,
        "delta": delta,
        "sigma_gauss": sigma_gauss,
        "x_bkg1_tau": x_bkg1_tau,
    }

    keep = [
        N_total, Acp, Nsig_D_plus, Nsig_D_minus, Nbkg_total, Acp_bkg, Nbkg_D_plus, Nbkg_D_minus,
        mean, sigma, gamma, delta, johnson, mean_gauss, sigma_gauss, gauss, sig_model,
        x_bkg1_tau, model_bkg, model_D_plus, model_D_minus,
    ]

    return {
        "tag": tag,
        "params": params,
        "model_D_plus": model_D_plus,
        "model_D_minus": model_D_minus,
        "model_bkg": model_bkg,
        "sig_model": sig_model,
        "Nsig_D_plus": Nsig_D_plus,
        "Nsig_D_minus": Nsig_D_minus,
        "Nbkg_D_plus": Nbkg_D_plus,
        "Nbkg_D_minus": Nbkg_D_minus,
        "keep": keep,
    }


def get_fit_result(path, object_name):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise RuntimeError(f"Cannot open fit result file: {path}")
    fit_result = f.Get(object_name)
    if not fit_result:
        raise RuntimeError(f"Cannot find RooFitResult '{object_name}' in {path}")
    fit_result.SetName(f"{object_name}_{os.path.basename(path)}")
    return f, fit_result


def find_par(pars, name):
    obj = pars.find(name)
    if obj:
        return obj
    for i in range(pars.getSize()):
        p = pars.at(i)
        if p.GetName() == name:
            return p
    return None


def apply_params(model_info, pars):
    for base_name, var in model_info["params"].items():
        p = find_par(pars, base_name)
        if p:
            var.setVal(p.getVal())
            if hasattr(p, "getError"):
                var.setError(p.getError())
        else:
            print(f"[warning] parameter {base_name} not found in fit result for {model_info['tag']}")


f_plus, fitres_plus = get_fit_result(fitresult_name_plus, args.fit_object_name)
f_minus, fitres_minus = get_fit_result(fitresult_name_minus, args.fit_object_name)

model_sp = build_model("signPlus")
model_sm = build_model("signMinus")
apply_params(model_sp, fitres_plus.floatParsFinal())
apply_params(model_sm, fitres_minus.floatParsFinal())

print("Loaded fit results:")
print("  plus  status/covQual:", fitres_plus.status(), fitres_plus.covQual())
print("  minus status/covQual:", fitres_minus.status(), fitres_minus.covQual())

# -----------------------------------------------------------------------------
# Histogram helpers
# -----------------------------------------------------------------------------
def hist_from_data(data, name, nbins):
    h = data.createHistogram(name, x, RooFit.Binning(nbins))
    h.SetDirectory(0)
    #h.Sumw2()
    return h

h_sp_Dp = hist_from_data(data_sp_Dp, "h_sp_Dp", args.nbins)
h_sp_Dm = hist_from_data(data_sp_Dm, "h_sp_Dm", args.nbins)
h_sm_Dp = hist_from_data(data_sm_Dp, "h_sm_Dp", args.nbins)
h_sm_Dm = hist_from_data(data_sm_Dm, "h_sm_Dm", args.nbins)

h_data_all = h_sp_Dp.Clone("h_data_all")
h_data_all.SetDirectory(0)
h_data_all.Add(h_sp_Dm)
h_data_all.Add(h_sm_Dp)
h_data_all.Add(h_sm_Dm)


def make_asym_hist(hp, hm, name):
    h = hp.Clone(name)
    h.SetDirectory(0)
    h.Reset("ICES") #to reset
    for ibin in range(1, hp.GetNbinsX() + 1):
        n_p = hp.GetBinContent(ibin)
        n_m = hm.GetBinContent(ibin)
        total = n_p + n_m
        if total > 0:
            asym = (n_p - n_m) / total
            err = math.sqrt(max(0.0, 1.0 - asym * asym) / total)
            h.SetBinContent(ibin, asym)
            h.SetBinError(ibin, err)
        else:
            h.SetBinContent(ibin, 0.0)
            h.SetBinError(ibin, 0.0)
    return h


def make_avg_asym_hist(hA_plusSign, hA_minusSign, name):
    h = hA_plusSign.Clone(name)
    h.SetDirectory(0)
    h.Reset("ICES") #to reset
    for ibin in range(1, h.GetNbinsX() + 1):
        a1 = hA_plusSign.GetBinContent(ibin)
        e1 = hA_plusSign.GetBinError(ibin)
        a2 = hA_minusSign.GetBinContent(ibin)
        e2 = hA_minusSign.GetBinError(ibin)
        h.SetBinContent(ibin, 0.5 * (a1 + a2))
        h.SetBinError(ibin, 0.5 * math.sqrt(e1 * e1 + e2 * e2))
    return h

hA_sp = make_asym_hist(h_sp_Dp, h_sp_Dm, "hA_signPlus")
hA_sm = make_asym_hist(h_sm_Dp, h_sm_Dm, "hA_signMinus")
hA_avg = make_avg_asym_hist(hA_sp, hA_sm, "hA_avg")

# -----------------------------------------------------------------------------
# Curve helpers: central curves only.
# -----------------------------------------------------------------------------
normset = ROOT.RooArgSet(x)


def eval_model_y(model_info, charge_name, mass, bin_width=1.0, component="total"):
    x.setVal(mass)
    if charge_name == "D_plus":
        model = model_info["model_D_plus"]
        nbkg = model_info["Nbkg_D_plus"]
    elif charge_name == "D_minus":
        model = model_info["model_D_minus"]
        nbkg = model_info["Nbkg_D_minus"]
    else:
        raise ValueError(charge_name)

    if component == "total":
        return model.expectedEvents(normset) * model.getVal(normset) * bin_width
    if component == "bkg":
        return nbkg.getVal() * model_info["model_bkg"].getVal(normset) * bin_width
    raise ValueError(component)


def eval_total_fit_y(mass, bin_width):
    y = 0.0
    for model_info in [model_sp, model_sm]:
        y += eval_model_y(model_info, "D_plus", mass, bin_width, "total")
        y += eval_model_y(model_info, "D_minus", mass, bin_width, "total")
    return y


def eval_total_bkg_y(mass, bin_width):
    y = 0.0
    for model_info in [model_sp, model_sm]:
        y += eval_model_y(model_info, "D_plus", mass, bin_width, "bkg")
        y += eval_model_y(model_info, "D_minus", mass, bin_width, "bkg")
    return y


def eval_sign_asym(model_info, mass):
    yp = eval_model_y(model_info, "D_plus", mass, 1.0, "total")
    ym = eval_model_y(model_info, "D_minus", mass, 1.0, "total")
    if yp + ym <= 0:
        return 0.0
    return (yp - ym) / (yp + ym)


def eval_avg_asym(mass):
    return 0.5 * (eval_sign_asym(model_sp, mass) + eval_sign_asym(model_sm, mass))


def make_line_graph(name, xvals, yvals):
    g = ROOT.TGraph(len(xvals))
    g.SetName(name)
    for i, (xx, yy) in enumerate(zip(xvals, yvals)):
        g.SetPoint(i, xx, yy)
    return g


def make_fill_graph_to_zero(name, xvals, yvals):
    g = ROOT.TGraph(len(xvals) + 2)
    g.SetName(name)
    g.SetPoint(0, xvals[0], 0.0)
    for i, (xx, yy) in enumerate(zip(xvals, yvals), start=1):
        g.SetPoint(i, xx, yy)
    g.SetPoint(len(xvals) + 1, xvals[-1], 0.0)
    return g

xmin, xmax = fit_range
bin_width = (xmax - xmin) / args.nbins
xvals = [xmin + (xmax - xmin) * i / (args.n_curve_points - 1) for i in range(args.n_curve_points)]
y_fit = [eval_total_fit_y(xx, bin_width) for xx in xvals]
y_bkg = [eval_total_bkg_y(xx, bin_width) for xx in xvals]
y_asym = [eval_avg_asym(xx) for xx in xvals]

# -----------------------------------------------------------------------------
# Plot
# -----------------------------------------------------------------------------
def add_lumi_prelim(canvas, lumi_fb=428, is_preliminary=True):
    canvas.cd(1)
    pos_x = 0.78
    top_y = 0.90
    line_spacing = 0.05

    header = "#font[62]{Belle II}"
    if is_preliminary:
        left_text = f"#splitline{{{header}}}{{#font[52]{{Preliminary}}}}"
        lumi_y = top_y - (line_spacing * 2.2)
    else:
        left_text = header
        lumi_y = top_y - (line_spacing * 1.2)

    latex_left = ROOT.TLatex()
    latex_left.SetNDC(True)
    latex_left.SetTextSize(0.042)
    latex_left.SetTextAlign(13)
    latex_left.DrawLatex(pos_x, top_y, left_text)

    latex_right = ROOT.TLatex()
    latex_right.SetNDC(True)
    latex_right.SetTextSize(0.042)
    latex_right.SetTextAlign(13)
    latex_right.DrawLatex(pos_x, lumi_y, f"#int L dt = {lumi_fb} fb^{{-1}}")

    if not hasattr(canvas, "_labels"):
        canvas._labels = []
    canvas._labels.extend([latex_left, latex_right])

canvas = ROOT.TCanvas("canvas_D_all", "D+ fit", 800, 600)
xlow = ctypes.c_double()
ylow = ctypes.c_double()
xup = ctypes.c_double()
yup = ctypes.c_double()
canvas.GetPad(0).GetPadPar(xlow, ylow, xup, yup)
canvas.Divide(1, 2)

xlow = xlow.value
ylow = ylow.value
xup = xup.value
yup = yup.value

upPad = canvas.GetPad(1)
upPad.SetPad(xlow, ylow + 0.25 * (yup - ylow), xup, yup)

dwPad = canvas.GetPad(2)
dwPad.SetPad(xlow, ylow, xup, ylow + 0.25 * (yup - ylow))

canvas.cd(1)

h_data_all.SetStats(0)
h_data_all.SetTitle("")
h_data_all.GetXaxis().SetTitle(fit_var_name)
h_data_all.GetXaxis().CenterTitle(True)
h_data_all.GetXaxis().SetTitleSize(0.06)
h_data_all.GetXaxis().SetTitleOffset(1.2)

#max_y = max(h_data_all.GetMaximum(), max(y_fit) if y_fit else 0.0)
#h_data_all.SetMaximum(1.25 * max_y)
#h_data_all.SetMinimum(0.0)

h_data_all.SetMarkerStyle(20)
h_data_all.SetMarkerSize(0.8)
h_data_all.Draw("PE")

g_bkg = make_fill_graph_to_zero("g_bkg_sum", xvals, y_bkg)
g_bkg.SetFillColor(ROOT.kGray)
g_bkg.SetLineColor(ROOT.kGray)
g_bkg.Draw("F SAME")

g_fit = make_line_graph("g_fit_sum", xvals, y_fit)
g_fit.SetLineColor(ROOT.kBlue)
g_fit.SetLineWidth(2)
g_fit.Draw("L SAME")

h_data_all.Draw("PE SAME")

leg1 = ROOT.TLegend(0.2, 0.65, 0.4, 0.90)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)
leg1.SetBorderSize(0)
leg1.AddEntry(h_data_all, "#font[42]{Data}", "PE")
leg1.AddEntry(g_fit, "#font[42]{Fit}", "l")
leg1.AddEntry(g_bkg, "#font[42]{Background}", "f")
leg1.Draw()

canvas.cd(2)

hA_avg.SetStats(0)
hA_avg.SetTitle("")
hA_avg.SetMarkerStyle(20)
hA_avg.SetMarkerSize(0.8)
hA_avg.SetYTitle("Asymmetry")
hA_avg.SetMinimum(-0.3)
hA_avg.SetMaximum(0.3)
hA_avg.GetYaxis().SetTitleSize(0.12)
hA_avg.GetYaxis().SetTitleOffset(0.4)
hA_avg.GetYaxis().SetLabelSize(0.08)
hA_avg.GetYaxis().CenterTitle(True)
hA_avg.GetXaxis().SetTitle(fit_var_name)
hA_avg.GetXaxis().SetLabelSize(0.15)
hA_avg.GetXaxis().SetTitleSize(0)
hA_avg.GetXaxis().CenterTitle(True)
hA_avg.Draw("PE")

g_asym = make_line_graph("g_asym_avg", xvals, y_asym)
g_asym.SetLineColor(ROOT.kBlue)
g_asym.SetLineWidth(2)
g_asym.Draw("L SAME")

line_zero = ROOT.TLine(fit_range[0], 0.0, fit_range[1], 0.0)
line_zero.SetLineStyle(2)
line_zero.SetLineWidth(2)
line_zero.SetLineColor(ROOT.kRed)
line_zero.Draw("SAME")

canvas.Update()
add_lumi_prelim(canvas, lumi_fb=428)
canvas.Update()
canvas.SaveAs(file_name_out)
print(f"Saved: {file_name_out}")

_ = (f_plus, f_minus)
