import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import netCDF4 as nc
import matplotlib.gridspec as gridspec
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.lines import Line2D
from scipy.ndimage import uniform_filter1d
import string
from matplotlib.colors import ListedColormap, BoundaryNorm
import sys


current_directory = os.path.dirname(os.path.abspath(__file__))

#==========================================load data===========================================#


fig, axes = plt.subplots(nrows=6, ncols=4, figsize=(9, 11),)#figsize=(width, heigh)
axes = axes.flatten()


models=['ACCESS-ESM1-5','AWI-CM-1-1-MR','BCC-CSM2-MR','CanESM5','CESM2-WACCM','CMCC-ESM2','E3SM-1-0','EC-Earth3','FGOALS-g3','GFDL-ESM4',
        'IITM-ESM','INM-CM5-0','IPSL-CM6A','KACE-1-0-G','KIOST-ESM','MIROC6','MPI-ESM1-2-HR','NESM3','NorESM2','TaiESM1',
        'CRUJRA','ERA5',]
labels = [f'{letter}' for letter in string.ascii_lowercase[:23]]


for i, model in enumerate(models):
    print(model)
    if model=='CRUJRA':
        dataset_ave   = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/CRUJRA_sudden_T_change_freq_1970_2020.nc")
        ATCw_ave      = dataset_ave['T_change_up_freq'][:]*364
        ATCc_ave      = dataset_ave['T_change_down_freq'][:]*364
        dataset_slope = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/CRUJRA_sudden_T_change_freq_trend_±10°C_1970_2020.nc")
        ATCw_slope    = dataset_slope['T_change_up_freq_trend_slope'][:]*364
        ATCc_slope    = dataset_slope['T_change_down_freq_trend_slope'][:]*364
        ATCw_pvalue   = dataset_slope['T_change_up_freq_trend_p_value'][:]
        ATCc_pvalue   = dataset_slope['T_change_down_freq_trend_p_value'][:]
        if 'latitude' in dataset.variables:
            lat = dataset['latitude'][:]
            lon = dataset['longitude'][:]
        elif 'lat' in dataset.variables:
            lat = dataset['lat'][:]
            lon = dataset['lon'][:]

    elif model=='ERA5':
        dataset   = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/ERA5_sudden_T_change_freq_1970_2020.nc")
        ATCw_ave      = dataset['T_change_up_freq'][:]*364
        ATCc_ave      = dataset['T_change_down_freq'][:]*364
        ATCw_slope    = dataset['T_change_up_freq_trend_slpoe'][:]*364
        ATCc_slope    = dataset['T_change_down_freq_trend_slpoe'][:]*364
        ATCw_pvalue   = dataset['T_change_up_freq_trend_p_value'][:]
        ATCc_pvalue   = dataset['T_change_down_freq_trend_p_value'][:]

        if 'latitude' in dataset.variables:
            lat = dataset['latitude'][:]
            lon = dataset['longitude'][:]
        elif 'lat' in dataset.variables:
            lat = dataset['lat'][:]
            lon = dataset['lon'][:]

    else:
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/T_change_freq_"+str(model)+"_yearly_1970-2015-rescale.nc")
        ATCw_ave    = dataset['T_change_up_freq'][:]*364
        ATCc_ave    = dataset['T_change_down_freq'][:]*364
        ATCw_slope    = dataset['T_change_up_freq_trend_slpoe'][:]*364
        ATCc_slope    = dataset['T_change_down_freq_trend_slpoe'][:]*364
        ATCw_pvalue   = dataset['T_change_up_freq_trend_p_value'][:]
        ATCc_pvalue   = dataset['T_change_down_freq_trend_p_value'][:]
        ATCw_ave=np.nanmean(ATCw_ave,axis=0)
        ATCc_ave=np.nanmean(ATCc_ave,axis=0)


        if 'latitude' in dataset.variables:
            lat = dataset['latitude'][:]
            lon = dataset['longitude'][:]
        elif 'lat' in dataset.variables:
            lat = dataset['lat'][:]
            lon = dataset['lon'][:]

    ATCw_ave[(lat < -60),:] = np.nan
    ATCc_ave[(lat < -60),:] = np.nan
    ATCw_slope[(lat < -60),:] = np.nan
    ATCc_slope[(lat < -60),:] = np.nan

    mask_ATCw=np.isnan(ATCw_ave) | np.isnan(ATCw_slope) | (np.array(ATCw_pvalue)> 0.05) .astype(bool)
    mask_ATCc=np.isnan(ATCc_ave) | np.isnan(ATCc_slope) | (np.array(ATCc_pvalue)> 0.05) .astype(bool)
    #print("ATCw_pvalue",np.sum(np.array(ATCw_pvalue)< 0.05))

    ATCw_ave = ATCw_ave[~mask_ATCw]
    ATCc_ave = ATCc_ave[~mask_ATCc]
    ATCw_slope = ATCw_slope[~mask_ATCw]
    ATCc_slope = ATCc_slope[~mask_ATCc]

    ATCw_ave=ATCw_ave.flatten()
    ATCc_ave=ATCc_ave.flatten()
    ATCw_slope=ATCw_slope.flatten()
    ATCc_slope=ATCc_slope.flatten()

