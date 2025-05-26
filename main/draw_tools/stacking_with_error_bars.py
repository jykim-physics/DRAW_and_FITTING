import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from scipy import stats

try:
    # plt.style.use('belle2')
    # plt.style.use('belle2_serif')
    plt.style.use('belle2_modern')
except OSError:
    print("Please install belle2 matplotlib style")   
px = 1/plt.rcParams['figure.dpi']

from main.data_tools.extract_ntuples import get_pd, get_np
from main.draw_tools.decorations import b2helix, watermark, lumi
from main.data_tools.error_bars import make_data_weight


def MC_stack_plot_old(data, var, scale, xrange, nbins, xlabel="", labels=list,title="", unit = "GeV/c^2",save_repo='',force_range=tuple, ncol=2, luminosity="", legend_loc=""):
 
    data_list  = data

    weights = make_data_weight(data_list, scale)
    colors=b2helix(len(labels))
    
    xbins = np.linspace(*xrange, nbins+1)
    bin_width = xbins[1] - xbins[0]
    bin_mids = (xbins[1:] + xbins[:-1])/2
    
    x = data_list
    only_list = []
    for nums in x:
      for val in nums:
        only_list.append(val)
    y = weights
    only_list2 = []
    for nums in y:
      for val in nums:
        only_list2.append(val)
    np_only_list = np.array(only_list)
    np_only_list2 = np.array(only_list2)

    sum_w = np.sum(\
                np.array([stats.binned_statistic(np_only_list,np_only_list2, statistic="sum", bins=xbins)[0]]), axis=0)
    print(sum_w)
    print('fitst_bin_entries=' + str(sum_w[0]))
    sum_w2 = np.sum(\
                np.array([stats.binned_statistic(np_only_list,np_only_list2**2, statistic="sum", bins=xbins)[0]]), axis=0)
    fig = plt.figure(figsize=(10, 6))
    plt.hist(data_list, bins=xbins, histtype='stepfilled', stacked=True,label=labels,color=colors,edgecolor='black', weights = weights)
      
    ax = plt.gca()
    ax.bar(
                x = bin_mids,
                height=2 * np.sqrt(sum_w2),
                width=bin_width,
                bottom=sum_w - np.sqrt(sum_w2),
                color="black",
                hatch="///////",
                fill=False,
                lw=0,
                label="MC stat. unc."    
    )
    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width , box.height])
    # Put a legend to the right of the current axis
    # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))  
    if legend_loc != "":
        plt.legend(loc=legend_loc,prop={'size':13}, ncol = ncol)
    else:
        plt.legend(loc='upper right',prop={'size':13}, ncol = ncol)
        
    # watermark(t="",logo="MC15ri")
    # lumi(l=luminosity, px=0.033, py=0.839)
    # ex. luminosity="$5\; \mathrm{pb}^{-1}$"
    if luminosity != "":
        lumi(l=luminosity, px=0.033, py=0.90)

    ax.set_title(title)

    if sum_w[0]*1.2 == 0:
        pass
        ax.set_xlim(*force_range)
    else:
        max_entries = max(sum_w)

        # ax.set_ylim(0,max_entries*1.2)
        #ax.set_ylim(0,sum_w[0]*1.2)
        ax.set_xlim(*xrange)

    plt.xlabel(xlabel + r'$\; \mathrm{' + unit + r'}$');
    plt.ylabel('Entries'+' /' + '$(' + ' '  + "{0:.4f}".format(bin_width).rstrip('0').rstrip('.') + '\mathrm{' + unit  + '})$');
    if save_repo!='':
        plt.savefig(save_repo)
    plt.tight_layout()
    #plt.show()

def MC_stack_plot(data, var, scale, xrange, nbins, xlabel="", labels=None,
                  title="", unit="GeV/c^2", save_repo='', force_range=None,
                  ncol=2, luminosity="", legend_loc=""):
    
    if labels is None:
        labels = [f"MC {i}" for i in range(len(data))]
    
    # 설정
    colors = b2helix(len(labels))
    xbins = np.linspace(*xrange, nbins + 1)
    bin_width = xbins[1] - xbins[0]
    bin_mids = (xbins[:-1] + xbins[1:]) / 2

    # 데이터와 가중치 평탄화
    flat_data = np.concatenate(data)
    flat_weights = np.concatenate(make_data_weight(data, scale))

    # 스택된 히스토그램을 위한 bin별 합계 및 제곱합
    sum_w = stats.binned_statistic(flat_data, flat_weights, bins=xbins, statistic="sum")[0]
    sum_w2 = stats.binned_statistic(flat_data, flat_weights**2, bins=xbins, statistic="sum")[0]

    # 플롯
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(data, bins=xbins, weights=make_data_weight(data, scale),
            histtype='stepfilled', stacked=True, label=labels,
            color=colors, edgecolor='black')

    # MC 통계적 불확실성 시각화
    ax.bar(bin_mids, 2 * np.sqrt(sum_w2), width=bin_width,
           bottom=sum_w - np.sqrt(sum_w2), color='black',
           hatch='///////', fill=False, lw=0, label="MC stat. unc.")

    # 범례
    if legend_loc:
        ax.legend(loc=legend_loc, prop={'size':13}, ncol=ncol)
    else:
        ax.legend(loc='upper right', prop={'size':13}, ncol=ncol)

    # 타이틀, 축 설정
    ax.set_title(title)
    ax.set_xlabel(f"{xlabel} $\\; \\mathrm{{{unit}}}$")
    ax.set_ylabel(f"Entries / $({bin_width:.4f} \\; \\mathrm{{{unit}}})$")
    
    # x축 범위
    if sum_w[0]*1.2 == 0 and force_range:
        ax.set_xlim(*force_range)
    else:
        ax.set_xlim(*xrange)

    # 루미노시티 워터마크
    if luminosity:
        lumi(l=luminosity, px=0.033, py=0.90)

    # 저장
    plt.tight_layout()
    if save_repo:
        plt.savefig(save_repo)

