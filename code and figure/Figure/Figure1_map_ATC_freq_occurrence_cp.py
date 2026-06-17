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
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

current_directory = os.path.dirname(os.path.abspath(__file__))


def weighted_nanstd(data, weights, lat_cond):
    mask = lat_cond
    d = data[mask, :].flatten()
    w = weights[mask, :].flatten()

    valid = ~(np.isnan(d) | np.isnan(w))# 同时剔除 data 和 weight 中任一为 NaN 的位置
    d, w = d[valid], w[valid]

    mean = np.average(d, weights=w)
    return np.sqrt(np.average((d - mean)**2, weights=w))

def weighted_nanmean(data, weights, lat_cond):
    mask = lat_cond
    d = data[mask, :].flatten()
    w = weights[mask, :].flatten()
    valid = ~(np.isnan(d) | np.isnan(w))
    d, w = d[valid], w[valid]
    return np.average(d, weights=w)



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
station_combined['ATCc_frac'] = station_combined['mean_T_ratio_down']/(station_combined['mean_T_ratio_up']+ station_combined['mean_T_ratio_down'])


#=========================================load ERA5 data===================================================#
#ERA5_dataset=nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/LFCA/T_change_freq_ERA5_yearly_1970-2020_0.5d.nc")
ERA5_dataset=nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/LFCA/T_change_freq_ERA5_yearly_1970-2020.nc")
ERA5_ATCw=ERA5_dataset['T_change_up_freq'][:]*365
ERA5_ATCc=ERA5_dataset['T_change_down_freq'][:]*365
ERA5_lat=ERA5_dataset['lat'][:]
ERA5_lon=ERA5_dataset['lon'][:]
ERA5_ATC_freq = ERA5_ATCw + ERA5_ATCc

ERA5_ATC_freq=np.nanmean(ERA5_ATC_freq,axis=0)

ERA5_ATCc_frac=ERA5_ATCc[:]/(ERA5_ATCw[:]+ERA5_ATCc[:])
ERA5_ATCc_frac=np.nanmean(ERA5_ATCc_frac,axis=0)
#print(ERA5_ATCc.shape)
#print(ERA5_ATCc_frac.shape)

data_area = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/ERA5_area.nc")
area_weight=data_area['cell_area'][:]

ERA5_global_ATCw = weighted_nanmean(np.nanmean(ERA5_ATCw,axis=0), area_weight, ERA5_lat > -60)
ERA5_global_ATCc = weighted_nanmean(np.nanmean(ERA5_ATCc,axis=0), area_weight, ERA5_lat > -60)
ERA5_global_ATCw_std = weighted_nanstd(np.nanmean(ERA5_ATCw,axis=0), area_weight, ERA5_lat > -60)
ERA5_global_ATCc_std = weighted_nanstd(np.nanmean(ERA5_ATCc,axis=0), area_weight, ERA5_lat > -60)


print("ERA5_global_ATCw",ERA5_global_ATCw,"ERA5_global_ATCw_std",ERA5_global_ATCw_std,)
print("ERA5_global_ATCc",ERA5_global_ATCc,"ERA5_global_ATCc_std",ERA5_global_ATCc_std,)

#=========================================load CRUJRA data===================================================#
CRUJRA_dataset=nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/EOF/CRUJRA_sudden_T_change_freq_trend_±10°C_1970_2020_yearly.nc")
CRUJRA_ATCw=CRUJRA_dataset['T_change_up_freq'][:]*365
CRUJRA_ATCc=CRUJRA_dataset['T_change_down_freq'][:]*365
CRUJRA_lat=CRUJRA_dataset['lat'][:]
CRUJRA_lon=CRUJRA_dataset['lon'][:]
CRUJRA_ATC_freq = CRUJRA_ATCw + CRUJRA_ATCc

CRUJRA_ATC_freq=np.nanmean(CRUJRA_ATC_freq,axis=0)


CRUJRA_ATCc_frac=CRUJRA_ATCc[:]/(CRUJRA_ATCw[:]+CRUJRA_ATCc[:])
CRUJRA_ATCc_frac=np.nanmean(CRUJRA_ATCc_frac,axis=0)

data_area = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/CRUJRA_area.nc")
area_weight=data_area['cell_area'][:]

