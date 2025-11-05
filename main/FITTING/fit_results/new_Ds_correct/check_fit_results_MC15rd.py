import ROOT
import os
import fnmatch


#gg_or_pipipi = "pipipi"
gg_or_pipipi = "gg"
Kp_or_pip = "pip"
#Kp_or_pip = "Kp"
input_dir = f"/share/storage/jykim/plots/MC15rd/eta{Kp_or_pip}/{gg_or_pipipi}/generic/fitresult/"
output_file = f"fitv8_results_MC15rd_{Kp_or_pip}_{gg_or_pipipi}.txt"
#output_file = f"test.txt"
#output_file = f"fitv10_results_MC15rd_{Kp_or_pip}_{gg_or_pipipi}.txt"

max_acp_ratio = max_acp_ds_ratio = max_n_total_ratio = max_n_total_ds_ratio = -1
min_acp_error = min_acp_ds_error = float('inf')
min_acp_file = min_acp_ds_file = max_acp_file = max_acp_ds_file = max_n_total_file = max_n_total_ds_file = ""
min_acp = min_acp_ds = None

root_files = []

#for root_file in os.listdir(input_dir):
#    if fnmatch.fnmatch(root_file, f"MC15rd_eta{Kp_or_pip}_{gg_or_pipipi}_fit_opt_loose_v7_fitv1_bdt_train_Dp_CMS_p_all_0.*.root"):
#        root_files.append(root_file)

# Regular expression to match filenames with two decimal places after the "0."
#pattern = f"MC15rd_eta{Kp_or_pip}_{gg_or_pipipi}_fit_opt_loose_v7_fitv1_bdt_train_Dp_CMS_p_all_0\.\d{{2}}\.root"
pattern = f"MC15rd_eta{Kp_or_pip}_{gg_or_pipipi}_fit_opt_loose_v7_fitv8_bdt_train_Dp_CMS_p_all_0.[0-9][0-9]_new_Ds_correct_weighted.root"
#pattern = f"MC15rd_eta{Kp_or_pip}_{gg_or_pipipi}_fit_opt_loose_v7_fitv10_bdt_train_Dp_CMS_p_all_0.[0-9][0-9]_new_Ds_correct_weighted.root"

for root_file in os.listdir(input_dir):
    if fnmatch.fnmatch(root_file, pattern):
        root_files.append(root_file)

root_files.sort()
print(root_files)


with open(output_file, 'w') as out_f:
    out_f.write("File Name\tFit Status\tAcp ± Uncertainty\tAcp_Ds ± Uncertainty\tN_total ± Uncertainty\tN_total_Ds ± Uncertainty\tacp_ratio\tacp_ds_ratio\tn_total_ratio\tn_total_ds_ratio\tnbkg_total\tnbkg_total_error\n")

    for root_file in root_files:
        file_path = os.path.join(input_dir, root_file)
        f = ROOT.TFile(file_path)
        fit_result = f.Get("jykim")

        if not fit_result:
            print(f"Fit result object 'jykim' not found in {file_path}")
            continue

        fit_status = "Not Converged"
        covariance_status = "Bad Covariance"

        if fit_result.status() == 0:
            fit_status = "Converged"

        if fit_result.covQual() == 3:
            covariance_status = "Good Covariance"

        params = fit_result.floatParsFinal()

        acp = acp_error = None
        acp_ds = acp_ds_error = None
        n_total = n_total_error = None
        n_total_ds = n_total_ds_error = None

        acp_ratio = acp_ds_ratio = n_total_ratio = n_total_ds_ratio = None

        for i in range(params.getSize()):
            param = params[i]
            param_name = param.GetName()
            param_val = param.getVal()
            param_error = param.getError()

            if param_name == "Acp":
                acp = param_val
                acp_error = param_error
                acp_ratio = acp / acp_error if acp_error != 0 else 0
                if acp_ratio > max_acp_ratio:
                    max_acp_ratio = acp_ratio
                    max_acp_file = root_file
                if acp_error < min_acp_error:
                    min_acp_error = acp_error
                    min_acp = acp
                    min_acp_file = root_file

            elif param_name == "Acp_Ds":
                acp_ds = param_val
                acp_ds_error = param_error
                acp_ds_ratio = acp_ds / acp_ds_error if acp_ds_error != 0 else 0
                if acp_ds_ratio > max_acp_ds_ratio:
                    max_acp_ds_ratio = acp_ds_ratio
                    max_acp_ds_file = root_file
                if acp_ds_error < min_acp_ds_error:
                    min_acp_ds_error = acp_ds_error
                    min_acp_ds = acp_ds
                    min_acp_ds_file = root_file

            elif param_name == "N_total":
                n_total = param_val
                n_total_error = param_error
                n_total_ratio = n_total / n_total_error if n_total_error != 0 else 0
                if n_total_ratio > max_n_total_ratio:
                    max_n_total_ratio = n_total_ratio
                    max_n_total_file = root_file

            elif param_name == "N_total_Ds":
                n_total_ds = param_val
                n_total_ds_error = param_error
                n_total_ds_ratio = n_total_ds / n_total_ds_error if n_total_ds_error != 0 else 0
                if n_total_ds_ratio > max_n_total_ds_ratio:
                    max_n_total_ds_ratio = n_total_ds_ratio
                    max_n_total_ds_file = root_file

            elif param_name == "Nbkg_total":
                nbkg_total = param_val
                nbkg_total_error = param_error
                nbkg_total_ratio = nbkg_total / nbkg_total_error if nbkg_total_error != 0 else 0

        out_f.write(f"{root_file}\t{fit_status}({covariance_status})\t{acp} ± {acp_error}\t{acp_ds} ± {acp_ds_error}\t{n_total} ± {n_total_error}\t{n_total_ds} ± {n_total_ds_error}\t{acp_ratio}\t{acp_ds_ratio}\t{n_total_ratio}\t{n_total_ds_ratio}\t{nbkg_total} ± {nbkg_total_error}\n")

        f.Close()

    print(f"File with highest N_total/Uncertainty: {max_n_total_file} with ratio {max_n_total_ratio}")
    print(f"File with highest N_total_Ds/Uncertainty: {max_n_total_ds_file} with ratio {max_n_total_ds_ratio}")
    print(f"File with lowest Acp uncertainty: {min_acp_file} with uncertainty {min_acp_error} (Acp = {min_acp})")
    print(f"File with lowest Acp_Ds uncertainty: {min_acp_ds_file} with uncertainty {min_acp_ds_error} (Acp_Ds = {min_acp_ds})")
    print(f"Results saved in {output_file}")