def MC_stack_plot_weight(data, var, scale, xrange, nbins, xlabel="", labels=None,
                  title="", unit="GeV/c^2", save_repo='', force_range=None,
                  ncol=2, luminosity="", legend_loc=""):

    if labels is None:
        labels = [f"MC {i}" for i in range(len(data))]

    colors = b2helix(len(labels))
    xbins = np.linspace(*xrange, nbins + 1)
    bin_width = xbins[1] - xbins[0]
    bin_mids = (xbins[:-1] + xbins[1:]) / 2

    # pandas Series 또는 리스트를 numpy 배열로 변환
    flat_data = np.concatenate([np.asarray(d) for d in data])
    flat_weights = np.concatenate([np.asarray(w) for w in scale])

    # bin 단위 가중합 및 제곱합 계산
    sum_w = stats.binned_statistic(flat_data, flat_weights, bins=xbins, statistic="sum")[0]
    sum_w2 = stats.binned_statistic(flat_data, flat_weights**2, bins=xbins, statistic="sum")[0]

    # 스택 히스토그램
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(data, bins=xbins, weights=scale,
            histtype='stepfilled', stacked=True, label=labels,
            color=colors, edgecolor='black')

    # 통계 불확실성 영역
    ax.bar(bin_mids, 2 * np.sqrt(sum_w2), width=bin_width,
           bottom=sum_w - np.sqrt(sum_w2), color='black',
           hatch='///////', fill=False, lw=0, label="MC stat. unc.")

    # 범례 설정
    if legend_loc:
        ax.legend(loc=legend_loc, prop={'size':13}, ncol=ncol)
    else:
        ax.legend(loc='upper right', prop={'size':13}, ncol=ncol)

    # 타이틀 및 축 라벨
    ax.set_title(title)
    ax.set_xlabel(f"{xlabel} $\\; \\mathrm{{{unit}}}$")
    ax.set_ylabel(f"Entries / $({bin_width:.4f} \\; \\mathrm{{{unit}}})$")

    # X축 범위
    if sum_w[0]*1.2 == 0 and force_range:
        ax.set_xlim(*force_range)
    else:
        ax.set_xlim(*xrange)

    # 루미노시티 워터마크
    if luminosity:
        lumi(l=luminosity, px=0.033, py=0.90)

    plt.tight_layout()
    if save_repo:
        plt.savefig(save_repo)


def MC_stack_plot_density(data, var, scale, xrange, nbins, xlabel="", labels=list,title="", unit = "GeV/c^2",save_repo='',force_range=tuple):

    colors=b2helix(len(labels))  
    xbins = np.linspace(*xrange, nbins+1)
    bin_width = xbins[1] - xbins[0]
    bin_mids = (xbins[1:] + xbins[:-1])/2
    data_list  = data
        
    values, bins, _ = plt.hist(data_list, bins=xbins, histtype='stepfilled', stacked=True,label=labels,color=colors,edgecolor='black',density=True)

    # area = sum(np.diff(bins)*values)
    # print('area = ' + str(area))
    # print('area2 = ' + str(sum(area)))    

    weights = make_data_weight(data_list, scale)

    
    x = data_list
    only_list = []
    for nums in x:
      for val in nums:
        only_list.append(val)
    y = weights
    only_list2 = []
    for nums in y:
      for val in nums:
        only_list2.append(val)
    np_only_list = np.array(only_list)
    np_only_list2 = np.array(only_list2)

    sum_w = np.sum(\
                np.array([stats.binned_statistic(np_only_list,np_only_list2, statistic="sum", bins=xbins)[0]]), axis=0)
    print(sum_w)
    print('fitst_bin_entries=' + str(sum_w[0]))
    sum_w2 = np.sum(\
                np.array([stats.binned_statistic(np_only_list,np_only_list2**2, statistic="sum", bins=xbins)[0]]), axis=0)
    
    
      
    ax = plt.gca()
    # ax.bar(
    #             x = bin_mids,
    #             height=2 * np.sqrt(sum_w2),
    #             width=bin_width,
    #             bottom=sum_w - np.sqrt(sum_w2),
    #             color="black",
    #             hatch="///////",
    #             fill=False,
    #             lw=0,
    #             label="MC stat. unc."    
    # )
    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width , box.height])
    # Put a legend to the right of the current axis
    # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))   
    # plt.legend(loc='upper right',prop={'size':13}, ncol = 2)
        
    # watermark(t="",logo="MC15ri")
    ax.set_title(title)

    
    # max_entries = max(values)
    # print(sum(values))
    # ax.set_ylim(0,max_entries*1.2)
    #ax.set_ylim(0,sum_w[0]*1.2)
    ax.set_xlim(*xrange)

    plt.xlabel(xlabel + r'$\; [\mathrm{' + unit + r'}]$');
    plt.ylabel('Entries'+' /' + '$(' + ' '  + "{0:.4f}".format(bin_width).rstrip('0').rstrip('.') + '\mathrm{' + unit  + '})$');
    plt.savefig(save_repo)
    plt.tight_layout()

#def 
