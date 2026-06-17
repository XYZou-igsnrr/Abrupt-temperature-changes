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
import matplotlib.colors as mcolors
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from scipy.stats import linregress
import matplotlib.patches as mpatches
import pymannkendall as mk


current_directory = os.path.dirname(os.path.abspath(__file__))


plt.rcParams.update({
    'font.size': 12,           
    'axes.titlesize': 12,      
    'axes.labelsize': 12,      
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
})

fig, axes = plt.subplots(nrows=8, ncols=3, figsize=(7, 10))
axes = axes.flatten()
axes[23].remove()

models=['ISD','CRUJRA','ERA5','ACCESS-ESM1-5','AWI-CM-1-1-MR','BCC-CSM2-MR','CanESM5','CESM2-WACCM','CMCC-ESM2','E3SM-1-0','EC-Earth3','FGOALS-g3','GFDL-ESM4',
        'IITM-ESM','INM-CM5-0','IPSL-CM6A','KACE-1-0-G','KIOST-ESM','MIROC6','MPI-ESM1-2-HR','NESM3','NorESM2','TaiESM1',]
labels = [f'{letter}' for letter in string.ascii_lowercase[:23]]

ATCw_color='#fdaba1'
ATCc_color='#a1c4d7'

all_data = []
for i, model in enumerate(models):
    print(model)

    if model=='CRUJRA':
        sudden_Tmean_change_csv =pd.read_csv("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/multi-threshold/CRUJRA_multi_sudden_tmp_change_±10°C_1970_2020.csv")
        Global_ATCw = sudden_Tmean_change_csv ['Global_ATCw']*365
        Global_ATCc = sudden_Tmean_change_csv ['Global_ATCc']*365
        NH_ATCw    = sudden_Tmean_change_csv ['Northern_ATCw']*365
        NH_ATCc    = sudden_Tmean_change_csv ['Northern_ATCc']*365
        SH_ATCw    = sudden_Tmean_change_csv ['Southern_ATCw']*365
        SH_ATCc    = sudden_Tmean_change_csv ['Southern_ATCc']*365

        #cal trend
        Global_ATCw_slope, Global_ATCw_pValue, = mk.original_test(Global_ATCw).slope, mk.original_test(Global_ATCw).p,
        Global_ATCc_slope, Global_ATCc_pValue, = mk.original_test(Global_ATCc).slope, mk.original_test(Global_ATCc).p,
        Northern_ATCw_slope, Northern_ATCw_pValue, = mk.original_test(NH_ATCw).slope, mk.original_test(NH_ATCw).p,
        Northern_ATCc_slope, Northern_ATCc_pValue, = mk.original_test(NH_ATCc).slope, mk.original_test(NH_ATCc).p,
        Southern_ATCw_slope, Southern_ATCw_pValue, = mk.original_test(SH_ATCw).slope, mk.original_test(SH_ATCw).p,
        Southern_ATCc_slope, Southern_ATCc_pValue, = mk.original_test(SH_ATCc).slope, mk.original_test(SH_ATCc).p,

        Global_ATCw_slope=Global_ATCw_slope if Global_ATCw_pValue < 0.05 else np.nan
        Global_ATCc_slope=Global_ATCc_slope if Global_ATCc_pValue < 0.05 else np.nan
        Northern_ATCw_slope=Northern_ATCw_slope if Northern_ATCw_pValue < 0.05 else np.nan
        Northern_ATCc_slope=Northern_ATCc_slope if Northern_ATCc_pValue < 0.05 else np.nan
        Southern_ATCw_slope=Southern_ATCw_slope if Southern_ATCw_pValue < 0.05 else np.nan
        Southern_ATCc_slope=Southern_ATCc_slope if Southern_ATCc_pValue < 0.05 else np.nan


    elif model=='ERA5':
        sudden_Tmean_change_csv = pd.read_csv("/data1/zxy/sudden_temp_change/ERA5_tmp/multi-threshold/ERA5_T_sudden_change_±10°C_1970_2020.csv")
        Global_ATCw = sudden_Tmean_change_csv ['Global_ATCw']*365
        Global_ATCc = sudden_Tmean_change_csv ['Global_ATCc']*365
        NH_ATCw    = sudden_Tmean_change_csv ['Northern_ATCw']*365
        NH_ATCc    = sudden_Tmean_change_csv ['Northern_ATCc']*365
        SH_ATCw    = sudden_Tmean_change_csv ['Southern_ATCw']*365
        SH_ATCc    = sudden_Tmean_change_csv ['Southern_ATCc']*365

        #cal trend
        Global_ATCw_slope, Global_ATCw_pValue, = mk.original_test(Global_ATCw).slope, mk.original_test(Global_ATCw).p,
        Global_ATCc_slope, Global_ATCc_pValue, = mk.original_test(Global_ATCc).slope, mk.original_test(Global_ATCc).p,
        Northern_ATCw_slope, Northern_ATCw_pValue, = mk.original_test(NH_ATCw).slope, mk.original_test(NH_ATCw).p,
        Northern_ATCc_slope, Northern_ATCc_pValue, = mk.original_test(NH_ATCc).slope, mk.original_test(NH_ATCc).p,
        Southern_ATCw_slope, Southern_ATCw_pValue, = mk.original_test(SH_ATCw).slope, mk.original_test(SH_ATCw).p,
        Southern_ATCc_slope, Southern_ATCc_pValue, = mk.original_test(SH_ATCc).slope, mk.original_test(SH_ATCc).p,

        Global_ATCw_slope=Global_ATCw_slope if Global_ATCw_pValue < 0.05 else np.nan
        Global_ATCc_slope=Global_ATCc_slope if Global_ATCc_pValue < 0.05 else np.nan
        Northern_ATCw_slope=Northern_ATCw_slope if Northern_ATCw_pValue < 0.05 else np.nan
        Northern_ATCc_slope=Northern_ATCc_slope if Northern_ATCc_pValue < 0.05 else np.nan
        Southern_ATCw_slope=Southern_ATCw_slope if Southern_ATCw_pValue < 0.05 else np.nan
        Southern_ATCc_slope=Southern_ATCc_slope if Southern_ATCc_pValue < 0.05 else np.nan


    elif model=='ISD':
        sudden_Tmean_change_csv = pd.read_csv("/data1/zxy/sudden_temp_change/ISD-global-daily/multi-threshold/multi_sudden_tmp_change_±10°C.csv")
        Global_ATCw = 365*sudden_Tmean_change_csv ['ATCw_count']/sudden_Tmean_change_csv ['obs_count']
        Global_ATCc = 365*sudden_Tmean_change_csv ['ATCc_count']/sudden_Tmean_change_csv ['obs_count']
        NH_ATCw = 365*sudden_Tmean_change_csv ['ATCw_Northern']/sudden_Tmean_change_csv ['obs_count_Northern']
        NH_ATCc = 365*sudden_Tmean_change_csv ['ATCc_Northern']/sudden_Tmean_change_csv ['obs_count_Northern']
        SH_ATCw = 365*sudden_Tmean_change_csv ['ATCw_Southern']/sudden_Tmean_change_csv ['obs_count_Southern']
        SH_ATCc = 365*sudden_Tmean_change_csv ['ATCc_Southern']/sudden_Tmean_change_csv ['obs_count_Southern']


        #cal trend
        Global_ATCw_slope, Global_ATCw_pValue, = mk.original_test(Global_ATCw).slope, mk.original_test(Global_ATCw).p,
        Global_ATCc_slope, Global_ATCc_pValue, = mk.original_test(Global_ATCc).slope, mk.original_test(Global_ATCc).p,
        Northern_ATCw_slope, Northern_ATCw_pValue, = mk.original_test(NH_ATCw).slope, mk.original_test(NH_ATCw).p,
        Northern_ATCc_slope, Northern_ATCc_pValue, = mk.original_test(NH_ATCc).slope, mk.original_test(NH_ATCc).p,
        Southern_ATCw_slope, Southern_ATCw_pValue, = mk.original_test(SH_ATCw).slope, mk.original_test(SH_ATCw).p,
        Southern_ATCc_slope, Southern_ATCc_pValue, = mk.original_test(SH_ATCc).slope, mk.original_test(SH_ATCc).p,

        Global_ATCw_slope=Global_ATCw_slope if Global_ATCw_pValue < 0.05 else np.nan
        Global_ATCc_slope=Global_ATCc_slope if Global_ATCc_pValue < 0.05 else np.nan
        Northern_ATCw_slope=Northern_ATCw_slope if Northern_ATCw_pValue < 0.05 else np.nan
        Northern_ATCc_slope=Northern_ATCc_slope if Northern_ATCc_pValue < 0.05 else np.nan
        Southern_ATCw_slope=Southern_ATCw_slope if Southern_ATCw_pValue < 0.05 else np.nan
        Southern_ATCc_slope=Southern_ATCc_slope if Southern_ATCc_pValue < 0.05 else np.nan


    else:
        sudden_Tmean_change_csv = pd.read_csv("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/multi-threshold/"+str(model)+"_T_sudden_change_±10°C_1970_2015.csv")
        Global_ATCw = sudden_Tmean_change_csv ['Global_ATCw']*365
        Global_ATCc = sudden_Tmean_change_csv ['Global_ATCc']*365
        NH_ATCw     = sudden_Tmean_change_csv ['Northern_ATCw']*365
        NH_ATCc     = sudden_Tmean_change_csv ['Northern_ATCc']*365
        SH_ATCw     = sudden_Tmean_change_csv ['Southern_ATCw']*365
        SH_ATCc     = sudden_Tmean_change_csv ['Southern_ATCc']*365
    
        years = np.arange(1970, 2015)
        Global_ATCw_slope, Global_ATCw_pValue, = mk.original_test(Global_ATCw).slope, mk.original_test(Global_ATCw).p,
        Global_ATCc_slope, Global_ATCc_pValue, = mk.original_test(Global_ATCc).slope, mk.original_test(Global_ATCc).p,
        Northern_ATCw_slope, Northern_ATCw_pValue, = mk.original_test(NH_ATCw).slope, mk.original_test(NH_ATCw).p,
        Northern_ATCc_slope, Northern_ATCc_pValue, = mk.original_test(NH_ATCc).slope, mk.original_test(NH_ATCc).p,
        Southern_ATCw_slope, Southern_ATCw_pValue, = mk.original_test(SH_ATCw).slope, mk.original_test(SH_ATCw).p,
        Southern_ATCc_slope, Southern_ATCc_pValue, = mk.original_test(SH_ATCc).slope, mk.original_test(SH_ATCc).p,
    
        Global_ATCw_slope=Global_ATCw_slope if Global_ATCw_pValue < 0.05 else np.nan
        Global_ATCc_slope=Global_ATCc_slope if Global_ATCc_pValue < 0.05 else np.nan
        Northern_ATCw_slope=Northern_ATCw_slope if Northern_ATCw_pValue < 0.05 else np.nan
        Northern_ATCc_slope=Northern_ATCc_slope if Northern_ATCc_pValue < 0.05 else np.nan
        Southern_ATCw_slope=Southern_ATCw_slope if Southern_ATCw_pValue < 0.05 else np.nan
        Southern_ATCc_slope=Southern_ATCc_slope if Southern_ATCc_pValue < 0.05 else np.nan


    all_data.extend([
            {'Model': model, 'Region': 'Globe', 'Type':  'ATCw mean-then-trend', 'Value': Global_ATCw_slope,},
            {'Model': model, 'Region': 'NH'    , 'Type': 'ATCw mean-then-trend', 'Value': Northern_ATCw_slope,},
            {'Model': model, 'Region': 'SH'    , 'Type': 'ATCw mean-then-trend', 'Value': Southern_ATCw_slope,},

            {'Model': model, 'Region': 'Globe', 'Type':  'ATCc mean-then-trend', 'Value': Global_ATCc_slope,},
            {'Model': model, 'Region': 'NH'    , 'Type': 'ATCc mean-then-trend', 'Value': Northern_ATCc_slope,},
            {'Model': model, 'Region': 'SH'    , 'Type': 'ATCc mean-then-trend', 'Value': Southern_ATCc_slope,},
        ])

    width = 0.2
    region = ['Globe', 'NH', 'SH']

    axes[i].bar(0 - width/2, Global_ATCw_slope,   width,  label='Globe ATCw', color=ATCw_color, )
    axes[i].bar(0 + width/2, Global_ATCc_slope,   width,  label='Globe ATCc', color=ATCc_color, )
    axes[i].bar(1 - width/2, Northern_ATCw_slope, width,  label='NH ATCw', color=ATCw_color, )
    axes[i].bar(1 + width/2, Northern_ATCc_slope, width,  label='NH ATCc', color=ATCc_color, )
    axes[i].bar(2 - width/2, Southern_ATCw_slope, width,  label='SH ATCw', color=ATCw_color, )
    axes[i].bar(2 + width/2, Southern_ATCc_slope, width,  label='SH ATCc', color=ATCc_color, )

    

    axes[i].set_ylabel('')
    axes[i].set_ylim(-0.026, 0.026)
    yticks=[-0.02, 0, 0.02]
    if i % 3 == 0:
        axes[i].set_yticks(yticks)
        axes[i].set_yticklabels([f'{t:.2f}'.replace('-0', '0') if t != 0 else '0' for t in yticks])
        axes[i].tick_params(axis='y', labelleft=True, left=True,)
    else:
        axes[i].tick_params(axis='y', labelleft=False, left=False)
    if i >=20:
        axes[i].set_xticks(np.arange(len(region)))
        axes[i].set_xticklabels(region)
        axes[i].tick_params(axis='x', labelbottom=True, bottom=True,)
    else:
        axes[i].tick_params(axis='x', labelbottom=False, bottom=False)
    axes[i].tick_params(axis='both', direction='out', length=5, width=1)
    axes[i].set_xlim(-0.6, 2 + 0.6)
    axes[i].axhline(y=0, color='gray', linewidth=0.8, linestyle='-', alpha=0.7)
    axes[i].set_title(str(model),y=0.75)
    axes[i].text(0.05, 0.80, f"{labels[i]}", transform=axes[i].transAxes, fontsize=axes[i].title.get_fontsize()+2, fontweight='bold', verticalalignment='bottom', horizontalalignment='left')


df = pd.DataFrame(all_data)
print(df.head(18).sort_values(['Model', 'Region']))

exclude_models = ['ISD', 'CRUJRA', 'ERA5']
df_filtered = df[~df['Model'].isin(exclude_models)]

cmip6_avg = df_filtered.groupby(['Region', 'Type'], as_index=False)['Value'].mean()
cmip6_avg['Model'] = 'CMIP6'
print(cmip6_avg)


axes[0].set_ylabel('ATC trend (yr⁻²)',)

legend_handles = []
legend_handles.append(mpatches.Patch(color=ATCw_color,  label='ATCw'))
legend_handles.append(mpatches.Patch(color=ATCc_color,  label='ATCc'))
axes[-2].legend(handles=legend_handles,loc='center right', bbox_to_anchor=(1.65, 0.31),alignment='left' )

plt.subplots_adjust(left=0.12, right=0.98, bottom=0.04, top=0.98, wspace=0, hspace=0.0)

script_name = os.path.splitext(os.path.basename(__file__))[0]
plt.savefig(str(current_directory)+f"/{script_name}.png", dpi=300)

#plt.show()














