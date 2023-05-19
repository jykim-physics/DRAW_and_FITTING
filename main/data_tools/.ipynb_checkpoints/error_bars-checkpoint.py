import pandas as pd
import numpy as np
import ROOT
from scipy import stats

def sum_w(data, weights, bins): 

    sum_w = np.sum( 
                np.array([stats.binned_statistic(data, weights, statistic="sum", bins=bins)[0]], axis=0)    
    return sum_w 

def sum_w2(data, weights, bins): 

    sum_w2 = np.sum( 
                np.array([stats.binned_statistic(data, weights ** 2, statistic="sum", bins=bins)[0]], axis=0)    
    return sum_w2

        
def make_data_weight(data_list, scale):        
    if weights is None:
        weights = []
        for i,d in enumerate(data_list):
            wei = np.ones(len(d))
            if scale is not None:
                if isinstance(scale, int) or isinstance(scale, float):
                    if not isinstance(scale, bool):
                        wei *= scale
                elif isinstance(scale, dict):
                    assert cats[i] in scale.keys(), "Scale list must have same lenght as data"
                    wei *= scale[cats[i]]
                else:
                    print("Please provide int or float with scale")
            weights.append(wei)        
     return weight   

        
        
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

def get_pd_file_list(file_list=list, tree=str, base_filter=str, variables=list):

    tree=tree
    base_filter  = base_filter 
    
    names = ROOT.std.vector('string')()
    for n in file_list: names.push_back(n)

    ROOT_df_start = ROOT.RDataFrame(tree, names)    
    col_dict  = ROOT_df_start.AsNumpy(variables)
    
    if base_filter !=None:
        ROOT_df_filtered  = ROOT_df_start.Filter(base_filter)                            
        col_dict  = ROOT_df_filtered.AsNumpy(variables)
    
    pd_df  = pd.DataFrame(col_dict)
    
    return pd_df
