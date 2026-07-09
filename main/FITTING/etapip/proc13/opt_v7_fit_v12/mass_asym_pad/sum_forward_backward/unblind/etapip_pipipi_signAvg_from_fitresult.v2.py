import ROOT
from ROOT import RooFit, RooRealVar, RooDataSet, RooArgList, RooAddPdf, RooFormulaVar
import glob
import ctypes
import os
import argparse
import math
import random

ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser(
    description=(
        "Plot combined sign-plus/sign-minus result for etapip_pipipi using existing "
        "RooFitResult files. No refit is performed. The lower-pad asymmetry is "
        "0.5*(A_raw(sign plus) + A_raw(sign minus))."
    )
)
parser.add_argument("-t", "--train", required=True, help="Specify train version, same as in the fit scripts")
parser.add_argument("-b", "--bdt", required=True, help="Specify BDT value, same as in the fit scripts")
parser.add_argument("--nbins", type=int, default=200, help="Number of bins for data histograms")
parser.add_argument("--n-curve-points", type=int, default=500, help="Number of points used for smooth fitted curves")
parser.add_argument("--fit-object-name", default="jykim", help="Object name of RooFitResult saved in the fit-result ROOT files")
parser.add_argument(
    "--suffix",
    default="sumw2fixed_pdf_fixed_unblind",
    help="Suffix used in the original etapip_pipipi fit-result filenames",
)
parser.add_argument("--output", default="", help="Output PDF path. If empty, use the default /share/storage/... path")
parser.add_argument(
    "--no-blind",
    action="store_true",
    help="Do not hide the lower-pad asymmetry in the original etapip_pipipi blinding window",
)
args = parser.parse_args()

# -----------------------------------------------------------------------------
# Configuration: keep the paths and names consistent with etapip_pipipi_offset_CB.py.
# -----------------------------------------------------------------------------
BDT_cut = str(args.bdt)
suffix = args.suffix
base_plot_dir = "/share/storage/jykim/plots/proc_all/etapip/pipipi/generic"
base_fit_dir = f"{base_plot_dir}/fitresult"

fitresult_name_plus = (
    f"{base_fit_dir}/proc13_etapip_pipipi_fit_opt_loose_v7_fitv12_bdt_"
    f"{args.train}_plus_{BDT_cut}_{suffix}.root"
)
fitresult_name_minus = (
    f"{base_fit_dir}/proc13_etapip_pipipi_fit_opt_loose_v7_fitv12_bdt_"
    f"{args.train}_minus_{BDT_cut}_{suffix}.root"
)

if args.output:
    file_name_out = args.output
else:
    file_name_out = (
        f"{base_plot_dir}/proc13_etapip_pipipi_fit_opt_loose_v7_fitv12_bdt_"
        f"{args.train}_Dall_CMS_signAvg_{BDT_cut}_{suffix}.pdf"
    )

for path in [file_name_out, fitresult_name_plus, fitresult_name_minus]:
    print(path)

out_dir = os.path.dirname(file_name_out)
if out_dir and not os.path.exists(out_dir):
    os.makedirs(out_dir)

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

# Input ntuples: same logic as the original etapip_pipipi fit script.
base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/proc13/proc13_EtaHp_loose_v7"
cm_elements = [
    "jae_13_had_4S_off_v1",
    "jae_13_had_4S_v3",
    "jae_23_had_4S_off_v1",
    "jae_23_had_4S_v1",
    "jae_23_had_5Sscan_10657_v1",
    "jae_23_had_5Sscan_10706_v1",
    "jae_23_had_5Sscan_10751_v1",
    "jae_23_had_5Sscan_10810_v1",
]

tree_name = "etapip_pipipi"
file_list = []
for element in cm_elements:
    pattern = f"{base_path}/{element}/{tree_name}/min_unc_search/{BDT_cut}/*BDT.root"
    file_list += glob.glob(pattern)

print(file_list)
print(f"Number of files: {len(file_list)}")

mychain = ROOT.TChain(tree_name)
for fname in file_list:
    mychain.Add(fname)