CRUJRA_global_ATCw = weighted_nanmean(np.nanmean(CRUJRA_ATCw,axis=0), area_weight, CRUJRA_lat > -60)
CRUJRA_global_ATCc = weighted_nanmean(np.nanmean(CRUJRA_ATCc,axis=0), area_weight, CRUJRA_lat > -60)
CRUJRA_global_ATCw_std = weighted_nanstd(np.nanmean(CRUJRA_ATCw,axis=0), area_weight, CRUJRA_lat > -60)
CRUJRA_global_ATCc_std = weighted_nanstd(np.nanmean(CRUJRA_ATCc,axis=0), area_weight, CRUJRA_lat > -60)

print("CRUJRA_global_ATCw",CRUJRA_global_ATCw,"CRUJRA_global_ATCw_std",CRUJRA_global_ATCw_std)
print("CRUJRA_global_ATCc",CRUJRA_global_ATCc,"CRUJRA_global_ATCc_std",CRUJRA_global_ATCc_std)

#==========================================load CMIP6 data===========================================#

models=['ACCESS-ESM1-5','AWI-CM-1-1-MR','BCC-CSM2-MR','CanESM5','CESM2-WACCM','CMCC-ESM2','E3SM-1-0','EC-Earth3','FGOALS-g3','GFDL-ESM4',
        'IITM-ESM','INM-CM5-0','IPSL-CM6A','KACE-1-0-G','KIOST-ESM','MIROC6','MPI-ESM1-2-HR','NESM3','NorESM2','TaiESM1',]

CMIP6_ATC_ave=[]
CMIP6_ATCc_frac_ave=[]
CMIP6_ATCc_frac_d=[]

#Global_CMIP6_ATCc_frac_ave=[]
#Global_CMIP6_ATCc_frac_d=[]
#Northern_CMIP6_ATCc_frac_ave=[]
#Northern_CMIP6_ATCc_frac_d=[]
#Southern_CMIP6_ATCc_frac_ave=[]
#Southern_CMIP6_ATCc_frac_d=[]

Global_CMIP6_ATCc=[]
Global_CMIP6_ATCw=[]

for i, model in enumerate(models):
    print(model)
    dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/T_change_freq_"+str(model)+"_yearly_1970-2015_mk-rescale.nc")
    if 'latitude' in dataset.variables:
        CMIP6_lat = dataset['latitude'][:]
        CMIP6_lon = dataset['longitude'][:]
    elif 'lat' in dataset.variables:
        CMIP6_lat = dataset['lat'][:]
        CMIP6_lon = dataset['lon'][:]

    ATCw = np.array(dataset['T_change_up_freq'][:])*365
    ATCc = np.array(dataset['T_change_down_freq'][:])*365
    ATC  = ATCw[:]+ATCc[:]
    ATC_frac=ATCc[:]/ATC[:]
    ATC_frac_ave=np.nanmean(ATC_frac,axis=0)

    CMIP6_ATC_ave.append(np.nanmean(ATC,axis=0))

    Global_CMIP6_ATCw.append(np.nanmean(ATCw,axis=0))
    Global_CMIP6_ATCc.append(np.nanmean(ATCc,axis=0))
    CMIP6_ATCc_frac_ave.append(ATC_frac_ave)


CMIP6_ATC_ave      =np.nanmean(CMIP6_ATC_ave,axis=0)
CMIP6_ATCc_frac_ave=np.nanmean(CMIP6_ATCc_frac_ave,axis=0)

data_area = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/CMIP6_0.5d_area.nc")
area_weight=data_area['cell_area'][:]
CMIP6_global_ATCw = weighted_nanmean(np.nanmean(Global_CMIP6_ATCw,axis=0), area_weight, CMIP6_lat > -60)
CMIP6_global_ATCc = weighted_nanmean(np.nanmean(Global_CMIP6_ATCc,axis=0), area_weight, CMIP6_lat > -60)
CMIP6_global_ATCw_std = weighted_nanstd(np.nanmean(Global_CMIP6_ATCw,axis=0), area_weight, CMIP6_lat > -60)
CMIP6_global_ATCc_std = weighted_nanstd(np.nanmean(Global_CMIP6_ATCc,axis=0), area_weight, CMIP6_lat > -60)

