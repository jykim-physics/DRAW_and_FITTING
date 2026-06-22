import ROOT
import glob
import os
import argparse

parser = argparse.ArgumentParser(description="Process Dp_CMS_sign argument")
parser.add_argument("-s", "--sign", choices=["plus", "minus", "all"], required=True,
                    help="Specify 'plus', 'minus', or 'all'")
parser.add_argument("-t", "--train", required=True,
                    help="Specify train version")
args = parser.parse_args()

print(f"Dp_CMS_sign is set to: {args.sign}")

if args.sign == "plus":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>0"
elif args.sign == "minus":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta<0"
elif args.sign == "all":
    Dp_CMS_cosTheta_cut = "Dp_CMS_cosTheta>-10"

#suffix = "no_bdt_removed_DspKsKp"
suffix = "after_bdt_removed_DspKsKp"

out_dir = "/share/storage/jykim/plots/MC15rd/Kspip/gg/generic"
os.makedirs(out_dir, exist_ok=True)
print("Directory created:", out_dir)

ROOT.gROOT.SetBatch(True)
ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/Kspip/MC15rd_Kspip_loose_v7_1_260109"

cm_elements = [
    "MC_KsHp_e7_18_4S_v3",
    "MC_KsHp_e20_b26_v1",
    "MC_KsHp_e20_e26_4S_v2",
    "MC_KsHp_e21_5Sscan_v1",
    "MC_KsHp_mori_off_v1",
]

ref_tree = "etapip_gg"
tree_name = "Ks"

file_list = []
for element in cm_elements:
    #pattern = f"{base_path}/{element}/{ref_tree}/{tree_name}/no_bdt/*.BDT.root"
    pattern = f"{base_path}/{element}/{ref_tree}/{tree_name}/0.80/*.BDT.root"
    file_list += glob.glob(pattern)

print(file_list)
print(f"Number of files: {len(file_list)}")

mychain = ROOT.TChain(tree_name)
for f in file_list:
    mychain.Add(f)

fit_variable = "Dp_M"
fit_var_name = "M(K^{0}_{S}#pi^{+}) [GeV/c^{2}]"

xmin, xmax = 1.80, 1.93
nbins = 80

# True이면 shape 비교용 unit-area normalization
# False이면 raw entries 비교
normalize_to_area = False

# ------------------------------------------------------------
# Common cuts
# ------------------------------------------------------------
base_cut = (
    "rank_Dp_chiProb==1"
    f" && {Dp_CMS_cosTheta_cut}"
    " && etapip_Eta_isSignal==1"
    " && etapip_Eta_genMotherID==Pip_genMotherID"
)
base_cut_for_bkg = (
    "rank_Dp_chiProb==1"
    f" && {Dp_CMS_cosTheta_cut}"
)

# ------------------------------------------------------------
# Component 1:
# Ds+ -> Ks K+ reconstructed as Ks pi+
# and charge conjugate
# ------------------------------------------------------------
cut_Ds_to_KsK_plus = (
    "Pip_charge==1"
    f" && {base_cut}"
    " && Pip_genMotherPDG==431"
    " && Pip_mcPDG==321"
)

cut_Ds_to_KsK_minus = (
    "Pip_charge==-1"
    f" && {base_cut}"
    " && Pip_genMotherPDG==-431"
    " && Pip_mcPDG==-321"
)

# ------------------------------------------------------------
# Component 2:
# D+ -> Ks pi+
# and charge conjugate
# ------------------------------------------------------------
cut_D_to_Kspi_plus = (
    "Pip_charge==1"
    f" && {base_cut}"
    " && Pip_genMotherPDG==411"
    " && Pip_mcPDG==211"
)

cut_D_to_Kspi_minus = (
    "Pip_charge==-1"
    f" && {base_cut}"
    " && Pip_genMotherPDG==-411"
    " && Pip_mcPDG==-211"
)

