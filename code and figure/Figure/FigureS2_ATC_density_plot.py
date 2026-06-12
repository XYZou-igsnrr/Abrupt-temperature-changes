# -*- coding: utf-8 -*-
import netCDF4 as nc
import numpy as np
import os
import matplotlib.pyplot as plt
import cartopy.feature as cfeature
from IPython.display import display, Math
import cartopy.crs as ccrs
import csv
import matplotlib.colors as mcolors
import pandas as pd
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.ticker as mticker
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FormatStrFormatter
import seaborn as sns
from scipy.stats import gaussian_kde
import scipy.stats as stats


def density(x,y):

    xy = np.vstack([x, y])
    kde = gaussian_kde(xy)  # 使用核密度估计计算散点的密度
    density = kde(xy)  # 返回每个
    print('density finish')
    return density
    
    
def calculate_mean_se(data):

    if not isinstance(data, np.ndarray):
        data = np.array(data)

    # 获取非NaN值
    valid_values = data[~np.isnan(data)]
    
    if valid_values.size == 0:
        return np.nan, np.nan
    elif valid_values.size < 2:
        return valid_values.mean(), np.nan
      
    mean = np.mean(valid_values)
    std= np.std(valid_values, ddof=1) # 样本标准差（更常用）
    se = stats.sem(valid_values)  # 标准误差
    ci = se * stats.t.ppf(0.975, len(valid_values)-1)  # 95% C
    
    return mean,std ,se, ci


current_directory = os.path.dirname(os.path.abspath(__file__))

#=========================================load ISD data===================================================#
station_up = pd.read_csv("/data1/zxy/sudden_temp_change/ISD-global-daily/station_sudden_change_+10°C_after_1973.csv")
station_down = pd.read_csv("/data1/zxy/sudden_temp_change/ISD-global-daily/station_sudden_change_-10°C_after_1973.csv")

station_up = station_up[station_up['obs_count'] >= 1000]
station_down = station_down[station_down['obs_count'] >= 1000]

station_combined = pd.merge(
    station_up,
    station_down,
    on=['station', 'lat', 'lon'],
    suffixes=('_up', '_down'),
    how='inner'
)
station_combined['ATC'] = station_combined['mean_T_ratio_up']*365 + station_combined['mean_T_ratio_down']*365


global_ATCc_ISD  ,global_ATCc_ISD_std,global_ATCc_ISD_se,global_ATCc_ISD_ci    =calculate_mean_se(station_combined['mean_T_ratio_down']*365)
Northern_ATCc_ISD,Northern_ATCc_ISD_std,Northern_ATCc_ISD_se,Northern_ATCc_ISD_ci=calculate_mean_se(station_combined[station_combined['lat'] > 0]['mean_T_ratio_down']*365)
Southern_ATCc_ISD,Southern_ATCc_ISD_std,Southern_ATCc_ISD_se,Southern_ATCc_ISD_ci=calculate_mean_se(station_combined[(station_combined['lat'] < 0) & (station_combined['lat'] > -60)]['mean_T_ratio_down']*365)

global_ATCw_ISD  ,global_ATCw_ISD_std,global_ATCw_ISD_se,global_ATCw_ISD_ci    =calculate_mean_se(station_combined['mean_T_ratio_up']*365)
Northern_ATCw_ISD,Northern_ATCw_ISD_std,Northern_ATCw_ISD_se,Northern_ATCw_ISD_ci=calculate_mean_se(station_combined[station_combined['lat'] > 0]['mean_T_ratio_up']*365)
Southern_ATCw_ISD,Southern_ATCw_ISD_std,Southern_ATCw_ISD_se,Southern_ATCw_ISD_ci=calculate_mean_se(station_combined[(station_combined['lat'] < 0) & (station_combined['lat'] > -60)]['mean_T_ratio_up']*365)


#=========================================load ERA5 data===================================================#
ERA5_dataset=nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/LFCA/T_change_freq_ERA5_yearly_1970-2020.nc")
ERA5_T_change_up_freq=ERA5_dataset['T_change_up_freq'][:]*365
ERA5_T_change_down_freq=ERA5_dataset['T_change_down_freq'][:]*365
ERA5_lat=ERA5_dataset['lat'][:]
ERA5_lon=ERA5_dataset['lon'][:]
ERA5_ATC_freq = ERA5_T_change_up_freq + ERA5_T_change_down_freq