# -----------------------------------------------------------------------------
# Observable and variables.
# -----------------------------------------------------------------------------
fit_variable = "Dp_M"
fit_var_name = "M(#eta_{3#pi}#pi^{+}) [GeV/c^{2}]"
fit_range = (1.71, 2.06)
charge_var = "Pip_charge"

x = ROOT.RooRealVar(fit_variable, fit_var_name, fit_range[0], fit_range[1])
x.setBins(200)
Pip_charge = ROOT.RooRealVar(charge_var, charge_var, -1, 1)
Dp_CMS_cosTheta = ROOT.RooRealVar("Dp_CMS_cosTheta", "Dp_CMS_cosTheta", -1, 1)
BDT = ROOT.RooRealVar("BDT", "BDT", 0, 1)
Pip_dr = ROOT.RooRealVar("Pip_dr", "Pip_dr", -10000, 10000)
Dp_dz = ROOT.RooRealVar("Dp_dz", "Dp_dz", -10000, 10000)
Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane = ROOT.RooRealVar(
    "Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane",
    "Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane",
    -1,
    1,
)
Dp_cosHelicityAngleMomentum = ROOT.RooRealVar(
    "Dp_cosHelicityAngleMomentum", "Dp_cosHelicityAngleMomentum", -1, 1
)
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
    Dp_cosHelicityAngleMomentum,
    Dp_CMS_p,
    rank_Dp_chiProb,
)

# -----------------------------------------------------------------------------
# Data import: four samples are built explicitly, then the lower-pad asymmetry is
# averaged over sign plus/minus.
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
# Shape inputs from MC/control fits: same external ROOT files as the original fit.
# -----------------------------------------------------------------------------
def open_fit_result(path, object_name="jykim"):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise RuntimeError(f"Cannot open ROOT file: {path}")
    obj = f.Get(object_name)
    if not obj:
        raise RuntimeError(f"Cannot find object '{object_name}' in {path}")
    return f, obj


f_sig, result_object_sig = open_fit_result(
    "/share/storage/jykim/plots/MC15rd/etapip/pipipi/"
    "MC15rd_6M_etapip_pipipi_Dp_M_v12_CB_conv_result_extended_train_Dp_CMS_p.0.72.root"
)
fit_args_sig = result_object_sig.floatParsFinal()

f_sig_Ds, result_object_sig_Ds = open_fit_result(
    "/share/storage/jykim/plots/MC15rd/etapip/pipipi/"
    "MC15rd_6M_etapip_pipipi_Dp_M_v12_CB_conv_result_extended_train_Dp_CMS_p_Ds_p.0.72.weighted.root"
)
fit_args_sig_Ds = result_object_sig_Ds.floatParsFinal()

f_rhopeta, result_object_rhopeta = open_fit_result(
    "/share/storage/jykim/plots/MC15rd/etapip/pipipi/"
    "MC15rd_etapip_pipipi_Dp_M_fit_v12_novo_result_rhopeta_Dp_CMS_p_0.72.root"
)
fit_args_rhopeta = result_object_rhopeta.floatParsFinal()


def must_find(pars, name):
    obj = pars.find(name)
    if not obj:
        raise RuntimeError(f"Cannot find parameter '{name}'")
    return obj


mc = {
    "sigmaL": must_find(fit_args_sig, "sigmaL").getVal(),
    "sigmaR": must_find(fit_args_sig, "sigmaR").getVal(),
    "alphaL": must_find(fit_args_sig, "alphaL").getVal(),
    "nL": must_find(fit_args_sig, "nL").getVal(),
    "alphaR": must_find(fit_args_sig, "alphaR").getVal(),
    "nR": must_find(fit_args_sig, "nR").getVal(),
    "sigma_gaussian": must_find(fit_args_sig, "sigma_gaussian").getVal(),
    "Ds_sigmaL": must_find(fit_args_sig_Ds, "sigmaL").getVal(),
    "Ds_sigmaR": must_find(fit_args_sig_Ds, "sigmaR").getVal(),
    "Ds_alphaL": must_find(fit_args_sig_Ds, "alphaL").getVal(),
    "Ds_nL": must_find(fit_args_sig_Ds, "nL").getVal(),
    "Ds_alphaR": must_find(fit_args_sig_Ds, "alphaR").getVal(),
    "Ds_nR": must_find(fit_args_sig_Ds, "nR").getVal(),
    "Ds_sigma_gaussian": must_find(fit_args_sig_Ds, "sigma_gaussian").getVal(),
    "novo_sigma": must_find(fit_args_rhopeta, "sigma").getVal(),
    "novo_tail": must_find(fit_args_rhopeta, "tail").getVal(),
}

