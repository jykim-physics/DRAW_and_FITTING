#!/usr/bin/env python3
"""
Usage:
  python plot_bdt_scan.py path/to/your_text.txt

- Parses lines starting with 'MC15rd_...'
- Extracts BDT cut value (0.xx) and N_total ± Uncertainty
- Computes y = N_total / sqrt(Uncertainty_of_N_total)
- Saves:
    - ntot_over_sqrt_uncertainty.csv
    - ntot_over_sqrt_uncertainty.png
"""

import re
import math
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from math import sqrt
import ROOT
import ctypes
try:
#     plt.style.use('belle2')
    plt.style.use('belle2_serif')
#     plt.style.use('belle2_modern')
except OSError:
    print("Please install belle2 matplotlib style")
px = 1/plt.rcParams['figure.dpi']

def parse_text(raw_text: str) -> pd.DataFrame:
    # Each data row starts with the filename
    line_re = re.compile(r'^MC15rd_.*$', re.MULTILINE)
    # Matches "<number> ± <number>" or "<number> +/- <number>"
    pair_re = re.compile(
        r'([\-+]?\d+(?:\.\d+)?(?:[Ee][+\-]?\d+)?)\s*(?:±|\+/-)\s*([\-+]?\d+(?:\.\d+)?(?:[Ee][+\-]?\d+)?)'
    )

    records = []
    for m in line_re.finditer(raw_text):
        line = m.group(0)

        # Extract BDT cut value from the filename pattern "..._all_0.70_..."
        thr_m = re.search(r'_all_(\d\.\d{2})_', line)
        if not thr_m:
            continue
        bdt_cut = float(thr_m.group(1))

        # Extract all "<val> ± <err>" pairs in the line.
        # Expected order in the provided text:
        # 1) Acp, 2) Acp_Ds, 3) N_total, 4) N_total_Ds, 5) nbkg_total
        pairs = pair_re.findall(line)
        if len(pairs) < 3:
            # Not enough pairs to get N_total and its uncertainty
            continue

        # N_total is the 3rd pair
        n_total = float(pairs[3][0])
        n_total_unc = float(pairs[3][1])

        # Compute y = N_total / sqrt(Uncertainty)
        y_val = float('nan')
        if n_total_unc > 0:
            #y_val = n_total / math.sqrt(n_total_unc)
            y_val = n_total / n_total_unc

        records.append(
            {"bdt_cut": bdt_cut, "N_total": n_total,
             "sigma_N_total": n_total_unc, "N_over_sigma": y_val}
        )

    df = pd.DataFrame(records)
    df.sort_values("bdt_cut", inplace=True, ignore_index=True)
    return df

def main():
    if len(sys.argv) < 3:
        print("ERROR: Please provide the path to the text file.\n"
              "Usage: python plot_bdt_scan.py path/to/your_text.txt tree_name")
        sys.exit(1)

    in_path = sys.argv[1]
    tree_name = sys.argv[2]
    with open(in_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    df = parse_text(raw_text)
    if df.empty:
        print("No data rows were parsed. Check the input format.")
        sys.exit(1)

    title_dict = dict()
    title_dict['etapip_gg']=r"$D^+_{s} \to \eta_{\gamma\gamma} \pi^+$"
    title_dict['etapip_gg_K']=r"$D^+_{s} \to \eta_{\gamma\gamma} K^+$"
    title_dict['etapip_pipipi']=r"$D^+_{s} \to \eta_{3\pi} \pi^+$"
    title_dict['etapip_pipipi_K']=r"$D^+_{s} \to \eta_{3\pi} K^+$"
    # Save CSV
    #csv_path = "ntot_over_sqrt_uncertainty.csv"
    csv_path = f"Ds_ntot_over_sqrt_uncertainty_{tree_name}.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved CSV -> {csv_path}")

    # Plot
    plt.figure(figsize=(9, 5.5))
    plt.scatter(df["bdt_cut"], df["N_over_sigma"], marker="x")
    plt.xlabel("BDT cut value")
    plt.ylabel(r"$N_{D^+_{s}} / \sigma_{N_{D^+_{s}}}$")
    #plt.title(r"$D^+_{(s)} \to \eta_{\gamma\gamma} K^+$")
    #plt.title(r"$D^+_{(s)} \to \eta_{3\pi} K^+$")
    #plt.title(r"$D^+_{(s)} \to \eta_{\gamma\gamma} \pi^+$")
    #plt.title(r"$D^+_{(s)} \to \eta_{3\pi} \pi^+$")
    plt.title(title_dict[tree_name])
    plt.grid(True, linestyle="--", alpha=0.5)

    if tree_name=='etapip_gg':
      plt.xlim(0.61, 0.90)
    elif tree_name=='etapip_pipipi':
      plt.xlim(0.51, 0.90)
    elif tree_name=='etapip_pipipi_K':
      plt.xlim(0.61, 0.99)
    elif tree_name=='etapip_gg_K':
      plt.xlim(0.75, 0.99)

    # Annotate the maximum point (if non-NaN)
    idx_max = df["N_over_sigma"].idxmax()
    x_max = df.loc[idx_max, "bdt_cut"]
    y_max = df.loc[idx_max, "N_over_sigma"]
    if pd.notna(y_max):
        plt.annotate(f"max @ {x_max:.2f}",
                     xy=(x_max, y_max),
                     #xytext=(x_max, y_max * 1.05),
                     xytext=(x_max * 1.005, y_max * 0.90),
                     arrowprops=dict(arrowstyle="->"))

    png_path = f"Ds_ntot_over_sqrt_uncertainty_{tree_name}.png"
    plt.tight_layout()
    plt.savefig(png_path, dpi=150)
    print(f"Saved plot -> {png_path}")
    plt.show()

if __name__ == "__main__":
    main()

