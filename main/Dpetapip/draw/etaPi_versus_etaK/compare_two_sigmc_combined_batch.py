#!/usr/bin/env python3
import os
import sys
import glob
import argparse
import ROOT


VARIABLES = [
    # var_name, xmin, xmax, display_name, legend_loc, is_logscale, output_tag
    #("BDT", 0.0, 1.0, "BDT", "left", False, "BDT"),
    #("Dp_cosHelicityAngleMomentum", -1.0, 1.0, "cosHel(D^{+}_{(s)})", "right", False, "Dp_cosHelicityAngleMomentum"),
    #("etapip_Eta_Easym", 0.0, 1.0, "abs((E_{#gamma_{1}} - E_{#gamma_{2}}) /(E_{#gamma_{1}} + E_{#gamma_{2}}))", "right", False, "etapip_Eta_Easym"),
    #("Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane", -1.0, 1.0, "cos#theta_{XY}", "right", True, "Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane"),
    #("Dp_dz", -0.2, 0.4, "dz(D^{+}_{(s)})", "right", False, "Dp_dz"),
    #("Pip_dr", 0.0, 0.1, "dr(h^{+})", "right", False, "Pip_dr"),
    #("Dp_CMS_p", 2.5, 5.2, "p^{*}(D^{+}_{(s)})", "right", False, "Dp_CMS_p"),
    #("etapip_Eta_daughterAngle_0_1", 0.0, 2.0, "Opening angle(#gamma, #gamma)", "right", False, "etapip_Eta_daughterAngle_0_1"),
    #("etapip_Eta_daughterDiffOfPhi_0_1", 0.0, 3.15, "|#Delta#phi(#gamma, #gamma)|", "right", False, "etapip_Eta_daughterDiffOfPhi_0_1_abs"),
    #("etapip_Eta_p", 0.0, 6.5, "p(#eta_{#gamma #gamma})", "right", False, "etapip_Eta_p"),
    ("etapip_Eta_p", 0.0, 6.5, "p(#eta)", "right", False, "etapip_Eta_p"),
    #("eta_Pi0_daughterAngle_0_1", 0.0, 2.0, "Opening angle(#gamma, #gamma)", "right", False, "eta_Pi0_daughterAngle_0_1"),
    #("eta_Pi0_daughterDiffOfPhi_0_1", 0.0, 3.15, "|#Delta#phi(#gamma, #gamma)|", "right", False, "eta_Pi0_daughterDiffOfPhi_0_1_abs"),
    #("eta_Pi0_p", 0.0, 4.0, "p(#pi^{0})", "right", False, "eta_Pi0_p"),
    ("etapip_Eta_cosTheta", -1, 1, "cos#theta(#eta)", "left", False, "etapip_Eta_cosTheta"),
]


def str_to_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def add_files_to_chain(chain: ROOT.TChain, file_pattern: str) -> int:
    files = sorted(glob.glob(file_pattern))
    if not files:
        raise FileNotFoundError(f"No ROOT files matched pattern: {file_pattern}")

    for fname in files:
        chain.Add(fname)
    return len(files)


def check_branches(chain: ROOT.TChain, required_branches: list[str]) -> None:
    branch_names = {b.GetName() for b in chain.GetListOfBranches()}
    missing = [name for name in required_branches if name not in branch_names]

    if missing:
        available = sorted(branch_names)
        raise AttributeError(
            f"Missing branch(es) in tree '{chain.GetName()}': {missing}\n"
            f"Available branches include: {available[:40]}"
        )


def safe_int(value, nan_value: int = -1) -> int:
    value = float(value)
    if ROOT.TMath.IsNaN(value):
        return nan_value
    return int(value)


def make_hist(name: str, title: str, nbins: int, xmin: float, xmax: float, xtitle: str) -> ROOT.TH1F:
    hist = ROOT.TH1F(name, title, nbins, xmin, xmax)
    hist.Sumw2()
    hist.SetXTitle(xtitle)
    hist.SetYTitle("Entries")
    hist.SetStats(0)
    return hist


def normalize_if_requested(hist: ROOT.TH1F) -> None:
    integral = hist.Integral()
    if integral > 0:
        hist.Scale(1.0 / integral)
        hist.SetYTitle("Normalized entries")
    else:
        print(f"[WARNING] Histogram {hist.GetName()} has zero integral; skip normalization.")


def set_hist_style(hist: ROOT.TH1F, line_color: int) -> None:
    hist.SetLineColor(line_color)
    hist.SetMarkerColor(line_color)
    hist.SetLineWidth(2)
    hist.SetFillStyle(0)
    hist.SetMarkerStyle(0)
    hist.SetMarkerSize(0)