print("CMIP6_global_ATCw",CMIP6_global_ATCw,"CMIP6_global_ATCw_std",CMIP6_global_ATCw_std)
print("CMIP6_global_ATCc",CMIP6_global_ATCc,"CMIP6_global_ATCc_std",CMIP6_global_ATCc_std)



#======================================================plot barplot====================================================#


models=['ISD','CRUJRA','ERA5','CMIP6']

all_data = []
for i, model in enumerate(models):
    print(model)
    if model=='CRUJRA':
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/EOF/CRUJRA_sudden_T_change_freq_trend_±10°C_1970_2020_yearly.nc")
        ATC_freq =CRUJRA_ATC_freq.copy()
        ATCc_frac=CRUJRA_ATCc_frac.copy()
        data_area = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/CRUJRA_area.nc")
        area_weight=data_area['cell_area'][:]


    elif model=='ERA5':
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/LFCA/T_change_freq_ERA5_yearly_1970-2020.nc")
        ATC_freq   =ERA5_ATC_freq.copy()
        ATCc_frac  =ERA5_ATCc_frac.copy()
        data_area = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/ERA5_area.nc")
        area_weight=data_area['cell_area'][:]


    elif model=='ISD':
        global_station=station_combined[station_combined['lat']>-60]
        NH_station    =station_combined[station_combined['lat']>0]
        SH_station    =station_combined[(station_combined['lat']<=0) & (station_combined['lat']>-60)]
        
        global_ATC_freq  =np.nanmean(global_station['ATC'])
        NH_ATC_freq=np.nanmean(NH_station['ATC'])
        SH_ATC_freq=np.nanmean(SH_station['ATC'])
        global_ATC_freq_std   =np.nanstd(global_station['ATC'])
        NH_ATC_freq_std =np.nanstd(NH_station['ATC'])
        SH_ATC_freq_std =np.nanstd(SH_station['ATC'])
    
        global_ATCc_frac  =np.nanmean(global_station['ATCc_frac'])
        NH_ATCc_frac      =np.nanmean(NH_station['ATCc_frac'])
        SH_ATCc_frac      =np.nanmean(SH_station['ATCc_frac'])
        global_ATCc_frac_std =np.nanstd(global_station['ATCc_frac'])
        NH_ATCc_frac_std     =np.nanstd(NH_station['ATCc_frac'])
        SH_ATCc_frac_std     =np.nanstd(SH_station['ATCc_frac'])            

        all_data.extend([
            {'Model': model, 'Region': 'Globe', 'Type': 'ATC',         'Value': global_ATC_freq,  'error': global_ATC_freq_std},
            {'Model': model, 'Region': 'Globe', 'Type': 'ATCc_frac',   'Value': global_ATCc_frac,  'error': global_ATCc_frac_std},
            {'Model': model, 'Region': 'NH'    , 'Type': 'ATC',         'Value': NH_ATC_freq,       'error': NH_ATC_freq_std},
            {'Model': model, 'Region': 'NH'    , 'Type': 'ATCc_frac',   'Value': NH_ATCc_frac,      'error': NH_ATCc_frac_std},
            {'Model': model, 'Region': 'SH'    , 'Type': 'ATC',         'Value': SH_ATC_freq,       'error': SH_ATC_freq_std},
            {'Model': model, 'Region': 'SH'    , 'Type': 'ATCc_frac',   'Value': SH_ATCc_frac,      'error': SH_ATCc_frac_std},
        ])
        continue

    else:
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/ACCESS-ESM1-5/T_change_freq_ACCESS-ESM1-5_yearly_1970-2015_mk-rescale.nc")
        ATC_freq   =CMIP6_ATC_ave.copy()
        ATCc_frac  =CMIP6_ATCc_frac_ave.copy()
        data_area = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/CMIP6_0.5d_area.nc")
        area_weight=data_area['cell_area'][:]

    if 'latitude' in dataset.variables:
        lat = dataset['latitude'][:]
        lon = dataset['longitude'][:]
    elif 'lat' in dataset.variables:
        lat = dataset['lat'][:]
        lon = dataset['lon'][:]

    print(len(lat))
