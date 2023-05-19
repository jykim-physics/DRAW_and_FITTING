import numpy as np

def make_data_weight(data_list, scale):
    weights = None
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
    return weights