ERA5_ATC_freq=np.nanmean(ERA5_ATC_freq,axis=0)
ERA5_T_change_up_freq=np.nanmean(ERA5_T_change_up_freq,axis=0)
ERA5_T_change_down_freq=np.nanmean(ERA5_T_change_down_freq,axis=0)


global_ATCc_ERA5  ,global_ATCc_ERA5_std  ,global_ATCc_ERA5_se  ,global_ATCc_ERA5_ci    =calculate_mean_se(ERA5_T_change_down_freq[ERA5_lat>-60,:])
Northern_ATCc_ERA5,Northern_ATCc_ERA5_std,Northern_ATCc_ERA5_se,Northern_ATCc_ERA5_ci  =calculate_mean_se(ERA5_T_change_down_freq[ERA5_lat>0,:])
Southern_ATCc_ERA5,Southern_ATCc_ERA5_std,Southern_ATCc_ERA5_se,Southern_ATCc_ERA5_ci  =calculate_mean_se(ERA5_T_change_down_freq[(ERA5_lat<0)&(ERA5_lat>-60),:])
print(global_ATCc_ERA5  ,global_ATCc_ERA5_std  ,global_ATCc_ERA5_se  ,global_ATCc_ERA5_ci)

global_ATCw_ERA5  ,global_ATCw_ERA5_std,global_ATCw_ERA5_se,global_ATCw_ERA5_ci    =calculate_mean_se(ERA5_T_change_up_freq[ERA5_lat>-60,:])
Northern_ATCw_ERA5,Northern_ATCw_ERA5_std,Northern_ATCw_ERA5_se,Northern_ATCw_ERA5_ci=calculate_mean_se(ERA5_T_change_up_freq[ERA5_lat>0,:])
Southern_ATCw_ERA5,Southern_ATCw_ERA5_std,Southern_ATCw_ERA5_se,Southern_ATCw_ERA5_ci=calculate_mean_se(ERA5_T_change_up_freq[(ERA5_lat<0)&(ERA5_lat>-60),:])

#=========================================load CRUJRA data===================================================#
CRUJRA_dataset=nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/EOF/CRUJRA_sudden_T_change_freq_trend_±10°C_1970_2020_yearly.nc")
CRUJRA_T_change_up_freq=CRUJRA_dataset['T_change_up_freq'][:]*365
CRUJRA_T_change_down_freq=CRUJRA_dataset['T_change_down_freq'][:]*365
CRUJRA_lat=CRUJRA_dataset['lat'][:]
CRUJRA_lon=CRUJRA_dataset['lon'][:]
CRUJRA_ATC_freq = CRUJRA_T_change_up_freq + CRUJRA_T_change_down_freq

CRUJRA_ATC_freq=np.nanmean(CRUJRA_ATC_freq,axis=0)
CRUJRA_T_change_up_freq=np.nanmean(CRUJRA_T_change_up_freq,axis=0)
CRUJRA_T_change_down_freq=np.nanmean(CRUJRA_T_change_down_freq,axis=0)


global_ATCc_CRUJRA  ,global_ATCc_CRUJRA_std,global_ATCc_CRUJRA_se,global_ATCc_CRUJRA_ci  =calculate_mean_se(CRUJRA_T_change_down_freq[CRUJRA_lat>-60,:])
Northern_ATCc_CRUJRA,Northern_ATCc_CRUJRA_std,Northern_ATCc_CRUJRA_se,Northern_ATCc_CRUJRA_ci=calculate_mean_se(CRUJRA_T_change_down_freq[CRUJRA_lat>0,:])
Southern_ATCc_CRUJRA,Southern_ATCc_CRUJRA_std,Southern_ATCc_CRUJRA_se,Southern_ATCc_CRUJRA_ci=calculate_mean_se(CRUJRA_T_change_down_freq[(CRUJRA_lat<0)&(CRUJRA_lat>-60),:])

