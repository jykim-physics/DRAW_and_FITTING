import uproot
import numpy as np
import matplotlib.pyplot as plt
import os

try:
    plt.style.use('/home/jykim/DRAW_and_FITTING/main/mplstyle/belle2_serif.mplstyle')
except OSError:
    print("Please install belle2 matplotlib style")

# Configuration
modes = {
    "etapip_gg_K": [-5, 5],
    "etapip_pipipi_K": [-5, 5],
    "etapip_pipipi": [-0.1, 0.1],
    "etapip_gg": [-0.1, 0.1]
}

branches = ["delta_acp", "delta_Ds_acp"]
tree_name = "acp_bootstrap"
bins = 50
output_dir = "plots"
os.makedirs(output_dir, exist_ok=True)

# Function to extract data
def extract_branch_values(file_path, tree_name, branch_name):
    with uproot.open(file_path) as file:
        tree = file[tree_name]
        data = tree[branch_name].array(library="np") * 100  # Convert to percentage
    return data

# Loop over modes and branches
for mode, (range_min, range_max) in modes.items():
    for branch_name in branches:
        print(f"\n=== Processing mode: {mode}, branch: {branch_name} ===")

        file1 = f"bootstrap_acp_results_{mode}_minus_converge.root"
        file2 = f"bootstrap_acp_results_{mode}_plus_converge.root"

        # Check if files exist
        if not os.path.exists(file1) or not os.path.exists(file2):
            print(f"Missing file(s) for mode {mode}. Skipping...")
            continue

        # Extract data
        data1 = extract_branch_values(file1, tree_name, branch_name)
        data2 = extract_branch_values(file2, tree_name, branch_name)

        # Calculate statistics
        mean1, std1 = np.mean(data1), np.std(data1)
        mean2, std2 = np.mean(data2), np.std(data2)

        # Plot
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        axes[0].hist(data1, bins=bins, range=(range_min, range_max), histtype='stepfilled', alpha=0.7)
        axes[0].set_title(r"$\cos\theta^*<0$")
        axes[0].set_xlabel(r"$\Delta A_{CP}$ [%]")
        axes[0].set_ylabel("Counts")
        axes[0].text(0.05, 0.95, f"Mean = {mean1:.3f}%\nStd = {std1:.3f}%", transform=axes[0].transAxes,
                     verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        axes[1].hist(data2, bins=bins, range=(range_min, range_max), histtype='stepfilled', alpha=0.7)
        axes[1].set_title(r"$\cos\theta^*>0$")
        axes[1].set_xlabel(r"$\Delta A_{CP}$ [%]")
        axes[1].set_ylabel("Counts")
        axes[1].text(0.05, 0.95, f"Mean = {mean2:.3f}%\nStd = {std2:.3f}%", transform=axes[1].transAxes,
                     verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.tight_layout()
        plot_path = f"{output_dir}/{branch_name}_{mode}.png"
        plt.savefig(plot_path)
        plt.close()

        # Print statistics
        print(f"cosθ* < 0: mean = {mean1:.3f}%, std = {std1:.3f}%")
        print(f"cosθ* > 0: mean = {mean2:.3f}%, std = {std2:.3f}%")

        combined_mean = (mean1 + mean2) / 2
        combined_std = np.sqrt(std1**2 + std2**2) / 2

        print(f"Combined mean: {combined_mean:.3f}%")
        print(f"Combined error (std): {combined_std:.3f}%")

