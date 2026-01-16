#!/bin/bash
python3 check_fit_results_MC15rd.py gg pip
#python3 check_fit_results_MC15rd.py pipipi pip
#python3 check_fit_results_MC15rd.py gg Kp
#python3 check_fit_results_MC15rd.py pipipi Kp


python3 plot_bdt_scan_FOM.py tmp_fitv12_results_MC15rd_pip_gg.txt etapip_gg
#python3 plot_bdt_scan_FOM.py tmp_fitv12_results_MC15rd_pip_pipipi.txt etapip_pipipi
#python3 plot_bdt_scan_FOM.py tmp_fitv12_results_MC15rd_Kp_gg.txt etapip_gg_K
#python3 plot_bdt_scan_FOM.py tmp_fitv12_results_MC15rd_Kp_pipipi.txt etapip_pipipi_K

python3  plot_bdt_scan_FOM_Ds.py tmp_fitv12_results_MC15rd_pip_gg.txt  etapip_gg
#python3  plot_bdt_scan_FOM_Ds.py tmp_fitv12_results_MC15rd_pip_pipipi.txt etapip_pipipi
#python3  plot_bdt_scan_FOM_Ds.py tmp_fitv12_results_MC15rd_Kp_gg.txt etapip_gg_K
#python3  plot_bdt_scan_FOM_Ds.py tmp_fitv12_results_MC15rd_Kp_pipipi.txt etapip_pipipi_K

