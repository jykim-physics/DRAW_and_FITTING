import os
import uproot
import numpy as np
import matplotlib.pyplot as plt

try:
    plt.style.use('/home/jykim/DRAW_and_FITTING/main/mplstyle/belle2_serif.mplstyle')
except OSError:
    print("Please install belle2 matplotlib style")

# Modes to process
modes = [
    "etapip_pipipi_K",
    "etapip_gg_K",
]

branch_name = "relative_delta"
branch_name1 = branch_name + "_NDp"
branch_name2 = branch_name + "_NDsp"

range_min, range_max = -15, 15
# range_min, range_max = -5, 5

tree_name = "acp_bootstrap"
bins = 50

os.makedirs("plots", exist_ok=True)


def extract_branch_values(file_path, tree_name, branch_name):
    with uproot.open(file_path) as file:
        if tree_name not in file:
            raise KeyError(f"Tree '{tree_name}' not found in {file_path}")

        tree = file[tree_name]

        if branch_name not in tree:
            raise KeyError(f"Branch '{branch_name}' not found in tree '{tree_name}'")

        data = tree[branch_name].array(library="np") * 100  # Convert to percentage

    return data


for mode in modes:
    print("=" * 60)
    print(f"Mode: {mode}")

    file1 = f"bootstrap_acp_results_{mode}_all_converge.root"
    #file1 = f"bootstrap_acp_results_{mode}_plus_converge.root"
    #file1 = f"bootstrap_acp_results_{mode}_minus_converge.root"

    if not os.path.exists(file1):
        print(f"[SKIP] File not found: {file1}")
        continue

    try:
        data1 = extract_branch_values(file1, tree_name, branch_name1)
        data2 = extract_branch_values(file1, tree_name, branch_name2)

    except Exception as e:
        print(f"[SKIP] Failed to read {file1}")
        print(f"Reason: {e}")
        continue

    if len(data1) == 0 or len(data2) == 0:
        print(f"[SKIP] Empty data found in {file1}")
        continue

    mean1, std1 = np.mean(data1), np.std(data1)
    mean2, std2 = np.mean(data2), np.std(data2)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    axes[0].hist(
        data1,
        bins=bins,
        range=(range_min, range_max),
        histtype="stepfilled",
        alpha=0.7,
    )
    axes[0].set_xlabel(
        r"$\Delta N_{\text{sig},D^+}/N_{\text{sig},D^+}$ [%]"
    )
    axes[0].set_ylabel("Counts")
    axes[0].text(
        0.05,
        0.95,
        f"Mean = {mean1:.3f}%\nStd = {std1:.3f}%",
        transform=axes[0].transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    axes[1].hist(
        data2,
        bins=bins,
        range=(range_min, range_max),
        histtype="stepfilled",
        alpha=0.7,
    )
    axes[1].set_xlabel(
        r"$\Delta N_{\text{sig},D^+_s}/N_{\text{sig},D^+_s}$ [%]"
    )
    axes[1].set_ylabel("Counts")
    axes[1].text(
        0.05,
        0.95,
        f"Mean = {mean2:.3f}%\nStd = {std2:.3f}%",
        transform=axes[1].transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    plt.tight_layout()

    output_path = f"plots/{branch_name}_{mode}.png"
    plt.savefig(output_path, dpi=300)
    plt.show()
    plt.close(fig)

    print(f"D+  : mean = {mean1:.3f}%, std = {std1:.3f}%")
    print(f"Ds+ : mean = {mean2:.3f}%, std = {std2:.3f}%")
    print(f"Saved: {output_path}")