#    global_ATC_freq  =np.nanmean(ATC_freq[lat>-60,:])
#    NH_ATC_freq=np.nanmean(ATC_freq[lat>0,:])
#    SH_ATC_freq=np.nanmean(ATC_freq[(lat<0)&(lat>-60),:])
#    global_ATC_freq_std   =np.nanstd(ATC_freq[lat>-60,:])
#    NH_ATC_freq_std =np.nanstd(ATC_freq[lat>0,:])
#    SH_ATC_freq_std =np.nanstd(ATC_freq[(lat<0)&(lat>-60),:])
#
#    global_ATCc_frac  =np.nanmean(ATCc_frac[lat>-60,:])
#    NH_ATCc_frac=np.nanmean(ATCc_frac[lat>0,:])
#    SH_ATCc_frac=np.nanmean(ATCc_frac[(lat > -60) & (lat < 0),:])
#    global_ATCc_frac_std   =np.nanstd(ATCc_frac[lat>-60,:])
#    NH_ATCc_frac_std =np.nanstd(ATCc_frac[lat>0,:])
#    SH_ATCc_frac_std =np.nanstd(ATCc_frac[(lat<0)&(lat>-60),:])

    global_ATC_freq = weighted_nanmean(ATC_freq, area_weight, lat > -60)
    NH_ATC_freq = weighted_nanmean(ATC_freq, area_weight, lat > 0)
    SH_ATC_freq = weighted_nanmean(ATC_freq, area_weight, (lat < 0) & (lat > -60))
    global_ATC_freq_std = weighted_nanstd(ATC_freq, area_weight, lat > -60)
    NH_ATC_freq_std = weighted_nanstd(ATC_freq, area_weight, lat > 0)
    SH_ATC_freq_std = weighted_nanstd(ATC_freq, area_weight, (lat < 0) & (lat > -60))
    
    # ATCc_frac
    global_ATCc_frac = weighted_nanmean(ATCc_frac, area_weight, lat > -60)
    NH_ATCc_frac = weighted_nanmean(ATCc_frac, area_weight, lat > 0)
    SH_ATCc_frac = weighted_nanmean(ATCc_frac, area_weight, (lat > -60) & (lat < 0))
    global_ATCc_frac_std = weighted_nanstd(ATCc_frac, area_weight, lat > -60)
    NH_ATCc_frac_std = weighted_nanstd(ATCc_frac, area_weight, lat > 0)
    SH_ATCc_frac_std = weighted_nanstd(ATCc_frac, area_weight, (lat < 0) & (lat > -60))

    all_data.extend([
            {'Model': model, 'Region': 'Globe', 'Type': 'ATC',         'Value': global_ATC_freq,  'error': global_ATC_freq_std},
            {'Model': model, 'Region': 'Globe', 'Type': 'ATCc_frac',   'Value': global_ATCc_frac,  'error': global_ATCc_frac_std},
            {'Model': model, 'Region': 'NH'    , 'Type': 'ATC',         'Value': NH_ATC_freq,       'error': NH_ATC_freq_std},
            {'Model': model, 'Region': 'NH'    , 'Type': 'ATCc_frac',   'Value': NH_ATCc_frac,      'error': NH_ATCc_frac_std},
            {'Model': model, 'Region': 'SH'    , 'Type': 'ATC',         'Value': SH_ATC_freq,       'error': SH_ATC_freq_std},
            {'Model': model, 'Region': 'SH'    , 'Type': 'ATCc_frac',   'Value': SH_ATCc_frac,      'error': SH_ATCc_frac_std},
        ])


df = pd.DataFrame(all_data)
models = df['Model'].unique()
region = ['Globe', 'NH', 'SH']
print(df)

#=======================plot====================================#
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['axes.labelsize']  = 10
plt.rcParams['axes.titlesize']  = 10

fig = plt.figure(figsize=(7,7)) # figsize=(width, heigh)
gs_top = fig.add_gridspec(4, 2, height_ratios=[1, 1, 1,1], width_ratios=[1, 1], hspace=0.02, wspace=0.15,top=0.98,bottom=0.06,left=0.06,right=0.96)

axes = np.empty((4, 3), dtype=object)

