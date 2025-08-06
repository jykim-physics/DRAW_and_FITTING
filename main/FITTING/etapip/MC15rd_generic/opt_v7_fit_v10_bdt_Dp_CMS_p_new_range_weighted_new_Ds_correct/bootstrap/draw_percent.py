import uproot
import numpy as np
import matplotlib.pyplot as plt

try:
    plt.style.use('/home/jykim/DRAW_and_FITTING/main/mplstyle/belle2_serif.mplstyle')
except OSError:
    print("Please install belle2 matplotlib style")

#mode = "etapip_gg_K"
#branch_name = "delta_acp"
#branch_name = "delta_Ds_acp"
#range_min, range_max = -10, 10

#mode = "etapip_pipipi_K"
#branch_name = "delta_acp"
#branch_name = "delta_Ds_acp"
#range_min, range_max = -10, 10

mode = "etapip_pipipi"
branch_name = "delta_acp"
#branch_name = "delta_Ds_acp"
range_min, range_max = -0.1, 0.1

#mode = "etapip_gg"
#branch_name = "delta_acp"
#branch_name = "delta_Ds_acp"
#range_min, range_max = -1, 1
#range_min, range_max = -0.1, 0.1

print(f"Current mode is {mode}")
print(f"Branch name is {branch_name}")
# File paths
#file1 = f"bootstrap_acp_results_{mode}_minus.root"
#file2 = f"bootstrap_acp_results_{mode}_plus.root"
file1 = f"bootstrap_acp_results_{mode}_minus_converge.root"
file2 = f"bootstrap_acp_results_{mode}_plus_converge.root"

# Parameters
tree_name = "acp_bootstrap"
bins = 50

# Function to extract data from ROOT files using uproot
def extract_branch_values(file_path, tree_name, branch_name):
    with uproot.open(file_path) as file:
        tree = file[tree_name]
        data = tree[branch_name].array(library="np") * 100  # Convert to percentage
    return data

# Extract data
data1 = extract_branch_values(file1, tree_name, branch_name)
data2 = extract_branch_values(file2, tree_name, branch_name)

# Calculate statistics
mean1, std1 = np.mean(data1), np.std(data1)
mean2, std2 = np.mean(data2), np.std(data2)

# Plot histograms
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
plt.savefig(f"plots/{branch_name}_{mode}.png")
plt.show()

print(f"cos minus: mean = {mean1:.3f}%, std = {std1:.3f}%")
print(f"cso plus: mean = {mean2:.3f}%, std = {std2:.3f}%")

# Combined statistics
combined_mean = (mean1 + mean2) / 2
combined_std = np.sqrt(std1**2 + std2**2)/2

print(f"\nCombined mean: {combined_mean:.3f}%")
print(f"Combined error (std): {combined_std:.3f}%")