# ------------------------------------------------------------
# Component 3:
# Others = neither Ds -> KsK nor D -> Kspi
#
# Important:
# others = NOT(A OR B)
#        = NOT(A) AND NOT(B)
# ------------------------------------------------------------
cut_others_plus = (
    "Pip_charge==1"
    f" && {base_cut_for_bkg}"
    " && !((etapip_Eta_isSignal==1 &&  etapip_Eta_genMotherID==Pip_genMotherID && Pip_genMotherPDG==431 && Pip_mcPDG==321)"
    " || (etapip_Eta_isSignal==1 &&  etapip_Eta_genMotherID==Pip_genMotherID && Pip_genMotherPDG==411 && Pip_mcPDG==211))"
)

cut_others_minus = (
    "Pip_charge==-1"
    f" && {base_cut_for_bkg}"
    " && !((etapip_Eta_isSignal==1 &&  etapip_Eta_genMotherID==Pip_genMotherID && Pip_genMotherPDG==-431 && Pip_mcPDG==-321)"
    " || (etapip_Eta_isSignal==1 &&  etapip_Eta_genMotherID==Pip_genMotherID && Pip_genMotherPDG==-411 && Pip_mcPDG==-211))"
)

# ------------------------------------------------------------
# Histogram helper
# ------------------------------------------------------------
def make_charge_summed_hist(chain, hist_name, title, cut_plus, cut_minus):
    h_plus = ROOT.TH1F(f"{hist_name}_plus", title, nbins, xmin, xmax)
    h_minus = ROOT.TH1F(f"{hist_name}_minus", title, nbins, xmin, xmax)

    h_plus.Sumw2()
    h_minus.Sumw2()

    chain.Draw(f"{fit_variable}>>{h_plus.GetName()}", cut_plus, "goff")
    chain.Draw(f"{fit_variable}>>{h_minus.GetName()}", cut_minus, "goff")

    h_sum = h_plus.Clone(hist_name)
    h_sum.SetDirectory(0)
    h_sum.Add(h_minus)

    return h_sum, h_plus, h_minus


h_Ds_to_KsK, h_Ds_plus, h_Ds_minus = make_charge_summed_hist(
    mychain,
    "h_Ds_to_KsK",
    "D_{s}^{#pm} #rightarrow K^{0}_{S}K^{#pm} reconstructed as K^{0}_{S}#pi^{#pm}",
    cut_Ds_to_KsK_plus,
    cut_Ds_to_KsK_minus,
)

h_D_to_Kspi, h_D_plus, h_D_minus = make_charge_summed_hist(
    mychain,
    "h_D_to_Kspi",
    "D^{#pm} #rightarrow K^{0}_{S}#pi^{#pm}",
    cut_D_to_Kspi_plus,
    cut_D_to_Kspi_minus,
)

h_others, h_others_plus, h_others_minus = make_charge_summed_hist(
    mychain,
    "h_others",
    "Others",
    cut_others_plus,
    cut_others_minus,
)

print("")
print("Entries")
print("--------------------------------------------------")
print("D  -> Kspi plus        :", h_D_plus.Integral())
print("D  -> Kspi minus       :", h_D_minus.Integral())
print("D  -> Kspi total       :", h_D_to_Kspi.Integral())
print("")
print("Ds -> KsK misID plus   :", h_Ds_plus.Integral())
print("Ds -> KsK misID minus  :", h_Ds_minus.Integral())
print("Ds -> KsK misID total  :", h_Ds_to_KsK.Integral())
print("")
print("Others plus            :", h_others_plus.Integral())
print("Others minus           :", h_others_minus.Integral())
print("Others total           :", h_others.Integral())
print("--------------------------------------------------")
print("Check total            :", h_D_to_Kspi.Integral() + h_Ds_to_KsK.Integral() + h_others.Integral())

# ------------------------------------------------------------
# Optional normalization
# ------------------------------------------------------------
if normalize_to_area:
    for h in [h_D_to_Kspi, h_Ds_to_KsK, h_others]:
        if h.Integral() > 0:
            h.Scale(1.0 / h.Integral())

# ------------------------------------------------------------
# Drawing helpers
# ------------------------------------------------------------
def setup_hist_style(hist, color, marker):
    hist.SetLineColor(color)
    hist.SetMarkerColor(color)
    hist.SetMarkerStyle(marker)
    hist.SetLineWidth(2)