def fill_all_hists_with_cut(
    chain: ROOT.TChain,
    hists_by_var: dict[str, ROOT.TH1F],
    required_charge: int,
    signal_branch: str = "Dp_isSignal",
) -> tuple[int, int, int]:
    required_branches = ["Pip_charge", signal_branch, *hists_by_var.keys()]
    check_branches(chain, required_branches)

    n_seen = 0
    n_passed_cut = 0
    n_signal_nan = 0

    for entry in chain:
        n_seen += 1

        pip_charge = safe_int(getattr(entry, "Pip_charge"), nan_value=-999)
        raw_is_signal = float(getattr(entry, signal_branch))

        if ROOT.TMath.IsNaN(raw_is_signal):
            is_signal = -1
            n_signal_nan += 1
        else:
            is_signal = int(raw_is_signal)

        if pip_charge != required_charge:
            continue
        if is_signal != 1:
            continue

        n_passed_cut += 1

        for var_name, hist in hists_by_var.items():
            value = float(getattr(entry, var_name))
            if ROOT.TMath.IsNaN(value):
                continue

            # Plot absolute value for daughter Delta phi.
            if var_name == "etapip_Eta_daughterDiffOfPhi_0_1" or var_name == "eta_Pi0_daughterDiffOfPhi_0_1":
                value = abs(value)

            hist.Fill(value)

    return n_seen, n_passed_cut, n_signal_nan


def draw_one_variable(
    h1: ROOT.TH1F,
    h2: ROOT.TH1F,
    sample1_label: str,
    sample2_label: str,
    output_img_fname: str,
    legend_loc: str,
    use_log_y: bool,
    do_normalize: bool,
) -> None:
    if do_normalize:
        normalize_if_requested(h1)
        normalize_if_requested(h2)

    # sample1 = pion mode, sample2 = kaon mode
    set_hist_style(h1, ROOT.kOrange + 1)
    set_hist_style(h2, ROOT.kRed)

    canvas = ROOT.TCanvas(f"c_{h1.GetName()}", "Signal MC comparison", 800, 600)

    h_max = max(h1.GetMaximum(), h2.GetMaximum())
    if use_log_y:
        canvas.SetLogy(True)
        min_val = 1e-5 if do_normalize else 0.1
        ymax = max(h_max * 50.0, min_val * 10.0)
        h1.SetMinimum(min_val)
        h2.SetMinimum(min_val)
        h1.SetMaximum(ymax)
        h2.SetMaximum(ymax)
    else:
        canvas.SetLogy(False)
        ymax = h_max * 1.2 if h_max > 0 else 1.0
        h1.SetMinimum(0.0)
        h2.SetMinimum(0.0)
        h1.SetMaximum(ymax)
        h2.SetMaximum(ymax)

    if h1.GetMaximum() >= h2.GetMaximum():
        first, second = h1, h2
    else:
        first, second = h2, h1

    first.Draw("HIST")
    second.Draw("HIST SAME")
    first.Draw("E SAME")
    second.Draw("E SAME")

    if legend_loc == "left":
        legend = ROOT.TLegend(0.18, 0.75, 0.48, 0.90)
    else:
        legend = ROOT.TLegend(0.62, 0.75, 0.92, 0.90)

    legend.SetFillColorAlpha(ROOT.kWhite, 0.0)
    legend.SetBorderSize(0)
    #legend.SetFillStyle(0)
    legend.SetTextFont(42)
    legend.SetTextSize(0.045)
    legend.AddEntry(h1, sample1_label, "LE")
    legend.AddEntry(h2, sample2_label, "LE")
    legend.Draw()

    out_dir = os.path.dirname(output_img_fname)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    canvas.SaveAs(output_img_fname)
    print(f"[INFO] Saved: {output_img_fname}")

    # Avoid accumulating canvases in a long batch job.
    canvas.Close()


