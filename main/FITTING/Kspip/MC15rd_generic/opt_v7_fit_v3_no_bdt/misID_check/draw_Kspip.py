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

suffix = "no_bdt_removed_DspKsKp"

out_png = (
    f"/share/storage/jykim/plots/MC15rd/Kspip/gg/generic/"
    f"MC15rd_Kspip_gg_hist_overlay_fitv3_{args.train}_Dp_CMS_{args.sign}_{suffix}.png"
)

dir_path = os.path.dirname(out_png)
os.makedirs(dir_path, exist_ok=True)
print("Directory created:", dir_path)

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
    pattern = f"{base_path}/{element}/{ref_tree}/{tree_name}/no_bdt/*.BDT.root"
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

# ------------------------------------------------------------
# Common cuts
# ------------------------------------------------------------
base_cut = (
    "rank_Dp_chiProb==1"
    f" && {Dp_CMS_cosTheta_cut}"
    " && etapip_Eta_isSignal==1"
    " && etapip_Eta_genMotherID==Pip_genMotherID"
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

print("Entries")
print("Ds -> KsK misID plus  :", h_Ds_plus.Integral())
print("Ds -> KsK misID minus :", h_Ds_minus.Integral())
print("Ds -> KsK misID total :", h_Ds_to_KsK.Integral())

print("D -> Kspi plus        :", h_D_plus.Integral())
print("D -> Kspi minus       :", h_D_minus.Integral())
print("D -> Kspi total       :", h_D_to_Kspi.Integral())

# ------------------------------------------------------------
# Optional: normalize to unit area for shape comparison
# ------------------------------------------------------------
normalize_to_area = False

if normalize_to_area:
    if h_Ds_to_KsK.Integral() > 0:
        h_Ds_to_KsK.Scale(1.0 / h_Ds_to_KsK.Integral())
    if h_D_to_Kspi.Integral() > 0:
        h_D_to_Kspi.Scale(1.0 / h_D_to_Kspi.Integral())

# ------------------------------------------------------------
# Draw overlay
# ------------------------------------------------------------
# ------------------------------------------------------------
# Draw helper
# ------------------------------------------------------------
def setup_hist_style(hist, color, marker):
    hist.SetLineColor(color)
    hist.SetMarkerColor(color)
    hist.SetMarkerStyle(marker)
    hist.SetLineWidth(2)


def draw_single_hist(hist, out_name, legend_label):
    c = ROOT.TCanvas(f"c_{hist.GetName()}", f"c_{hist.GetName()}", 800, 700)

    hist.GetXaxis().SetTitle(fit_var_name)

    if normalize_to_area:
        hist.GetYaxis().SetTitle("Normalized entries")
    else:
        hist.GetYaxis().SetTitle("Entries")

    hist.SetMaximum(hist.GetMaximum() * 1.30)
    hist.Draw("E")

    # Legend moved to left
    leg = ROOT.TLegend(0.18, 0.72, 0.55, 0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(hist, legend_label, "lep")
    leg.Draw()

    c.SaveAs(out_name)
    print(f"Saved: {out_name}")


def draw_overlay_hist(hist1, hist2, out_name):
    c = ROOT.TCanvas("c_overlay", "c_overlay", 800, 700)

    hist1.GetXaxis().SetTitle(fit_var_name)

    if normalize_to_area:
        hist1.GetYaxis().SetTitle("Normalized entries")
    else:
        hist1.GetYaxis().SetTitle("Entries")

    max_y = max(hist1.GetMaximum(), hist2.GetMaximum())
    hist1.SetMaximum(max_y * 1.35)

    hist1.Draw("E")
    hist2.Draw("E SAME")

    # Legend moved to left
    leg = ROOT.TLegend(0.18, 0.68, 0.60, 0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(hist1, "D^{#pm} #rightarrow K^{0}_{S}#pi^{#pm}", "lep")
    leg.AddEntry(hist2, "D_{s}^{#pm} #rightarrow K^{0}_{S}K^{#pm} mis-ID", "lep")
    leg.Draw()

    c.SaveAs(out_name)
    print(f"Saved: {out_name}")


# ------------------------------------------------------------
# Style
# ------------------------------------------------------------
setup_hist_style(h_D_to_Kspi, ROOT.kBlue + 1, 20)
setup_hist_style(h_Ds_to_KsK, ROOT.kRed + 1, 24)


# ------------------------------------------------------------
# Output file names
# ------------------------------------------------------------
out_png_overlay = (
    f"/share/storage/jykim/plots/MC15rd/Kspip/gg/generic/"
    f"MC15rd_Kspip_gg_hist_overlay_fitv3_{args.train}_Dp_CMS_{args.sign}_{suffix}.png"
)

out_png_D_to_Kspi = (
    f"/share/storage/jykim/plots/MC15rd/Kspip/gg/generic/"
    f"MC15rd_Kspip_gg_hist_D_to_Kspi_fitv3_{args.train}_Dp_CMS_{args.sign}_{suffix}.png"
)

out_png_Ds_to_KsK = (
    f"/share/storage/jykim/plots/MC15rd/Kspip/gg/generic/"
    f"MC15rd_Kspip_gg_hist_Ds_to_KsK_misID_fitv3_{args.train}_Dp_CMS_{args.sign}_{suffix}.png"
)


# ------------------------------------------------------------
# Draw separately
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


# ------------------------------------------------------------
# Draw overlay
# ------------------------------------------------------------
draw_overlay_hist(
    h_D_to_Kspi,
    h_Ds_to_KsK,
    out_png_overlay
)

