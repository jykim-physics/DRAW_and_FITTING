import ROOT

f = ROOT.TFile.Open("/share/storage/jykim/plots/MC15ri/etapip/gg/generic/fitresult/MC15ri_1ab_etapip_gg_fit_tight_v2_fitv6.root")
# f = ROOT.TFile.Open("/media/jykim/T7/saved_plots/storage_plots/plots/MC15ri/etapip/gg/generic/fitresult/MC15ri_1ab_etapip_gg_fit_tight_v2_fitv8.root")
# f = ROOT.TFile.Open("/media/jykim/T7/saved_plots/storage_plots/plots/MC15ri/etapip/gg/generic/fitresult/MC15ri_1ab_etapip_gg_fit_tight_v2_fitv9.root")

# f = ROOT.TFile.Open("/media/jykim/T7/saved_plots/storage_plots/plots/MC15ri/etapip/gg/generic/fitresult/MC15ri_1ab_etapip_gg_fit_tight_v2_fitv3.root")

result_object1 = ROOT.gDirectory.Get("jykim")
#fit_params = result_object1.getParameters() 
f.Close()
result_object1.Print("v")

float_fit_args = result_object1.floatParsFinal()
float_fit_args.Print()

float_fit_args_init = result_object1.floatParsInit()
float_fit_args_init.Print()

const_fit_args = result_object1.constPars()
const_fit_args.Print()



