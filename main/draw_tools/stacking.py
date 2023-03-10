from main.data_tools.extract_ntuples import get_pd, get_np


def make_dict_data(file_name:str, tree:str, variables:list, cut):
 
    dict_data = {}
    pd_data = get_pd(file=file_name, tree=tree,base_filter=cut,variables=variables)

    for var in variables:
        dict_data[var] = pd_data[var]
    return dict_data

def make_dict_data_list(proj_name:str , variables:list, tree:str, cut:str):
    
    #global make_dict_data
    data_list = list
    dict_data_list = dict.fromkeys(variables, )
    base_loc =  '/media/jykim/T7/storage/01_recon/'
    base_loc += proj_name
    
    labels = ['mixed', 'charged', 'uubar', 'ddbar', 'ssbar', 'taupair','ccbar']
    
    for label in labels:
        for var in variables:

            temp_loc = base_loc + '/' + label + '/recon_*.root'
            #print(temp_loc)
            label_data = make_dict_data(temp_loc, tree, variables,cut=cut)

            print(label_data)
            dict_data_list[var] = list
            dict_data_list[var].append(label_data[var])
            #temp_pd = 

    return dict_data_list

#def 