global_ATCw_CRUJRA  ,global_ATCw_CRUJRA_std,global_ATCw_CRUJRA_se,global_ATCw_CRUJRA_ci  =calculate_mean_se(CRUJRA_T_change_up_freq[CRUJRA_lat>-60,:])
Northern_ATCw_CRUJRA,Northern_ATCw_CRUJRA_std,Northern_ATCw_CRUJRA_se,Northern_ATCw_CRUJRA_ci=calculate_mean_se(CRUJRA_T_change_up_freq[CRUJRA_lat>0,:])
Southern_ATCw_CRUJRA,Southern_ATCw_CRUJRA_std,Southern_ATCw_CRUJRA_se,Southern_ATCw_CRUJRA_ci=calculate_mean_se(CRUJRA_T_change_up_freq[(CRUJRA_lat<0)&(CRUJRA_lat>-60),:])



#=======================plot====================================#
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['axes.labelsize']  = 10
plt.rcParams['axes.titlesize']  = 10

fig = plt.figure(figsize=(7, 2.4)) # figsize=(width, heigh)
gs_top = fig.add_gridspec(1, 3, height_ratios=[1],width_ratios=[1, 1, 1], hspace=0.1, wspace=0.1,top=0.99,bottom=0.12,left=0.1,right=0.86)

axes = np.empty((1, 3), dtype=object)

for col in range(3):
    axes[0, col] = fig.add_subplot(gs_top[0, col])



new_color=mcolors.LinearSegmentedColormap.from_list('new_color', plt.get_cmap('PuOr')(np.linspace(0.55, 0.9, 256)))
new_Purples=mcolors.LinearSegmentedColormap.from_list('new_Purples', plt.get_cmap('Purples')(np.linspace(0.35, 0.8, 256)))
vmin=0
vmax=20

cmap = ListedColormap([
    "#5A8CFF", "#00B4F0", "#00D68F", "#F0E600",
    "#FFB300", "#FF7043", "#B0001B"
])
xls_vmin = 0
xls_vmax = 70
xls_bounds = np.linspace(xls_vmin, xls_vmax, 8)
xls_norm = BoundaryNorm(xls_bounds, cmap.N)


histcmap=mcolors.ListedColormap(sns.color_palette("mako", as_cmap=True)(np.linspace(0.2, 1.0, 256)))

ATCw_color='#fdaba1'
ATCc_color='#a1c4d7'


#===================================================================ISD freq==========================================================#
print('map ISD')

#density plot
x=station_combined['mean_T_ratio_up']*365
y=station_combined['mean_T_ratio_down']*365
#sns.scatterplot(x=x, y=y, ax=axes[0, 0], hue=density(x,y), palette=new_Purples,legend=False,size=0.1,)
sns.histplot(x=x, y=y,ax=axes[0, 0], bins=50, thresh=0,cmap=histcmap,cbar=False,stat="percent",pmax=0.25,alpha=0.8)
axes[0, 0].set_xlabel(r'ATCw occurrence (yr⁻¹)', )
axes[0, 0].set_ylabel(r'ATCc occurrence (yr⁻¹)', )
x_min = min(x)
x_max = max(x)
axes[0, 0].plot([x_min, 30], [x_min, 30], color='red', linestyle='--', label='1:1 Line',lw=1,alpha=0.8)
axes[0, 0].set_box_aspect(1)
axes[0, 0].set_xlim(0, 28)
axes[0, 0].set_ylim(0, 28)
axes[0, 0].set_xticks([0, 10, 20])
axes[0, 0].set_xticklabels(['0', '10', '20'])
axes[0, 0].set_yticks([0, 10, 20])
axes[0, 0].set_yticklabels(['0', '10', '20'])
axes[0, 0].text(0.02, 0.86, "a", ha="left", va="bottom", transform=axes[0, 0].transAxes, fontsize=14, fontweight='bold',)
axes[0, 0].text(0.52, 0.86, "ISD", ha="center", va="bottom", transform=axes[0, 0].transAxes, fontsize=11, )


#===================================================================CRUJRA freq==========================================================#
print('map CRUJRA')
#density plot
x=CRUJRA_T_change_up_freq.flatten()
y=CRUJRA_T_change_down_freq.flatten()
x = np.asarray(x)
y = np.asarray(y)
valid_mask = np.isfinite(x) & np.isfinite(y)    
x = x[valid_mask]
y = y[valid_mask]
print(len(x))

#sns.scatterplot(x=x, y=y, ax=axes[3, 1], palette=new_Purples,legend=False,size=0.05,)
sns.histplot(x=x, y=y,ax=axes[0, 1], bins=50, thresh=0,cmap=histcmap,stat="percent",cbar=False ,pmax=0.25,alpha=0.8)