#    print("ATCw_ave",len(ATCw_ave))
#    print("ATCw_slope",len(ATCw_slope))
#    print("ATCc_ave",len(ATCc_ave))
#    print("ATCc_slope",len(ATCc_slope))
    sys.stdout.flush()


    sns.regplot(x=ATCw_ave, y=ATCw_slope, scatter_kws={'color': 'mistyrose', 'alpha': 0.4, 's': 4,'edgecolors': 'none'},  # 更浅的红
                line_kws={'color': 'red', 'linewidth': 1, 'label': 'ATCw'}, ax=axes[i])

    sns.regplot(x=ATCc_ave, y=ATCc_slope, scatter_kws={'color': 'lightblue', 'alpha': 0.4, 's': 4,'edgecolors': 'none'},
                line_kws={'color': 'blue', 'linewidth': 1, 'label': 'ATCc'}, ax=axes[i])

    axes[i].axhline(y=0, color='gray', linestyle='--', linewidth=0.5)

    axes[i].set_xlim(-0.2, 24)
    axes[i].set_ylim(-0.22, 0.22)
    axes[i].set_xticks([0, 10, 20])
    axes[i].set_yticks([-0.2,-0.1, 0, 0.1,0.2])
                
    title_text = axes[i].set_title(str(model))
    axes[i].text(0, 1.08, f"{labels[i]}", transform=axes[i].transAxes, fontsize=axes[i].title.get_fontsize()+2, fontweight='bold',verticalalignment='bottom', horizontalalignment='left')
                

axes[0].set_ylabel('ATC trend (yr⁻²)')
axes[20].set_xlabel('ATC occurrence (yr⁻¹)')
axes[22].remove()
axes[23].remove()

plt.subplots_adjust(left=0.08, right=0.98, bottom=0.05, top=0.96, wspace=0.25, hspace=0.45)

#axes[21].legend(loc='center right', bbox_to_anchor=(1.7, 0.5),)
axes[21].legend(handles=[
    Line2D([0], [0], marker='o', color='none', markerfacecolor='mistyrose', markeredgecolor='none', alpha=0.6,label='ATCw grid cells'),
    Line2D([0], [0], marker='o', color='none', markerfacecolor='lightblue', markeredgecolor='none', alpha=0.6,label='ATCc grid cells'),
    Line2D([0], [1], color='red', label='ATCw regression line'),
    Line2D([0], [1], color='blue', label='ATCc regression line')
], loc='center left', bbox_to_anchor=(1.1, 0.5),)

script_name = os.path.splitext(os.path.basename(__file__))[0]
fig.savefig(str(current_directory)+f"/{script_name}.png", dpi=300)
#plt.show()
    
    