def setup_axis(hist):
    hist.GetXaxis().SetTitle(fit_var_name)

    if normalize_to_area:
        hist.GetYaxis().SetTitle("Normalized entries")
    else:
        hist.GetYaxis().SetTitle("Entries")


def draw_single_hist(hist, out_name, legend_label):
    c = ROOT.TCanvas(f"c_{hist.GetName()}", f"c_{hist.GetName()}", 800, 700)

    setup_axis(hist)

    if hist.GetMaximum() > 0:
        hist.SetMaximum(hist.GetMaximum() * 1.30)

    hist.Draw("E")

    # Legend on left
    leg = ROOT.TLegend(0.18, 0.72, 0.60, 0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.030)
    leg.AddEntry(hist, legend_label, "lep")
    leg.Draw()

    c.SaveAs(out_name)
    print(f"Saved: {out_name}")


def draw_overlay_three(hist1, hist2, hist3, out_name):
    c = ROOT.TCanvas("c_overlay_three", "c_overlay_three", 800, 700)

    setup_axis(hist1)

    max_y = max(hist1.GetMaximum(), hist2.GetMaximum(), hist3.GetMaximum())
    if max_y > 0:
        hist1.SetMaximum(max_y * 1.35)

    hist1.Draw("E")
    hist2.Draw("E SAME")
    hist3.Draw("E SAME")

    # Legend on left
    leg = ROOT.TLegend(0.18, 0.62, 0.65, 0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.030)
    leg.AddEntry(hist1, "D^{#pm} #rightarrow K^{0}_{S}#pi^{#pm}", "lep")
    leg.AddEntry(hist2, "D_{s}^{#pm} #rightarrow K^{0}_{S}K^{#pm} mis-ID", "lep")
    leg.AddEntry(hist3, "Others", "lep")
    leg.Draw()

    c.SaveAs(out_name)
    print(f"Saved: {out_name}")


# ------------------------------------------------------------
# Style
# ------------------------------------------------------------
setup_hist_style(h_D_to_Kspi, ROOT.kBlue + 1, 20)
setup_hist_style(h_Ds_to_KsK, ROOT.kRed + 1, 24)
setup_hist_style(h_others, ROOT.kGreen + 2, 21)

# ------------------------------------------------------------
# Output file names
# ------------------------------------------------------------
norm_tag = "norm" if normalize_to_area else "raw"

out_png_D_to_Kspi = (
    f"{out_dir}/MC15rd_Kspip_gg_hist_D_to_Kspi_"
    f"fitv3_{args.train}_Dp_CMS_{args.sign}_{suffix}_{norm_tag}.png"
)

out_png_Ds_to_KsK = (
    f"{out_dir}/MC15rd_Kspip_gg_hist_Ds_to_KsK_misID_"
    f"fitv3_{args.train}_Dp_CMS_{args.sign}_{suffix}_{norm_tag}.png"
)

out_png_others = (
    f"{out_dir}/MC15rd_Kspip_gg_hist_others_"
    f"fitv3_{args.train}_Dp_CMS_{args.sign}_{suffix}_{norm_tag}.png"
)

out_png_overlay = (
    f"{out_dir}/MC15rd_Kspip_gg_hist_overlay_with_others_"
    f"fitv3_{args.train}_Dp_CMS_{args.sign}_{suffix}_{norm_tag}.png"
)

# ------------------------------------------------------------
# Draw plots
# ------------------------------------------------------------
draw_single_hist(
    h_D_to_Kspi,
    out_png_D_to_Kspi,
    "D^{#pm} #rightarrow K^{0}_{S}#pi^{#pm}"
)

draw_single_hist(
    h_Ds_to_KsK,
    out_png_Ds_to_KsK,
    "D_{s}^{#pm} #rightarrow K^{0}_{S}K^{#pm} mis-ID"
)

draw_single_hist(
    h_others,
    out_png_others,
    "Others"
)

draw_overlay_three(
    h_D_to_Kspi,
    h_Ds_to_KsK,
    h_others,
    out_png_overlay
)