x_min = min(x)
x_max = max(x)
axes[0, 1].plot([x_min, 30], [x_min, 30], color='red', linestyle='--', label='1:1 Line',lw=1,alpha=0.8)
axes[0, 1].set_box_aspect(1)
axes[0, 1].set_xlabel('ATCw occurrence (yr⁻¹)', )
axes[0, 1].yaxis.tick_right()
axes[0, 1].set_xlim(0, 28)
axes[0, 1].set_ylim(0, 28)
axes[0, 1].set_xticks([0, 10, 20])
axes[0, 1].set_xticklabels(['0', '10', '20'])
axes[0, 1].set_yticks([])
axes[0, 1].set_ylabel('')  
axes[0, 1].text(0.02, 0.86, "b", ha="left", va="bottom", transform=axes[0,1].transAxes, fontsize=14, fontweight='bold',)
axes[0, 1].text(0.52, 0.86, "CRUJRA", ha="center", va="bottom", transform=axes[0, 1].transAxes, fontsize=11, )


#===================================================================ERA5 freq==========================================================#
print('map ERA5')

#density plot
x=ERA5_T_change_up_freq[ERA5_lat>-60,:].flatten()
y=ERA5_T_change_down_freq[ERA5_lat>-60,:].flatten()
x = np.asarray(x)
y = np.asarray(y)
valid_mask = np.isfinite(x) & np.isfinite(y)    
x = x[valid_mask]
y = y[valid_mask]
#sns.scatterplot(x=x, y=y, ax=axes[3, 2],  palette=new_Purples,legend=False,size=0.01,)
h=sns.histplot(x=x, y=y, ax=axes[0, 2],bins=50, thresh=0, cmap=histcmap,stat="percent",cbar=False,pmax=0.25,alpha=0.8)
axes[0, 2].set_xlabel(r'ATCw occurrence (yr⁻¹)', )
axes[0, 2].set_ylabel('', )
x_min = min(x)
x_max = max(x)
axes[0, 2].plot([x_min, 30], [x_min, 30], color='red', linestyle='--', label='1:1 Line',lw=1,alpha=0.8)
axes[0, 2].set_box_aspect(1)
axes[0, 2].yaxis.tick_right()
axes[0, 2].set_xlim(0, 28)
axes[0, 2].set_ylim(0, 28)
axes[0, 2].set_xticks([0, 10, 20])
axes[0, 2].set_xticklabels(['0', '10', '20'])
axes[0, 2].set_yticks([])
axes[0, 2].set_ylabel('')
axes[0, 2].text(0.02, 0.86, "c", ha="left", va="bottom", transform=axes[0, 2].transAxes, fontsize=14,fontweight='bold', )
axes[0, 2].text(0.52, 0.86, "ERA5", ha="center", va="bottom", transform=axes[0, 2].transAxes, fontsize=11, )

#============================================color bar==========================================================#
histcax=inset_axes(axes[0, 2], width="8%", height="100%", loc='lower left',
                  bbox_to_anchor=(1.05, 0, 1, 1), bbox_transform=axes[0, 2].transAxes, borderpad=0)
histcbar = fig.colorbar(h.collections[0], cax=histcax, label='percent',orientation='vertical',extend='max')
histcbar.ax.tick_params(labelsize=10)
histcbar.set_label('percent', rotation=0, labelpad=-25, y=-0.18, ha='center', va='bottom')
histcbar.set_ticks([0, 0.05, 0.1,])  # 设置刻度位置
histcbar.ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:.2f}%'))



#===============================================save figure============================================================#
#plt.subplots_adjust(left=0.02, right=0.98, bottom=0.04 , top=0.98,wspace=0.03, hspace=0.01)#wspace 水平间距   hspace垂直间距
#pos = axes[0, 1].get_position()
#axes[0, 1].set_position([pos.x0, pos.y0+0.05, pos.width, pos.height*0.7])
#pos = axes[1, 1].get_position()
#axes[1, 1].set_position([pos.x0, pos.y0+0.05, pos.width, pos.height*0.7])
#pos = axes[2, 1].get_position()
#axes[2, 1].set_position([pos.x0, pos.y0+0.05, pos.width, pos.height*0.7])


fig1 = plt.gcf()
fig1.savefig(str(current_directory)+"/FigureS2_ATC_density_plot.png", dpi=300)
#plt.show()


