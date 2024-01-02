import pandas as pd 

def cut_dfs_7types(cut, pd_ccbar, pd_uubar,pd_ddbar,pd_ssbar,pd_charged, pd_mixed, pd_taupair):
    pd_ccbar_after = pd_ccbar.query(cut)
    pd_uubar_after = pd_uubar.query(cut)
    pd_ddbar_after = pd_ddbar.query(cut)
    pd_ssbar_after = pd_ssbar.query(cut)
    pd_charged_after = pd_charged.query(cut)
    pd_mixed_after = pd_mixed.query(cut)
    pd_taupair_after = pd_taupair.query(cut)

    return pd_ccbar_after, pd_uubar_after , pd_ddbar_after , pd_ssbar_after , \
        pd_charged_after , pd_mixed_after , pd_taupair_after

def cut_dfs_generic_Vpi0eta(cut, pd_ccbar_Vpi0, pd_ccbar_Veta, pd_uubar,pd_ddbar,pd_ssbar,pd_charged, pd_mixed, pd_taupair,):
    pd_ccbar_Vpi0_after = pd_ccbar_Vpi0.query(cut)
    pd_ccbar_Veta_after = pd_ccbar_Veta.query(cut)
    pd_uubar_after = pd_uubar.query(cut)
    pd_ddbar_after = pd_ddbar.query(cut)
    pd_ssbar_after = pd_ssbar.query(cut)
    pd_charged_after = pd_charged.query(cut)
    pd_mixed_after = pd_mixed.query(cut)
    pd_taupair_after = pd_taupair.query(cut)

    return pd_ccbar_Vpi0_after, pd_ccbar_Veta_after, pd_uubar_after , pd_ddbar_after , pd_ssbar_after , \
        pd_charged_after , pd_mixed_after , pd_taupair_after


def cut_dfs_4types(cut, pd_ccbar, pd_uds,pd_charged, pd_mixed):
    pd_ccbar_after = pd_ccbar.query(cut)
    pd_uds_after = pd_uds.query(cut)
    pd_charged_after = pd_charged.query(cut)
    pd_mixed_after = pd_mixed.query(cut)

    return pd_ccbar_after, pd_uds_after , \
        pd_charged_after , pd_mixed_after