def build_hist_map(prefix: str, sample_label: str) -> dict[str, ROOT.TH1F]:
    hists = {}
    for var_name, xmin, xmax, display_name, _, _, _ in VARIABLES:
        nbins = 100 if var_name == "Dp_CMS_p" else 50
        hname = f"h_{prefix}_{var_name}"
        hists[var_name] = make_hist(hname, sample_label, nbins, xmin, xmax, display_name)
    return hists


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare pion-mode and kaon-mode signal MC, including charge-conjugate samples, in one ROOT/Python run."
    )

    parser.add_argument("--sample1-plus-pattern", required=True)
    parser.add_argument("--sample1-plus-tree", required=True)
    parser.add_argument("--sample1-cc-pattern", required=True)
    parser.add_argument("--sample1-cc-tree", required=True)
    parser.add_argument("--sample1-label", required=True)

    parser.add_argument("--sample2-plus-pattern", required=True)
    parser.add_argument("--sample2-plus-tree", required=True)
    parser.add_argument("--sample2-cc-pattern", required=True)
    parser.add_argument("--sample2-cc-tree", required=True)
    parser.add_argument("--sample2-label", required=True)

    parser.add_argument("--img-prefix", required=True)
    parser.add_argument("--normalized", default="True", help="True or False")
    parser.add_argument("--signal-branch", default="Dp_isSignal")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    do_normalize = str_to_bool(args.normalized)

    style_macro = "/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C"
    if os.path.exists(style_macro):
        ROOT.gROOT.LoadMacro(style_macro)
        ROOT.SetBelle2Style()

    ROOT.gROOT.SetBatch(True)
    ROOT.TH1.AddDirectory(False)

    sample1_plus_chain = ROOT.TChain(args.sample1_plus_tree)
    sample1_cc_chain = ROOT.TChain(args.sample1_cc_tree)
    sample2_plus_chain = ROOT.TChain(args.sample2_plus_tree)
    sample2_cc_chain = ROOT.TChain(args.sample2_cc_tree)

    n_s1_plus_files = add_files_to_chain(sample1_plus_chain, args.sample1_plus_pattern)
    n_s1_cc_files = add_files_to_chain(sample1_cc_chain, args.sample1_cc_pattern)
    n_s2_plus_files = add_files_to_chain(sample2_plus_chain, args.sample2_plus_pattern)
    n_s2_cc_files = add_files_to_chain(sample2_cc_chain, args.sample2_cc_pattern)

    print(f"[INFO] Sample 1 plus: label={args.sample1_label}, tree={args.sample1_plus_tree}, files={n_s1_plus_files}, entries={sample1_plus_chain.GetEntries()}, cut=(Pip_charge == 1 && {args.signal_branch} == 1)")
    print(f"[INFO] Sample 1 cc  : label={args.sample1_label}, tree={args.sample1_cc_tree}, files={n_s1_cc_files}, entries={sample1_cc_chain.GetEntries()}, cut=(Pip_charge == -1 && {args.signal_branch} == 1)")
    print(f"[INFO] Sample 2 plus: label={args.sample2_label}, tree={args.sample2_plus_tree}, files={n_s2_plus_files}, entries={sample2_plus_chain.GetEntries()}, cut=(Pip_charge == 1 && {args.signal_branch} == 1)")
    print(f"[INFO] Sample 2 cc  : label={args.sample2_label}, tree={args.sample2_cc_tree}, files={n_s2_cc_files}, entries={sample2_cc_chain.GetEntries()}, cut=(Pip_charge == -1 && {args.signal_branch} == 1)")
    print(f"[INFO] Normalized: {do_normalize}")

    h1_by_var = build_hist_map("sample1", args.sample1_label)
    h2_by_var = build_hist_map("sample2", args.sample2_label)

    s1_plus_seen, s1_plus_passed, s1_plus_nan = fill_all_hists_with_cut(
        sample1_plus_chain, h1_by_var, required_charge=1, signal_branch=args.signal_branch
    )
    s1_cc_seen, s1_cc_passed, s1_cc_nan = fill_all_hists_with_cut(
        sample1_cc_chain, h1_by_var, required_charge=-1, signal_branch=args.signal_branch
    )
    s2_plus_seen, s2_plus_passed, s2_plus_nan = fill_all_hists_with_cut(
        sample2_plus_chain, h2_by_var, required_charge=1, signal_branch=args.signal_branch
    )
    s2_cc_seen, s2_cc_passed, s2_cc_nan = fill_all_hists_with_cut(
        sample2_cc_chain, h2_by_var, required_charge=-1, signal_branch=args.signal_branch
    )

    print(f"[INFO] Passed sample1 cut: plus {s1_plus_passed}/{s1_plus_seen}, cc {s1_cc_passed}/{s1_cc_seen}, total {s1_plus_passed + s1_cc_passed}")
    print(f"[INFO] Passed sample2 cut: plus {s2_plus_passed}/{s2_plus_seen}, cc {s2_cc_passed}/{s2_cc_seen}, total {s2_plus_passed + s2_cc_passed}")
    print(f"[INFO] NaN {args.signal_branch} treated as -1:")
    print(f"       sample1 plus={s1_plus_nan}, sample1 cc={s1_cc_nan}, sample2 plus={s2_plus_nan}, sample2 cc={s2_cc_nan}")

    for var_name, _, _, _, legend_loc, use_log_y, output_tag in VARIABLES:
        output_img_fname = f"{args.img_prefix}_sigMC_etaPip_vs_etaKp_{output_tag}_norm{do_normalize}.png"
        print(f"[INFO] Drawing variable: {var_name}")
        draw_one_variable(
            h1_by_var[var_name],
            h2_by_var[var_name],
            args.sample1_label,
            args.sample2_label,
            output_img_fname,
            legend_loc,
            use_log_y,
            do_normalize,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