# -----------------------------------------------------------------------------
# Model definition: same PDF structure as etapip_pipipi_offset_CB.py, but tagged so
# that sign-plus and sign-minus fit results can coexist in memory.
# -----------------------------------------------------------------------------
scale = 1 / 4


def build_model(tag):
    N_total = RooRealVar(f"N_total_{tag}", "N_total", 60000 * scale, 30000 * scale, 400000 * scale)
    Acp = RooRealVar(f"Acp_{tag}", "Acp", 0, -1, 1)

    Nsig_D_plus = RooFormulaVar(
        f"Nsig_D_plus_{tag}", "0.5*@0*(1+@1)", RooArgList(N_total, Acp)
    )
    Nsig_D_minus = RooFormulaVar(
        f"Nsig_D_minus_{tag}", "0.5*@0*(1-@1)", RooArgList(N_total, Acp)
    )

    N_total_Ds = RooRealVar(
        f"N_total_Ds_{tag}", "N_total_Ds", 140000 * scale, 50000 * scale, 300000 * scale
    )
    Acp_Ds = RooRealVar(f"Acp_Ds_{tag}", "Acp_Ds", 0, -1, 1)

    Nsig_Ds_plus = RooFormulaVar(
        f"Nsig_Ds_plus_{tag}", "0.5*@0*(1+@1)", RooArgList(N_total_Ds, Acp_Ds)
    )
    Nsig_Ds_minus = RooFormulaVar(
        f"Nsig_Ds_minus_{tag}", "0.5*@0*(1-@1)", RooArgList(N_total_Ds, Acp_Ds)
    )

    Nbkg_total = RooRealVar(
        f"Nbkg_total_{tag}", "Nbkg_total", 250000 * scale, 20000 * scale, 500000 * scale
    )
    Acp_bkg = RooRealVar(f"Acp_bkg_{tag}", "Acp_bkg", 0, -0.5, 0.5)
    Nbkg_D_plus = RooFormulaVar(
        f"Nbkg_D_plus_{tag}", "0.5*@0*(1+@1)", RooArgList(Nbkg_total, Acp_bkg)
    )
    Nbkg_D_minus = RooFormulaVar(
        f"Nbkg_D_minus_{tag}", "0.5*@0*(1-@1)", RooArgList(Nbkg_total, Acp_bkg)
    )

    mean = ROOT.RooRealVar(f"mean_{tag}", "mean", 1.87, 1.85, 1.89)
    sigmaL = ROOT.RooRealVar(f"sigmaL_{tag}", "sigmaL", mc["sigmaL"])
    sigmaR = ROOT.RooRealVar(f"sigmaR_{tag}", "sigmaR", mc["sigmaR"])
    alphaL = ROOT.RooRealVar(f"alphaL_{tag}", "alphaL", mc["alphaL"])
    nL = ROOT.RooRealVar(f"nL_{tag}", "nL", mc["nL"])
    alphaR = ROOT.RooRealVar(f"alphaR_{tag}", "alphaR", mc["alphaR"])
    nR = ROOT.RooRealVar(f"nR_{tag}", "nR", mc["nR"])
    sigma_gaussian = ROOT.RooRealVar(
        f"sigma_gaussian_{tag}", "sigma_gaussian", mc["sigma_gaussian"], 0.001, 0.1
    )

    CB = ROOT.RooCrystalBall(
        f"CB_{tag}", "CB", x, mean, sigmaL, sigmaR, alphaL, nL, alphaR, nR
    )
    mean_gaussian = ROOT.RooRealVar(f"mean_gaussian_{tag}", "mean_gaussian", 0)
    gaussian = ROOT.RooGaussian(f"gaussian_{tag}", "Gaussian PDF", x, mean_gaussian, sigma_gaussian)
    sig_model = ROOT.RooFFTConvPdf(
        f"sig_model_{tag}", "CB #otimes Gaussian", x, CB, gaussian
    )

    Ds_mean = ROOT.RooRealVar(f"Ds_mean_{tag}", "Ds_mean", 1.97, 1.95, 1.99)
    Ds_sigmaL = ROOT.RooRealVar(f"Ds_sigmaL_{tag}", "Ds_sigmaL", mc["Ds_sigmaL"])
    Ds_sigmaR = ROOT.RooRealVar(f"Ds_sigmaR_{tag}", "Ds_sigmaR", mc["Ds_sigmaR"])
    Ds_alphaL = ROOT.RooRealVar(f"Ds_alphaL_{tag}", "Ds_alphaL", mc["Ds_alphaL"])
    Ds_nL = ROOT.RooRealVar(f"Ds_nL_{tag}", "Ds_nL", mc["Ds_nL"])
    Ds_alphaR = ROOT.RooRealVar(f"Ds_alphaR_{tag}", "Ds_alphaR", mc["Ds_alphaR"])
    Ds_nR = ROOT.RooRealVar(f"Ds_nR_{tag}", "Ds_nR", mc["Ds_nR"])
    Ds_sigma_gaussian = ROOT.RooRealVar(
        f"Ds_sigma_gaussian_{tag}", "Ds_sigma_gaussian", mc["Ds_sigma_gaussian"], 0.001, 0.1
    )

    Ds_CB = ROOT.RooCrystalBall(
        f"Ds_CB_{tag}", "Ds_CB", x, Ds_mean, Ds_sigmaL, Ds_sigmaR, Ds_alphaL, Ds_nL, Ds_alphaR, Ds_nR
    )
    Ds_mean_gaussian = ROOT.RooRealVar(f"Ds_mean_gaussian_{tag}", "Ds_mean_gaussian", 0)
    Ds_gaussian = ROOT.RooGaussian(
        f"Ds_gaussian_{tag}", "Gaussian PDF", x, Ds_mean_gaussian, Ds_sigma_gaussian
    )
    Ds_model = ROOT.RooFFTConvPdf(
        f"Ds_model_{tag}", "Ds CB #otimes Gaussian", x, Ds_CB, Ds_gaussian
    )

    novo_mean = ROOT.RooRealVar(f"novo_mean_{tag}", "novo_mean", 1.73, 1.71, 1.745)
    novo_sigma = ROOT.RooRealVar(f"novo_sigma_{tag}", "novo_sigma", mc["novo_sigma"])
    novo_tail = ROOT.RooRealVar(f"novo_tail_{tag}", "novo_tail", mc["novo_tail"])
    rhopeta = ROOT.RooNovosibirsk(
        f"rhopeta_{tag}", "Novosibirsk PDF", x, novo_mean, novo_sigma, novo_tail
    )

    x_bkg1_tau = ROOT.RooRealVar(f"x_bkg1_tau_{tag}", "x_bkg1_tau", -3, -8, -0.01)
    bkg_comb = ROOT.RooExponential(f"bkg_comb_{tag}", "combinatorial", x, x_bkg1_tau)
    bkg_frac = ROOT.RooRealVar(f"bkg_frac_{tag}", "bkg_frac", 0.3, 0.01, 1)
    model_bkg = ROOT.RooAddPdf(
        f"model_bkg_{tag}", "rho eta + comb", RooArgList(rhopeta, bkg_comb), bkg_frac
    )

    model_D_plus = RooAddPdf(
        f"model_D_plus_{tag}",
        "D+ model",
        ROOT.RooArgList(sig_model, Ds_model, model_bkg),
        ROOT.RooArgList(Nsig_D_plus, Nsig_Ds_plus, Nbkg_D_plus),
    )
    model_D_minus = RooAddPdf(
        f"model_D_minus_{tag}",
        "D- model",
        ROOT.RooArgList(sig_model, Ds_model, model_bkg),
        ROOT.RooArgList(Nsig_D_minus, Nsig_Ds_minus, Nbkg_D_minus),
    )

    params = {
        "N_total": N_total,
        "Acp": Acp,
        "N_total_Ds": N_total_Ds,
        "Acp_Ds": Acp_Ds,
        "Nbkg_total": Nbkg_total,
        "Acp_bkg": Acp_bkg,
        "mean": mean,
        "sigmaL": sigmaL,
        "sigmaR": sigmaR,
        "alphaL": alphaL,
        "nL": nL,
        "alphaR": alphaR,
        "nR": nR,
        "sigma_gaussian": sigma_gaussian,
        "Ds_mean": Ds_mean,
        "Ds_sigmaL": Ds_sigmaL,
        "Ds_sigmaR": Ds_sigmaR,
        "Ds_alphaL": Ds_alphaL,
        "Ds_nL": Ds_nL,
        "Ds_alphaR": Ds_alphaR,
        "Ds_nR": Ds_nR,
        "Ds_sigma_gaussian": Ds_sigma_gaussian,
        "novo_mean": novo_mean,
        "novo_sigma": novo_sigma,
        "novo_tail": novo_tail,
        "x_bkg1_tau": x_bkg1_tau,
        "bkg_frac": bkg_frac,
    }

    keep = [
        N_total,
        Acp,
        Nsig_D_plus,
        Nsig_D_minus,
        N_total_Ds,
        Acp_Ds,
        Nsig_Ds_plus,
        Nsig_Ds_minus,
        Nbkg_total,
        Acp_bkg,
        Nbkg_D_plus,
        Nbkg_D_minus,
        mean,
        sigmaL,
        sigmaR,
        alphaL,
        nL,
        alphaR,
        nR,
        sigma_gaussian,
        CB,
        mean_gaussian,
        gaussian,
        sig_model,
        Ds_mean,
        Ds_sigmaL,
        Ds_sigmaR,
        Ds_alphaL,
        Ds_nL,
        Ds_alphaR,
        Ds_nR,
        Ds_sigma_gaussian,
        Ds_CB,
        Ds_mean_gaussian,
        Ds_gaussian,
        Ds_model,
        novo_mean,
        novo_sigma,
        novo_tail,
        rhopeta,
        x_bkg1_tau,
        bkg_comb,
        bkg_frac,
        model_bkg,
        model_D_plus,
        model_D_minus,
    ]

    return {
        "tag": tag,
        "params": params,
        "model_D_plus": model_D_plus,
        "model_D_minus": model_D_minus,
        "model_bkg": model_bkg,
        "bkg_comb": bkg_comb,
        "rhopeta": rhopeta,
        "bkg_frac": bkg_frac,
        "Nsig_D_plus": Nsig_D_plus,
        "Nsig_D_minus": Nsig_D_minus,
        "Nsig_Ds_plus": Nsig_Ds_plus,
        "Nsig_Ds_minus": Nsig_Ds_minus,
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


# Parameters that were intentionally fixed in etapip_pipipi_offset_CB.py.
# They are initialized above from the external MC/control fit-result files and
# therefore do not have to appear in floatParsFinal() of the data fit result.
FIXED_FROM_EXTERNAL_SHAPE = {
    "sigmaL",
    "sigmaR",
    "alphaL",
    "nL",
    "alphaR",
    "nR",
    "Ds_sigmaL",
    "Ds_sigmaR",
    "Ds_alphaL",
    "Ds_nL",
    "Ds_alphaR",
    "Ds_nR",
    "novo_sigma",
    "novo_tail",
}

# These should normally be present in the data RooFitResult, because they were
# floating parameters in the original simultaneous fit.
EXPECTED_DATA_FIT_PARAMS = {
    "N_total",
    "Acp",
    "N_total_Ds",
    "Acp_Ds",
    "Nbkg_total",
    "Acp_bkg",
    "mean",
    "sigma_gaussian",
    "Ds_mean",
    "Ds_sigma_gaussian",
    "novo_mean",
    "x_bkg1_tau",
    "bkg_frac",
}


def find_par_in_fit_result(fit_result, name):
    """Return a parameter from floatParsFinal() or constPars(), if available.

    Important: RooFitResult.floatParsFinal() contains only parameters that floated
    in the fit. Parameters fixed in the original fit may instead appear in
    RooFitResult.constPars(), or may be absent if they came from external MC/control
    shape fits.
    """
    # 1) Floating parameters from the data fit.
    float_pars = fit_result.floatParsFinal()
    p = find_par(float_pars, name)
    if p:
        return p, "floatParsFinal"

    # 2) Constant parameters saved in the RooFitResult.
    # Use try/except rather than hasattr, because PyROOT method lookup can be odd
    # in some environments.
    try:
        const_pars = fit_result.constPars()
    except Exception:
        const_pars = None

    if const_pars:
        p = find_par(const_pars, name)
        if p:
            return p, "constPars"

    # 3) Not stored in this data fit result. For external fixed-shape parameters,
    # apply_params() will keep the values initialized from MC/control fit files.
    return None, None


def apply_params(model_info, fit_result):
    kept_external = []
    applied_float = []
    applied_const = []
    missing_expected = []

    for base_name, var in model_info["params"].items():
        p, source = find_par_in_fit_result(fit_result, base_name)

        if p:
            var.setVal(p.getVal())
            if hasattr(p, "getError"):
                var.setError(p.getError())
            if source == "floatParsFinal":
                applied_float.append(base_name)
            elif source == "constPars":
                applied_const.append(base_name)
            else:
                applied_const.append(base_name)
            continue

        if base_name in FIXED_FROM_EXTERNAL_SHAPE:
            kept_external.append(base_name)
            continue

        # For robustness, do not stop plotting if an expected parameter is absent,
        # but make this explicit because the curve may not match the data fit.
        if base_name in EXPECTED_DATA_FIT_PARAMS:
            missing_expected.append(base_name)
        else:
            print(f"#########################")
            print(f"[info] parameter {base_name} not found for {model_info['tag']}; keeping initialized value")

    print(f"[{model_info['tag']}] applied parameters from floatParsFinal(): {', '.join(applied_float) if applied_float else 'none'}")
    if applied_const:
        print(f"[{model_info['tag']}] applied parameters from constPars(): {', '.join(applied_const)}")
    if kept_external:
        print(
            f"[{model_info['tag']}] kept externally fixed shape parameters from MC/control fits: "
            f"{', '.join(kept_external)}"
        )
    if missing_expected:
        print(
            f"[warning] expected floating parameters missing for {model_info['tag']}: "
            f"{', '.join(missing_expected)}"
        )


f_plus, fitres_plus = get_fit_result(fitresult_name_plus, args.fit_object_name)
f_minus, fitres_minus = get_fit_result(fitresult_name_minus, args.fit_object_name)

model_sp = build_model("signPlus")
model_sm = build_model("signMinus")
apply_params(model_sp, fitres_plus)
apply_params(model_sm, fitres_minus)

print("Loaded fit results:")
print("  plus  status/covQual:", fitres_plus.status(), fitres_plus.covQual())
print("  minus status/covQual:", fitres_minus.status(), fitres_minus.covQual())

# -----------------------------------------------------------------------------
# Histogram helpers.
# -----------------------------------------------------------------------------
def hist_from_data(data, name, nbins):
    h = data.createHistogram(name, x, RooFit.Binning(nbins))
    h.SetDirectory(0)
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
    h.Reset("ICES")
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
    h.Reset("ICES")
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

# Preserve the original etapip_pipipi blinding of the lower-pad asymmetry by default.
if not args.no_blind:
    blind_min = 1.81
    blind_max = 2.02
    for ibin in range(1, hA_avg.GetNbinsX() + 1):
        bin_center = hA_avg.GetBinCenter(ibin)
        if blind_min <= bin_center <= blind_max:
            hA_avg.SetBinContent(ibin, 0.0)
            hA_avg.SetBinError(ibin, 0.0)

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
    if component == "comb":
        return (
            nbkg.getVal()
            * (1.0 - model_info["bkg_frac"].getVal())
            * model_info["bkg_comb"].getVal(normset)
            * bin_width
        )
    if component == "rhopeta":
        return (
            nbkg.getVal()
            * model_info["bkg_frac"].getVal()
            * model_info["rhopeta"].getVal(normset)
            * bin_width
        )
    raise ValueError(component)


def eval_sum_y(mass, bin_width, component="total"):
    y = 0.0
    for model_info in [model_sp, model_sm]:
        y += eval_model_y(model_info, "D_plus", mass, bin_width, component)
        y += eval_model_y(model_info, "D_minus", mass, bin_width, component)
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


def make_band_graph(name, xvals, ylow, yhigh):
    g = ROOT.TGraph(2 * len(xvals))
    g.SetName(name)
    for i, (xx, yy) in enumerate(zip(xvals, yhigh)):
        g.SetPoint(i, xx, yy)
    for j, (xx, yy) in enumerate(zip(reversed(xvals), reversed(ylow)), start=len(xvals)):
        g.SetPoint(j, xx, yy)
    return g


xmin, xmax = fit_range
bin_width = (xmax - xmin) / args.nbins
xvals = [xmin + (xmax - xmin) * i / (args.n_curve_points - 1) for i in range(args.n_curve_points)]
y_fit = [eval_sum_y(xx, bin_width, "total") for xx in xvals]
y_comb = [eval_sum_y(xx, bin_width, "comb") for xx in xvals]
y_rhopeta = [eval_sum_y(xx, bin_width, "rhopeta") for xx in xvals]
y_bkg_total = [a + b for a, b in zip(y_comb, y_rhopeta)]
y_asym = [eval_avg_asym(xx) for xx in xvals]

if not args.no_blind:
    y_asym = [0.0 if 1.81 <= xx <= 2.02 else yy for xx, yy in zip(xvals, y_asym)]

# -----------------------------------------------------------------------------
# Plot.
# -----------------------------------------------------------------------------
def add_lumi_prelim(canvas, lumi_fb=428, is_preliminary=True):
    canvas.cd(1)
    pos_x = 0.79
    top_y = 0.90
    line_spacing = 0.05

    #header = "#font[62]{Belle II}"
    header = "#font[42]{Belle II}"
    if is_preliminary:
        left_text = f"#splitline{{{header}}}{{#font[42]{{Preliminary}}}}"
        lumi_y = top_y - (line_spacing * 2.2)
    else:
        left_text = header
        lumi_y = top_y - (line_spacing * 1.2)

    latex_left = ROOT.TLatex()
    latex_left.SetNDC(True)
    latex_left.SetTextSize(FONT_SIZE_UP)
    latex_left.SetTextAlign(13)
    latex_left.DrawLatex(pos_x, top_y, left_text)

    latex_right = ROOT.TLatex()
    latex_right.SetNDC(True)
    latex_right.SetTextSize(FONT_SIZE_UP)
    latex_right.SetTextAlign(13)
    #latex_right.DrawLatex(pos_x, lumi_y, f"#int L dt = {lumi_fb} fb^{{-1}}")
    latex_right.DrawLatex(pos_x, lumi_y, f"{lumi_fb} fb^{{-1}}")

    if not hasattr(canvas, "_labels"):
        canvas._labels = []
    canvas._labels.extend([latex_left, latex_right])


canvas = ROOT.TCanvas("canvas_D_all", "Dall sign-averaged fit", 800, 600)
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
upPad.SetBottomMargin(0.146)

dwPad = canvas.GetPad(2)
dwPad.SetPad(xlow, ylow, xup, ylow + 0.25 * (yup - ylow))

TEXT_FONT = 42
FONT_SIZE_UP = 0.053

up_height = yup - (ylow + 0.25 * (yup - ylow))
dw_height = (ylow + 0.25 * (yup - ylow)) - ylow
FONT_SIZE_DW = FONT_SIZE_UP * up_height / dw_height

canvas.cd(1)

h_data_all.SetStats(0)
h_data_all.SetTitle("")
h_data_all.GetXaxis().SetTitle(fit_var_name)
h_data_all.GetYaxis().SetTitle(f"Candidates per {1000.0 * bin_width:.2f} MeV/c^{{2}}")
h_data_all.SetMarkerStyle(20)
h_data_all.SetMarkerSize(0.8)

for axis in [h_data_all.GetXaxis(), h_data_all.GetYaxis()]:
    axis.SetTitleFont(TEXT_FONT)
    axis.SetLabelFont(TEXT_FONT)
    axis.SetTitleSize(FONT_SIZE_UP)
    axis.SetLabelSize(FONT_SIZE_UP)
    axis.CenterTitle(True)

h_data_all.GetXaxis().SetTitleSize(FONT_SIZE_UP)
h_data_all.GetXaxis().SetTitleOffset(1.3)
h_data_all.GetYaxis().SetTitleOffset(1.35)

max_y = max(h_data_all.GetMaximum(), max(y_fit) if y_fit else 0.0)
h_data_all.SetMaximum(1.3 * max_y)
h_data_all.SetMinimum(0.0)
h_data_all.Draw("PE")

g_comb = make_fill_graph_to_zero("g_comb_sum", xvals, y_comb)
g_comb.SetFillColor(ROOT.kGray)
g_comb.SetLineColor(ROOT.kGray)
g_comb.Draw("F SAME")

g_rhopeta = make_band_graph("g_rhopeta_sum", xvals, y_comb, y_bkg_total)
g_rhopeta.SetFillColor(ROOT.kOrange + 4)
g_rhopeta.SetLineColor(ROOT.kOrange + 4)
g_rhopeta.Draw("F SAME")

g_fit = make_line_graph("g_fit_sum", xvals, y_fit)
g_fit.SetLineColor(ROOT.kBlue)
g_fit.SetLineWidth(2)
g_fit.Draw("L SAME")

h_data_all.Draw("PE SAME")

leg1 = ROOT.TLegend(0.2, 0.65, 0.4, 0.90)
leg1.SetFillColorAlpha(ROOT.kWhite, 0)
leg1.SetBorderSize(0)
leg1.SetTextFont(TEXT_FONT)
leg1.SetTextSize(FONT_SIZE_UP)
leg1.AddEntry(h_data_all, "#font[42]{Data}", "PE")
leg1.AddEntry(g_fit, "#font[42]{Fit}", "l")
leg1.AddEntry(g_rhopeta, "#font[42]{D_{s}^{+} #rightarrow #rho^{+} #eta}", "f")
leg1.AddEntry(g_comb, "#font[42]{Combinatorial}", "f")
leg1.Draw()

upPad.RedrawAxis()

canvas.cd(2)

hA_avg.SetStats(0)
hA_avg.SetTitle("")
hA_avg.SetMarkerStyle(20)
hA_avg.SetMarkerSize(0.8)
hA_avg.SetYTitle("Asymmetry")

for axis in [hA_avg.GetXaxis(), hA_avg.GetYaxis()]:
    axis.SetTitleFont(TEXT_FONT)
    axis.SetLabelFont(TEXT_FONT)
    axis.SetTitleSize(FONT_SIZE_DW)
    axis.SetLabelSize(FONT_SIZE_DW)
    axis.CenterTitle(True)

hA_avg.GetXaxis().SetTitleSize(0)
hA_avg.GetXaxis().SetLabelSize(0)
hA_avg.GetYaxis().SetTitleOffset(0.43)
hA_avg.GetXaxis().SetTitleOffset(1.0)
hA_avg.GetYaxis().SetLabelSize(FONT_SIZE_DW*0.8)

hA_avg.SetMinimum(-0.2)
hA_avg.SetMaximum(0.2)
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

# Keep ROOT files alive until the end.
_ = (f_sig, f_sig_Ds, f_rhopeta, f_plus, f_minus)