for row in range(4):
    axes[row, 0] = fig.add_subplot(gs_top[row, 0], projection=ccrs.PlateCarree())  # 地图投影
    axes[row, 1] = fig.add_subplot(gs_top[row, 1], projection=ccrs.PlateCarree())  # 地图投影
    axes[row, 2] = None  # 空列



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


histcmap=mcolors.ListedColormap(sns.color_palette("RdBu", as_cmap=True)(np.linspace(0.5, 0.8, 256)))

ATCw_color='#fdaba1'
ATCc_color='#a1c4d7'


vmin_frac=0
vmax_frac=1
cmap_frac = mcolors.ListedColormap(sns.color_palette("RdBu", as_cmap=True)(np.linspace(0.2, 0.8, 256)))
#===================================================================ISD freq==========================================================#
print('map ISD')
im_ISD_ATC = axes[0, 0].scatter(station_combined['lon'],station_combined['lat'], c=station_combined['ATC'], transform=ccrs.PlateCarree(),
                                              cmap=histcmap,vmin=vmin, vmax=vmax, s=1,alpha=0.9,edgecolors='none')
axes[0, 0].add_feature(cfeature.COASTLINE,linewidth=0.3,edgecolor='black')
axes[0, 0].text(0.02, 0.94, "a", ha="left", va="bottom", transform=axes[0,0].transAxes, fontsize=14,weight='bold')
axes[0, 0].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[0, 0].set_frame_on(False)

im_ISD_ATCc_frac = axes[0, 1].scatter(station_combined['lon'],station_combined['lat'], c=station_combined['ATCc_frac'], transform=ccrs.PlateCarree(),
                                              cmap=cmap_frac,vmin=vmin_frac, vmax=vmax_frac, s=1,alpha=0.9,edgecolors='none')
axes[0, 1].add_feature(cfeature.COASTLINE,linewidth=0.3,edgecolor='black')
axes[0, 1].text(0.02, 0.94, "b", ha="left", va="bottom", transform=axes[0,1].transAxes, fontsize=14, weight='bold')
axes[0, 1].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[0, 1].set_frame_on(False)


ISD_df = df[df['Model'] == 'ISD']
ATC_data = ISD_df[ISD_df['Type'] == 'ATC']
ATCc_frac_data = ISD_df[ISD_df['Type'] == 'ATCc_frac']
x = np.arange(len(region))
width = 0.6

ax_inset1 = inset_axes(axes[0, 0], width="18%", height="40%", loc='lower left', bbox_to_anchor=(0.02, 0.02, 1, 1), bbox_transform=axes[0, 0].transAxes)
ax_inset1.errorbar(x=ATC_data['Value'].values, y=x, xerr=([0] * len(ATC_data['error']), ATC_data['error'].values), capsize=2,  fmt='none', ecolor='black', alpha=0.7,elinewidth=0.6,zorder=1)             
ax_inset1.barh(y=x, width=ATC_data['Value'].values, height=width, label='ATC', color='#F2E6D8', alpha=0.9, edgecolor='black', linewidth=0.6,zorder=2)

ax_inset2 = inset_axes(axes[0, 1], width="18%", height="40%", loc='lower left', bbox_to_anchor=(0.02, 0.02, 1, 1), bbox_transform=axes[0, 1].transAxes)
ax_inset2.errorbar(x=ATCc_frac_data['Value'].values, y=x, xerr=([0] * len(ATCc_frac_data['error']), ATCc_frac_data['error'].values), capsize=2,  fmt='none', ecolor='black', alpha=0.7,elinewidth=0.6,zorder=1) 
ax_inset2.barh(y=x, width=ATCc_frac_data['Value'].values, height=width, label='ATC', color='#F2E6D8', alpha=0.9, edgecolor='black', linewidth=0.6,zorder=2)

#===================================================================CRUJRA freq==========================================================#
print('map CRUJRA')
im_CRUJRA_ATC = axes[1, 0].pcolormesh(CRUJRA_lon, CRUJRA_lat, CRUJRA_ATC_freq, transform=ccrs.PlateCarree(), cmap=histcmap,vmin=vmin, vmax=vmax)
axes[1, 0].add_feature(cfeature.COASTLINE,linewidth=0.3,edgecolor='black')
axes[1, 0].text(0.02, 0.94, "c", ha="left", va="bottom", transform=axes[1, 0].transAxes, fontsize=14, weight='bold')
axes[1, 0].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[1, 0].set_frame_on(False)

