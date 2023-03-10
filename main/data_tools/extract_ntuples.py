import pandas as pd
import numpy as np
import ROOT

def get_pd(file, tree=str, base_filter=str, variables=list):
    
    tree=tree
    f = file
    base_filter  = base_filter    
    
    ROOT_df_start = ROOT.RDataFrame(tree, f)  
    col_dict  = ROOT_df_start.AsNumpy(variables)
    
    if base_filter !=None:
        ROOT_df_filtered  = ROOT_df_start.Filter(base_filter)                            
        col_dict  = ROOT_df_filtered.AsNumpy(variables)
    
    pd_df  = pd.DataFrame(col_dict)
    
    return pd_df

def get_np(file:str, tree=str, base_filter=str, variables=list):
    
    tree=tree
    f = file
    base_filter  = base_filter    
    
    ROOT_df_start = ROOT.RDataFrame(tree, f)  
    
    if base_filter !=None:
        ROOT_df_filtered  = ROOT_df_start.Filter(base_filter)                            
        np_array = ROOT_df_filtered.AsNumpy(variables)
    else:
        np_array = ROOT_df_start.AsNumpy(variables)
    
    return np_array
