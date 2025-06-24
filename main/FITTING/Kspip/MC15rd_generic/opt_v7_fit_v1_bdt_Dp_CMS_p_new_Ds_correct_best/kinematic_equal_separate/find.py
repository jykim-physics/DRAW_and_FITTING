import ROOT
import glob
import math

# Your original setup
base_path = "/share/storage/jykim/storage_b2/storage/reduced_ntuples/MC15rd/Kspip//MC15rd_Kspip_loose_v7_1_250228_Dp_CMS_p_v3"
cm_elements = ["MCrd_Ks_e7_18_4S_v3", "MCrd_Ks_e20_b26_v1", "MCrd_Ks_e20_e26_4S_v2", "MCrd_Ks_e21_5S_scan_v1", "MCrd_Ks_mori_off_v1"]

ref_tree = "etapip_pipipi"
tree_name = "Ks"
BDT_cut = "0.74"     # ← Replace with your actual BDT_cut
args_sign = "plus"  # ← Replace with your actual args.sign

bad_files = []

for element in cm_elements:
    pattern = f"{base_path}/{element}/{ref_tree}/{tree_name}/{BDT_cut}/{args_sign}/bdtg_Ds/*.BCS.bdtg.root"
    file_list = glob.glob(pattern)

    for filename in file_list:
        file = ROOT.TFile.Open(filename)
        tree = file.Get(tree_name)

        if not tree:
            print(f"Tree {tree_name} not found in {filename}")
            continue

        # Loop over entries
        found_nan = False
        for entry in tree:
            for branch in tree.GetListOfBranches():
                val = getattr(entry, branch.GetName(), None)
                if isinstance(val, float) and math.isnan(val):
                    found_nan = True
                    break
            if found_nan:
                break

        if found_nan:
            print(f"❌ NaN found in file: {filename}")
            bad_files.append(filename)
        else:
            print(f"✅ No NaN in file: {filename}")

        file.Close()

print("\nSummary of bad files with NaN:")
for bad in bad_files:
    print(bad)