im_CRUJRA_ATCc_frac = axes[1, 1].pcolormesh(CRUJRA_lon, CRUJRA_lat, CRUJRA_ATCc_frac, transform=ccrs.PlateCarree(), cmap=cmap_frac,vmin=vmin_frac, vmax=vmax_frac)
axes[1, 1].add_feature(cfeature.COASTLINE,linewidth=0.3,edgecolor='black')
axes[1, 1].add_feature(cfeature.LAND, facecolor='gray', alpha=0.3, zorder=0)
axes[1, 1].text(0.02, 0.94, "d", ha="left", va="bottom", transform=axes[1, 1].transAxes, fontsize=14, weight='bold')
axes[1, 1].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[1, 1].set_frame_on(False)


CRUJRA_df = df[df['Model'] == 'CRUJRA']
ATC_data = CRUJRA_df[CRUJRA_df['Type'] == 'ATC']
ATCc_frac_data = CRUJRA_df[CRUJRA_df['Type'] == 'ATCc_frac']
x = np.arange(len(ATC_data))
width = 0.6

ax_inset3 = inset_axes(axes[1, 0], width="18%", height="40%", loc='lower left', bbox_to_anchor=(0.02, 0.02, 1, 1), bbox_transform=axes[1, 0].transAxes)
ax_inset3.errorbar(x=ATC_data['Value'].values, y=x, xerr=([0] * len(ATC_data['error']), ATC_data['error'].values), capsize=2,  fmt='none', ecolor='black', elinewidth=0.6,alpha=0.7, zorder=1)             
ax_inset3.barh(y=x, width=ATC_data['Value'].values, height=width, label='ATC', color='#F2E6D8', alpha=0.9,edgecolor='black', linewidth=0.6,zorder=2)

ax_inset4 = inset_axes(axes[1, 1], width="18%", height="40%", loc='lower left', bbox_to_anchor=(0.02, 0.02, 1, 1), bbox_transform=axes[1, 1].transAxes)
ax_inset4.errorbar(x=ATCc_frac_data['Value'].values, y=x, xerr=([0] * len(ATCc_frac_data['error']), ATCc_frac_data['error'].values), capsize=2,  fmt='none', ecolor='black', elinewidth=0.6,alpha=0.7, zorder=1) 
ax_inset4.barh(y=x, width=ATCc_frac_data['Value'].values, height=width, label='ATC', color='#F2E6D8', alpha=0.9,edgecolor='black', linewidth=0.6,zorder=2)



#===================================================================ERA5 freq==========================================================#
print('map ERA5')
im_ERA5_ATC = axes[2, 0].pcolormesh(ERA5_lon, ERA5_lat, ERA5_ATC_freq, transform=ccrs.PlateCarree(), cmap=histcmap,vmin=vmin, vmax=vmax)
axes[2, 0].add_feature(cfeature.COASTLINE,linewidth=0.3,edgecolor='black')
axes[2, 0].text(0.02, 0.94, "e", ha="left", va="bottom", transform=axes[2,0].transAxes, fontsize=14, weight='bold')
axes[2, 0].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[2, 0].set_frame_on(False)

im_ERA5_ATCc_frac = axes[2, 1].pcolormesh(ERA5_lon, ERA5_lat, ERA5_ATCc_frac, transform=ccrs.PlateCarree(), cmap=cmap_frac,vmin=vmin_frac, vmax=vmax_frac)
axes[2, 1].add_feature(cfeature.COASTLINE,linewidth=0.3,edgecolor='black')
axes[2, 1].add_feature(cfeature.LAND, facecolor='gray', alpha=0.3, zorder=0)
axes[2, 1].text(0.02, 0.94, "f", ha="left", va="bottom", transform=axes[2,1].transAxes, fontsize=14,weight='bold')
axes[2, 1].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[2, 1].set_frame_on(False)


ERA5_df = df[df['Model'] == 'ERA5']
ATC_data = ERA5_df[ERA5_df['Type'] == 'ATC']
ATCc_frac_data = ERA5_df[ERA5_df['Type'] == 'ATCc_frac']
x = np.arange(len(ATC_data))
width = 0.7

ax_inset5 = inset_axes(axes[2, 0], width="18%", height="40%", loc='lower left', bbox_to_anchor=(0.02, 0.02, 1, 1), bbox_transform=axes[2, 0].transAxes)
ax_inset5.errorbar(x=ATC_data['Value'].values, y=x, xerr=([0] * len(ATC_data['error']), ATC_data['error'].values), capsize=2,  fmt='none', ecolor='black', elinewidth=0.7,alpha=0.6, zorder=1)             
ax_inset5.barh(y=x, width=ATC_data['Value'].values, height=width, label='ATC', color='#F2E6D8', alpha=0.9, edgecolor='black', linewidth=0.6,zorder=2)

ax_inset6 = inset_axes(axes[2, 1], width="18%", height="40%", loc='lower left', bbox_to_anchor=(0.02, 0.02, 1, 1), bbox_transform=axes[2, 1].transAxes)
ax_inset6.errorbar(x=ATCc_frac_data['Value'].values, y=x, xerr=([0] * len(ATCc_frac_data['error']), ATCc_frac_data['error'].values), capsize=2,  fmt='none', ecolor='black', alpha=0.7, elinewidth=0.6,zorder=1) 
ax_inset6.barh(y=x, width=ATCc_frac_data['Value'].values, height=width, label='ATC', color='#F2E6D8', alpha=0.9, edgecolor='black', linewidth=0.6,zorder=2)


#===================================================================CMIP6 freq==========================================================#
print('map CMIP6')
im_CMIP6_ATC = axes[3, 0].pcolormesh(CMIP6_lon, CMIP6_lat, CMIP6_ATC_ave, transform=ccrs.PlateCarree(), cmap=histcmap,vmin=vmin, vmax=vmax)
axes[3, 0].add_feature(cfeature.COASTLINE,linewidth=0.3,edgecolor='black')
axes[3, 0].text(0.02, 0.94, "g", ha="left", va="bottom", transform=axes[3,0].transAxes, fontsize=14, weight='bold')
axes[3, 0].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[3, 0].set_frame_on(False)

im_CMIP6_ATCc_frac = axes[3, 1].pcolormesh(CMIP6_lon, CMIP6_lat, CMIP6_ATCc_frac_ave, transform=ccrs.PlateCarree(), cmap=cmap_frac,vmin=vmin_frac, vmax=vmax_frac)
axes[3, 1].add_feature(cfeature.COASTLINE,linewidth=0.3,edgecolor='black')
axes[3, 1].add_feature(cfeature.LAND, facecolor='gray', alpha=0.3, zorder=0)
axes[3, 1].text(0.02, 0.94, "h", ha="left", va="bottom", transform=axes[3,1].transAxes, fontsize=14, weight='bold')
axes[3, 1].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[3, 1].set_frame_on(False)

CMIP6_df = df[df['Model'] == 'CMIP6']
ATC_data = CMIP6_df[CMIP6_df['Type'] == 'ATC']
print(ATC_data)
ATCc_frac_data = CMIP6_df[CMIP6_df['Type'] == 'ATCc_frac']
x = np.arange(len(ATC_data))
width = 0.7

ax_inset7 = inset_axes(axes[3, 0], width="18%", height="40%", loc='lower left', bbox_to_anchor=(0.02, 0.02, 1, 1), bbox_transform=axes[3, 0].transAxes)
ax_inset7.errorbar(x=ATC_data['Value'].values, y=x, xerr=([0] * len(ATC_data['error']), ATC_data['error'].values), capsize=2,  fmt='none', ecolor='black', alpha=0.7,elinewidth=0.4,zorder=1)             
ax_inset7.barh(y=x, width=ATC_data['Value'].values, height=width, label='ATC', color='#F2E6D8', alpha=0.9, edgecolor='black', linewidth=0.6,zorder=2)

ax_inset8 = inset_axes(axes[3, 1], width="18%", height="40%", loc='lower left', bbox_to_anchor=(0.02, 0.02, 1, 1), bbox_transform=axes[3, 1].transAxes)
ax_inset8.errorbar(x=ATCc_frac_data['Value'].values, y=x, xerr=([0] * len(ATCc_frac_data['error']), ATCc_frac_data['error'].values), capsize=2,  fmt='none',ecolor='black', alpha=0.7,elinewidth=0.4,zorder=1) 
ax_inset8.barh(y=x, width=ATCc_frac_data['Value'].values, height=width, label='ATC', color='#F2E6D8',alpha=0.9,  edgecolor='black', linewidth=0.6,zorder=2)




ax_insets = [ax_inset1,ax_inset2,ax_inset3,ax_inset4,ax_inset5,ax_inset6,ax_inset7,ax_inset8]
[ax.spines['top'].set_visible(False)   for ax in ax_insets]
[ax.spines['left'].set_visible(False)  for ax in ax_insets]
[ax.spines['right'].set_visible(False) for ax in ax_insets]
[ax.axvline(x=0, color='black', linestyle='-', alpha=1,linewidth=0.8) for ax in ax_insets]
[ax.set_ylim(-0.5, len(region) -0.5)   for ax in ax_insets]
[ax.set_yticks(np.arange(len(region)))   for ax in ax_insets]
[ax.set_yticklabels(region)   for ax in ax_insets]
[ax.invert_yaxis()   for ax in ax_insets]
[ax.tick_params(axis='y', length=0)   for ax in ax_insets]

[ax.set_xlim(0, 13)   for ax in [ax_inset1,ax_inset3,ax_inset5,ax_inset7]]
[ax.set_xlim(0, 1)    for ax in [ax_inset2,ax_inset4,ax_inset6,ax_inset8]]
[ax.set_xticks([0,0.5,1])   for ax in [ax_inset2,ax_inset4,ax_inset6,ax_inset8]]
[ax.set_xticklabels(['0','50%',"100%"])   for ax in [ax_inset2,ax_inset4,ax_inset6,ax_inset8]]


#===================================================================map colorbar==========================================================#
cbar_ATC_ax_ave = fig.add_axes([0.1, 0.03, 0.3, 0.01])  # [left, bottom, width, height]
cbar_ATC_ave=fig.colorbar(im_ERA5_ATC, cax=cbar_ATC_ax_ave, orientation='horizontal', extend='max')
cbar_ATC_ave.set_ticks([vmin,vmin/2,0,vmax*0.5,vmax])  # 设置刻度位置
cbar_ATC_ave.outline.set_linewidth(0.5)  # 设置线宽
cbar_ATC_ave.outline.set_edgecolor('gray')  # 设置边框颜色
cbar_ATC_ave.ax.tick_params(axis='x', length=2, color='gray', width=1,labelsize=10,)
cbar_ATC_ave.set_label('Occurrence of ATC (yr⁻¹)', fontsize=10, labelpad=-32)

#======legend=======#
cbar_ATCc_ax = fig.add_axes([0.6, 0.03, 0.3, 0.01])  # [left, bottom, width, height]
cbar_ATCc=fig.colorbar(im_ERA5_ATCc_frac, cax=cbar_ATCc_ax, orientation='horizontal', extend='neither')
cbar_ATCc.set_ticks([0,vmax_frac*0.5,vmax_frac])  # 设置刻度位置
cbar_ATCc.set_ticklabels([f'{t*100:.0f}%' for t in [0,vmax_frac*0.5,vmax_frac]])
cbar_ATCc.outline.set_linewidth(0.5)  # 设置线宽
cbar_ATCc.outline.set_edgecolor('gray')  # 设置边框颜色
cbar_ATCc.ax.tick_params(axis='x', length=2, color='gray', width=1,labelsize=10,)
cbar_ATCc.set_label('ATCc fraction', fontsize=10, labelpad=-32)


#===============================================save figure============================================================#
#plt.subplots_adjust(left=0.02, right=0.98, bottom=0.04 , top=0.98,wspace=0.03, hspace=0.01)#wspace 水平间距   hspace垂直间距



fig1 = plt.gcf()
script_name = os.path.splitext(os.path.basename(__file__))[0]
fig1.savefig(str(current_directory)+f"/{script_name}.png", dpi=300)
#plt.show()


