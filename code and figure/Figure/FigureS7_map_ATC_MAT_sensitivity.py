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
from scipy import stats
import string
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.colors as mcolors
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from scipy.stats import linregress
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

def aggregate_slopes(slopes, sig_mask):
    n_models, lat_dim, lon_dim = slopes.shape
    result = np.full((lat_dim, lon_dim), np.nan)
    sig_result = np.zeros((lat_dim, lon_dim), dtype=bool)
    
    # 计算每个格点的全部模型平均
    all_avg = np.nanmean(slopes, axis=0)
    
    # 对每个格点进行聚合
    for i in range(lat_dim):
        for j in range(lon_dim):
            # 获取该格点显著的模型索引
            sig_indices = np.where(sig_mask[:, i, j])[0]
            
            if len(sig_indices) >= 2:
                # 使用显著模型的平均
                result[i, j] = np.mean(slopes[sig_indices, i, j])
                sig_result[i, j] = True
            else:
                # 使用全部模型的平均
                result[i, j] = all_avg[i, j]
    
    return result, sig_result


#==========================================load CRUJRA data===========================================#

CRUJRA_dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/CRUJRA_sudden_T_change_freq_MAT_sensitivity_1970_2020.nc")

CRUJRA_ATCw_pvalue=CRUJRA_dataset['T_change_up_freq_trend_p_value'][:]
CRUJRA_ATCc_pvalue=CRUJRA_dataset['T_change_down_freq_trend_p_value'][:]
CRUJRA_ATCw_slope=CRUJRA_dataset['T_change_up_freq_trend_slpoe'][:]*364
CRUJRA_ATCc_slope=CRUJRA_dataset['T_change_down_freq_trend_slpoe'][:]*364
lat=CRUJRA_dataset['lat'][:]

dataset_ref = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/CRUJRA_sudden_T_change_freq_1970_2020.nc")

CRUJRA_mask=dataset_ref['T_change_up_freq'][:]

#CRUJRA_ATCw_slope[(lat < -60),:]=np.nan
#CRUJRA_ATCc_slope[(lat < -60),:]=np.nan

CRUJRA_ATCw_slope[CRUJRA_mask.mask]=np.nan
CRUJRA_ATCc_slope[CRUJRA_mask.mask]=np.nan


#==========================================load ERA5 data===========================================#

ERA5_dataset = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/ERA5_sudden_T_change_freq_MAT_sensitivity_1970_2020.nc")

ERA5_ATCw_pvalue=ERA5_dataset['T_change_up_freq_trend_p_value'][:]
ERA5_ATCc_pvalue=ERA5_dataset['T_change_down_freq_trend_p_value'][:]
ERA5_ATCw_slope=ERA5_dataset['T_change_up_freq_trend_slpoe'][:]*364
ERA5_ATCc_slope=ERA5_dataset['T_change_down_freq_trend_slpoe'][:]*364


#==========================================load CMIP6 data===========================================#

models=['ACCESS-ESM1-5','AWI-CM-1-1-MR','BCC-CSM2-MR','CanESM5','CESM2-WACCM','CMCC-ESM2','E3SM-1-0','EC-Earth3','FGOALS-g3','GFDL-ESM4',
        'IITM-ESM','INM-CM5-0','IPSL-CM6A','KACE-1-0-G','KIOST-ESM','MIROC6','MPI-ESM1-2-HR','NESM3','NorESM2','TaiESM1',]

ATCw_slope_CMIP6=[]
ATCc_slope_CMIP6=[]
ATCw_pvalue_CMIP6=[]
ATCc_pvalue_CMIP6=[]

#Global_ATCw_slope_CMIP6=[]
#Global_ATCc_slope_CMIP6=[]
#Northern_ATCw_slope_CMIP6=[]
#Northern_ATCc_slope_CMIP6=[]
#Southern_ATCw_slope_CMIP6=[]
#Southern_ATCc_slope_CMIP6=[]

for i, model in enumerate(models):
    print(model)
    dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/T_change_freq_"+str(model)+"_MAT_sensitivity_1970-2015-rescale.nc")
    if 'latitude' in dataset.variables:
        lat = dataset['latitude'][:]
        lon = dataset['longitude'][:]
    elif 'lat' in dataset.variables:
        lat = dataset['lat'][:]
        lon = dataset['lon'][:]
    
    ATCw_slope_CMIP6.append(dataset['T_change_up_freq_trend_slpoe'][:]*364)
    ATCc_slope_CMIP6.append(dataset['T_change_down_freq_trend_slpoe'][:]*364)
    ATCw_pvalue_CMIP6.append(dataset['T_change_up_freq_trend_p_value'][:])
    ATCc_pvalue_CMIP6.append(dataset['T_change_down_freq_trend_p_value'][:])    

#    sudden_Tmean_change_csv =pd.read_csv("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/multi-threshold/"+str(model)+"_T_sudden_change_±10°C_1970_2015_MAT.csv")
#    Global_ATCw_slope, _, _, Global_ATCw_pValue, _ = linregress(sudden_Tmean_change_csv ['Global_MAT'], sudden_Tmean_change_csv ['Global_ATCw'])
#    Global_ATCc_slope, _, _, Global_ATCc_pValue, _ = linregress(sudden_Tmean_change_csv ['Global_MAT'], sudden_Tmean_change_csv ['Global_ATCc'])
#    Northern_ATCw_slope, _, _, Northern_ATCw_pValue, _ = linregress(sudden_Tmean_change_csv ['Northern_MAT'], sudden_Tmean_change_csv ['Northern_ATCw'])
#    Northern_ATCc_slope, _, _, Northern_ATCc_pValue, _ = linregress(sudden_Tmean_change_csv ['Northern_MAT'], sudden_Tmean_change_csv ['Northern_ATCc'])
#    Southern_ATCw_slope, _, _, Southern_ATCw_pValue, _ = linregress(sudden_Tmean_change_csv ['Southern_MAT'], sudden_Tmean_change_csv ['Southern_ATCw'])
#    Southern_ATCc_slope, _, _, Southern_ATCc_pValue, _ = linregress(sudden_Tmean_change_csv ['Southern_MAT'], sudden_Tmean_change_csv ['Southern_ATCc'])

#    Global_ATCw_slope_CMIP6.append(Global_ATCw_slope if Global_ATCw_pValue < 0.05 else 0)
#    Global_ATCc_slope_CMIP6.append(Global_ATCc_slope if Global_ATCc_pValue < 0.05 else 0)
#    Northern_ATCw_slope_CMIP6.append(Northern_ATCw_slope if Northern_ATCw_pValue < 0.05 else 0)
#    Northern_ATCc_slope_CMIP6.append(Northern_ATCc_slope if Northern_ATCc_pValue < 0.05 else 0)
#    Southern_ATCw_slope_CMIP6.append(Southern_ATCw_slope if Southern_ATCw_pValue < 0.05 else 0)
#    Southern_ATCc_slope_CMIP6.append(Southern_ATCc_slope if Southern_ATCc_pValue < 0.05 else 0)
    
ATCw_slope_CMIP6 = np.array(ATCw_slope_CMIP6)  
ATCc_slope_CMIP6 = np.array(ATCc_slope_CMIP6)
ATCw_pvalue_CMIP6 = np.array(ATCw_pvalue_CMIP6)<= 0.05
ATCc_pvalue_CMIP6 = np.array(ATCc_pvalue_CMIP6)<= 0.05

ATCw_ave_CMIP6, ATCw_sig_mask = aggregate_slopes(ATCw_slope_CMIP6, ATCw_pvalue_CMIP6)
ATCc_ave_CMIP6, ATCc_sig_mask = aggregate_slopes(ATCc_slope_CMIP6, ATCc_pvalue_CMIP6)

ATCw_ave_CMIP6[dataset['T_change_up_freq_trend_slpoe'][:].mask]=np.nan
ATCc_ave_CMIP6[dataset['T_change_up_freq_trend_slpoe'][:].mask]=np.nan
ATCw_sig_mask[dataset['T_change_up_freq_trend_slpoe'][:].mask]=False
ATCc_sig_mask[dataset['T_change_up_freq_trend_slpoe'][:].mask]=False


models=['CRUJRA','ERA5','CMIP6']
Global_ATC_slope_std  =None
Northern_ATC_slope_std=None
Southern_ATC_slope_std=None


all_data = []
for i, model in enumerate(models):
    print(model)
    if model=='CRUJRA':
        dataset = CRUJRA_dataset
        ATCw_slope=CRUJRA_ATCw_slope.copy()
        ATCw_pvalue=CRUJRA_ATCw_pvalue.copy()
        ATCw_slope[ATCw_pvalue > 0.05] = 0
        ATCw_slope[ATCw_pvalue == 1] = np.nan
        
        ATCc_slope=CRUJRA_ATCc_slope.copy()
        ATCc_pvalue=CRUJRA_ATCc_pvalue.copy()
        ATCc_slope[ATCc_pvalue > 0.05] = 0
        ATCc_slope[ATCc_pvalue == 1] = np.nan

        data_area = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/CRUJRA_area.nc")
        area_weight=data_area['cell_area'][:]


    elif model=='ERA5':
        dataset = ERA5_dataset
        ATCw_slope=ERA5_ATCw_slope.copy()
        ATCw_pvalue=ERA5_ATCw_pvalue.copy()
        ATCw_slope[ATCw_pvalue > 0.05] = 0
        ATCw_slope[ATCw_pvalue == 1] = np.nan
        
        ATCc_slope=ERA5_ATCc_slope.copy()
        ATCc_pvalue=ERA5_ATCc_pvalue.copy()
        ATCc_slope[ATCc_pvalue > 0.05] = 0
        ATCc_slope[ATCc_pvalue == 1] = np.nan

        data_area = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/ERA5_area.nc")
        area_weight=data_area['cell_area'][:]


    else:
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/ACCESS-ESM1-5/T_change_freq_ACCESS-ESM1-5_MAT_sensitivity_1970-2015-rescale.nc")
        ATCw_slope=ATCw_ave_CMIP6.copy()
        ATCc_slope=ATCc_ave_CMIP6.copy()
        ATCw_slope[~np.isnan(ATCw_slope) & ~ATCw_sig_mask] = 0
        ATCc_slope[~np.isnan(ATCc_slope) & ~ATCc_sig_mask] = 0

        data_area = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/CMIP6_0.5d_area.nc")
        area_weight=data_area['cell_area'][:]


    if 'latitude' in dataset.variables:
        lat = dataset['latitude'][:]
        lon = dataset['longitude'][:]
    elif 'lat' in dataset.variables:
        lat = dataset['lat'][:]
        lon = dataset['lon'][:]

#    ATCw_slope_global_mean=np.nanmean(ATCw_slope[lat>-60,:])
#    ATCw_slope_NH_mean    =np.nanmean(ATCw_slope[lat>0,:])
#    ATCw_slope_SH_mean    =np.nanmean(ATCw_slope[(lat<0)&(lat>-60),:])
#    ATCw_slope_global_std =np.nanstd(ATCw_slope[lat>-60,:])
#    ATCw_slope_NH_std     =np.nanstd(ATCw_slope[lat>0,:])
#    ATCw_slope_SH_std     =np.nanstd(ATCw_slope[(lat<0)&(lat>-60),:])   
#
#
#    ATCc_slope_global_mean=np.nanmean(ATCc_slope[lat>-60,:])
#    ATCc_slope_NH_mean    =np.nanmean(ATCc_slope[lat>0,:])
#    ATCc_slope_SH_mean    =np.nanmean(ATCc_slope[(lat<0)&(lat>-60),:])
#    ATCc_slope_global_std =np.nanstd(ATCc_slope[lat>-60,:])
#    ATCc_slope_NH_std     =np.nanstd(ATCc_slope[lat>0,:])
#    ATCc_slope_SH_std     =np.nanstd(ATCc_slope[(lat<0)&(lat>-60),:])

    ATCw_slope_global_mean = weighted_nanmean(ATCw_slope, area_weight, lat > -60)
    ATCw_slope_NH_mean     = weighted_nanmean(ATCw_slope, area_weight, lat > 0)
    ATCw_slope_SH_mean     = weighted_nanmean(ATCw_slope, area_weight, (lat < 0) & (lat > -60))
    ATCw_slope_global_std  = weighted_nanstd(ATCw_slope, area_weight, lat > -60)
    ATCw_slope_NH_std      = weighted_nanstd(ATCw_slope, area_weight, lat > 0)
    ATCw_slope_SH_std      = weighted_nanstd(ATCw_slope, area_weight, (lat < 0) & (lat > -60))

    # ATCc_frac
    ATCc_slope_global_mean = weighted_nanmean(ATCc_slope, area_weight, lat > -60)
    ATCc_slope_NH_mean     = weighted_nanmean(ATCc_slope, area_weight, lat > 0)
    ATCc_slope_SH_mean     = weighted_nanmean(ATCc_slope, area_weight, (lat > -60) & (lat < 0))
    ATCc_slope_global_std  = weighted_nanstd(ATCc_slope, area_weight, lat > -60)
    ATCc_slope_NH_std      = weighted_nanstd(ATCc_slope, area_weight, lat > 0)
    ATCc_slope_SH_std      = weighted_nanstd(ATCc_slope, area_weight, (lat < 0) & (lat > -60))


    all_data.extend([
            {'Model': model, 'Region': 'Globe', 'Type': 'ATCw_sp', 'Value': ATCw_slope_global_mean,'error': ATCw_slope_global_std},
            {'Model': model, 'Region': 'Globe', 'Type': 'ATCc_sp', 'Value': ATCc_slope_global_mean,'error': ATCc_slope_global_std},
            {'Model': model, 'Region': 'NH'    , 'Type': 'ATCw_sp', 'Value': ATCw_slope_NH_mean,'error': ATCw_slope_NH_std},
            {'Model': model, 'Region': 'NH'    , 'Type': 'ATCc_sp', 'Value': ATCc_slope_NH_mean,'error': ATCc_slope_NH_std},
            {'Model': model, 'Region': 'SH'    , 'Type': 'ATCw_sp', 'Value': ATCw_slope_SH_mean,'error': ATCw_slope_SH_std},
            {'Model': model, 'Region': 'SH'    , 'Type': 'ATCc_sp', 'Value': ATCc_slope_SH_mean,'error': ATCc_slope_SH_std},
        ])

df = pd.DataFrame(all_data)
models = df['Model'].unique()
region = ['Globe', 'NH', 'SH']


#=========================================================plot======================================================#
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['axes.labelsize']  = 10
plt.rcParams['axes.titlesize']  = 10


fig = plt.figure(figsize=(7, 5)) # figsize=(width, heigh)
gs_top = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1], width_ratios=[1, 1], hspace=0.02, wspace=0.15,top=0.98,bottom=0.12,left=0.06,right=0.98)

axes = np.empty((3, 2), dtype=object)

for row in range(3):
    axes[row, 0] = fig.add_subplot(gs_top[row, 0], projection=ccrs.PlateCarree())  # 地图投影
    axes[row, 1] = fig.add_subplot(gs_top[row, 1], projection=ccrs.PlateCarree())  # 地图投影




cmap='RdBu_r'
cmap=mcolors.ListedColormap(sns.color_palette("RdBu_r", as_cmap=True)(np.linspace(0.2, 0.8, 256)))
vmin_time=-2
vmax_time=2

#==================================================CRUJRA trend============================================================#
lon=CRUJRA_dataset['lon'][:]
lat=CRUJRA_dataset['lat'][:]
lon2d, lat2d = np.meshgrid(lon, lat)

im_CRUJRA_ATCw_slope = axes[0, 0].pcolormesh(lon, lat, CRUJRA_ATCw_slope, transform=ccrs.PlateCarree(), cmap=cmap,vmin=vmin_time, vmax=vmax_time)
interval = 4
alpha=1
mask = (CRUJRA_ATCw_pvalue <= 0.05)
sample = np.zeros_like(mask)
sample[::interval, ::interval] = mask[::interval, ::interval]

# ← 用 lon2d 而不是 lon
axes[0, 0].scatter(lon2d[sample], lat2d[sample], s=0.2,color='black',transform=ccrs.PlateCarree(),linewidths=0,alpha=alpha)
axes[0, 0].add_feature(cfeature.COASTLINE,linewidth=0.2,edgecolor='black',alpha=0.6)
axes[0, 0].set_frame_on(False)
axes[0, 0].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())

axes[0,0].text(0.02, 1.02, "a", ha="left", va="top", transform=axes[0,0].transAxes, fontsize=14, weight='bold' )

im_CRUJRA_ATCc_slope = axes[0, 1].pcolormesh(lon, lat, CRUJRA_ATCc_slope, transform=ccrs.PlateCarree(), cmap=cmap,vmin=vmin_time, vmax=vmax_time)

mask = (CRUJRA_ATCc_pvalue <= 0.05)
sample = np.zeros_like(mask)
sample[::interval, ::interval] = mask[::interval, ::interval]

axes[0, 1].scatter(lon2d[sample], lat2d[sample], s=0.2,color='black',transform=ccrs.PlateCarree(),linewidths=0,alpha=alpha)
axes[0, 1].add_feature(cfeature.COASTLINE,linewidth=0.2,edgecolor='black',alpha=0.6)
axes[0, 1].set_frame_on(False)
axes[0, 1].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[0,1].text(0.02, 1.02, "b", ha="left", va="top", transform=axes[0,1].transAxes, fontsize=14, weight='bold' )

CRUJRA_df = df[df['Model'] == 'CRUJRA']
ATC_data = CRUJRA_df[CRUJRA_df['Type'] == 'ATCw_sp']
ATCc_frac_data = CRUJRA_df[CRUJRA_df['Type'] == 'ATCc_sp']
x = np.arange(len(region))
width = 0.5

left_err = np.where(ATC_data['Value'].values > 0, 0, ATC_data['error'].values)   # 正值时左边0，负值时完整误差
right_err = np.where(ATC_data['Value'].values < 0, 0, ATC_data['error'].values) # 负值时右边0，正值时完整误差

ax_inset1 = inset_axes(axes[0, 0], width="20%", height="40%", loc='lower left', bbox_to_anchor=(0.02, 0.03, 1, 1), bbox_transform=axes[0, 0].transAxes)
ax_inset1.errorbar(x=ATC_data['Value'].values, y=x, xerr=(left_err, right_err), capsize=2,  fmt='none', ecolor='black', alpha=0.8,capthick=0.5,elinewidth=0.5,zorder=1)
ax_inset1.barh(y=x, width=ATC_data['Value'].values, height=width, color='#F2E6D8', alpha=0.8, edgecolor='black', linewidth=0.5,zorder=2)

left_err = np.where(ATCc_frac_data['Value'].values > 0, 0, ATCc_frac_data['error'].values)   # 正值时左边0，负值时完整误差
right_err = np.where(ATCc_frac_data['Value'].values < 0, 0, ATCc_frac_data['error'].values) # 负值时右边0，正值时完整误差

ax_inset2 = inset_axes(axes[0, 1], width="20%", height="40%", loc='lower left', bbox_to_anchor=(0.02, 0.03, 1, 1), bbox_transform=axes[0, 1].transAxes)
ax_inset2.errorbar(x=ATCc_frac_data['Value'].values, y=x, xerr=(left_err, right_err), capsize=2,  fmt='none', ecolor='black', alpha=0.8,capthick=0.5,elinewidth=0.5,zorder=1)
ax_inset2.barh(y=x, width=ATCc_frac_data['Value'].values, height=width, color='#F2E6D8', alpha=0.8, edgecolor='black', linewidth=0.5,zorder=2)


#==================================================ERA5 trend============================================================#
interval = 12
lon=ERA5_dataset['lon'][:]
lat=ERA5_dataset['lat'][:]
lon2d, lat2d = np.meshgrid(lon, lat)

im_ERA5_ATCw_slope = axes[1, 0].pcolormesh(lon, lat, ERA5_ATCw_slope, transform=ccrs.PlateCarree(), cmap=cmap,vmin=vmin_time, vmax=vmax_time)
mask = (ERA5_ATCw_pvalue <= 0.05)
sample = np.zeros_like(mask)
sample[::interval, ::interval] = mask[::interval, ::interval]

axes[1, 0].scatter(lon2d[sample], lat2d[sample], s=0.2,color='black',transform=ccrs.PlateCarree(),linewidths=0,alpha=alpha)
axes[1, 0].add_feature(cfeature.COASTLINE,linewidth=0.2,edgecolor='black',alpha=0.6)
axes[1, 0].set_frame_on(False)
axes[1, 0].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[1, 0].text(0.02, 1.02, "c", ha="left", va="top", transform=axes[1, 0].transAxes, fontsize=14, weight='bold' )

im_ERA5_ATCc_slope = axes[1, 1].pcolormesh(lon, lat, ERA5_ATCc_slope, transform=ccrs.PlateCarree(), cmap=cmap,vmin=vmin_time, vmax=vmax_time)
mask = (ERA5_ATCc_pvalue <= 0.05)
sample = np.zeros_like(mask)
sample[::interval, ::interval] = mask[::interval, ::interval]

axes[1, 1].scatter(lon2d[sample], lat2d[sample], s=0.2,color='black',transform=ccrs.PlateCarree(),linewidths=0,alpha=alpha)
axes[1, 1].add_feature(cfeature.COASTLINE,linewidth=0.2,edgecolor='black',alpha=0.6)
axes[1, 1].set_frame_on(False)
axes[1, 1].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[1, 1].text(0.02, 1.02, "d", ha="left", va="top", transform=axes[1,1].transAxes, fontsize=14, weight='bold' )

ERA5_df = df[df['Model'] == 'ERA5']
ATC_data = ERA5_df[ERA5_df['Type'] == 'ATCw_sp']
ATCc_frac_data = ERA5_df[ERA5_df['Type'] == 'ATCc_sp']
x = np.arange(len(ATC_data))
width = 0.5

left_err = np.where(ATC_data['Value'].values > 0, 0, ATC_data['error'].values)   # 正值时左边0，负值时完整误差
right_err = np.where(ATC_data['Value'].values < 0, 0, ATC_data['error'].values) # 负值时右边0，正值时完整误差

ax_inset3 = inset_axes(axes[1, 0], width="20%", height="40%", loc='lower left', bbox_to_anchor=(0.02, 0.03, 1, 1), bbox_transform=axes[1, 0].transAxes)
ax_inset3.errorbar(x=ATC_data['Value'].values, y=x, xerr=(left_err, right_err), capsize=2,  fmt='none', ecolor='black', alpha=0.8,capthick=0.5,elinewidth=0.5,zorder=1)
ax_inset3.barh(y=x, width=ATC_data['Value'].values, height=width, color='#F2E6D8', alpha=0.8, edgecolor='black', linewidth=0.5,zorder=2)

left_err = np.where(ATCc_frac_data['Value'].values > 0, 0, ATCc_frac_data['error'].values)   # 正值时左边0，负值时完整误差
right_err = np.where(ATCc_frac_data['Value'].values < 0, 0, ATCc_frac_data['error'].values) # 负值时右边0，正值时完整误差

ax_inset4 = inset_axes(axes[1, 1], width="20%", height="40%", loc='lower left', bbox_to_anchor=(0.02, 0.03, 1, 1), bbox_transform=axes[1, 1].transAxes)
ax_inset4.errorbar(x=ATCc_frac_data['Value'].values, y=x, xerr=(left_err, right_err), capsize=2,  fmt='none', ecolor='black', alpha=0.8,capthick=0.5,elinewidth=0.5,zorder=1)
ax_inset4.barh(y=x, width=ATCc_frac_data['Value'].values, height=width, color='#F2E6D8', alpha=0.8, edgecolor='black', linewidth=0.5,zorder=2)


#==================================================CMIP6 trend============================================================#
interval = 3
dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/ACCESS-ESM1-5/T_change_freq_ACCESS-ESM1-5_MAT_sensitivity_1970-2015-rescale.nc")
lon=dataset['lon'][:]
lat=dataset['lat'][:]
lon2d, lat2d = np.meshgrid(lon, lat)

im_ATCw_ave_CMIP6 = axes[2, 0].pcolormesh(lon, lat, ATCw_ave_CMIP6, transform=ccrs.PlateCarree(), cmap=cmap,vmin=vmin_time, vmax=vmax_time)
mask = ATCw_sig_mask
sample = np.zeros_like(mask)
sample[::interval, ::interval] = mask[::interval, ::interval]

axes[2, 0].scatter(lon2d[sample], lat2d[sample], s=0.2,color='black',transform=ccrs.PlateCarree(),linewidths=0,alpha=alpha)
axes[2, 0].add_feature(cfeature.COASTLINE,linewidth=0.2,edgecolor='black',alpha=0.6)
axes[2, 0].set_frame_on(False)
axes[2, 0].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[2, 0].text(0.02, 1.02, "e", ha="left", va="top", transform=axes[2, 0].transAxes, fontsize=14, weight='bold' )

im_ATCc_ave_CMIP6 = axes[2, 1].pcolormesh(lon, lat, ATCc_ave_CMIP6, transform=ccrs.PlateCarree(), cmap=cmap,vmin=vmin_time, vmax=vmax_time)
mask = ATCc_sig_mask
sample = np.zeros_like(mask)
sample[::interval, ::interval] = mask[::interval, ::interval]

axes[2, 1].scatter(lon2d[sample], lat2d[sample], s=0.2,color='black',transform=ccrs.PlateCarree(),linewidths=0,alpha=alpha)
axes[2, 1].add_feature(cfeature.COASTLINE,linewidth=0.2,edgecolor='black',alpha=0.6)
axes[2, 1].set_frame_on(False)
axes[2, 1].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[2, 1].text(0.02, 1.02, "f", ha="left", va="top", transform=axes[2, 1].transAxes, fontsize=14, weight='bold' )

CMIP6_df = df[df['Model'] == 'CMIP6']
ATC_data = CMIP6_df[CMIP6_df['Type'] == 'ATCw_sp']
print(ATC_data)
ATCc_frac_data = CMIP6_df[CMIP6_df['Type'] == 'ATCc_sp']
x = np.arange(len(ATC_data))
width = 0.5

left_err = np.where(ATC_data['Value'].values > 0, 0, ATC_data['error'].values)   # 正值时左边0，负值时完整误差
right_err = np.where(ATC_data['Value'].values < 0, 0, ATC_data['error'].values) # 负值时右边0，正值时完整误差

ax_inset5 = inset_axes(axes[2, 0], width="20%", height="40%", loc='lower left', bbox_to_anchor=(0.02, 0.03, 1, 1), bbox_transform=axes[2, 0].transAxes)
ax_inset5.errorbar(x=ATC_data['Value'].values, y=x, xerr=(left_err, right_err), capsize=2,  fmt='none', ecolor='black', alpha=0.8,capthick=0.5,elinewidth=0.5,zorder=1)
ax_inset5.barh(y=x, width=ATC_data['Value'].values, height=width, color='#F2E6D8', alpha=0.8, edgecolor='black', linewidth=0.5,zorder=2)

left_err = np.where(ATCc_frac_data['Value'].values > 0, 0, ATCc_frac_data['error'].values)   # 正值时左边0，负值时完整误差
right_err = np.where(ATCc_frac_data['Value'].values < 0, 0, ATCc_frac_data['error'].values) # 负值时右边0，正值时完整误差

ax_inset6 = inset_axes(axes[2, 1], width="20%", height="40%", loc='lower left', bbox_to_anchor=(0.02, 0.03, 1, 1), bbox_transform=axes[2, 1].transAxes)
ax_inset6.errorbar(x=ATCc_frac_data['Value'].values, y=x, xerr=(left_err, right_err), capsize=2,  fmt='none', ecolor='black', alpha=0.8,capthick=0.5,elinewidth=0.5,zorder=1)
ax_inset6.barh(y=x, width=ATCc_frac_data['Value'].values, height=width, color='#F2E6D8', alpha=0.8, edgecolor='black', linewidth=0.5,zorder=2)


ax_insets = [ax_inset1,ax_inset2,ax_inset3,ax_inset4,ax_inset5,ax_inset6,]
[ax.spines['top'].set_visible(False)   for ax in ax_insets]
[ax.spines['left'].set_visible(False)  for ax in ax_insets]
[ax.spines['right'].set_visible(False) for ax in ax_insets]
[ax.axvline(x=0, color='gray', linestyle='-', linewidth=0.8, alpha=0.7) for ax in ax_insets]
[ax.set_ylim(-0.5, len(region) -0.5)   for ax in ax_insets]
[ax.set_yticks(np.arange(len(region)))   for ax in ax_insets]
[ax.set_yticklabels(region)   for ax in ax_insets]
[ax.invert_yaxis()   for ax in ax_insets]
[ax.tick_params(axis='y', length=0)   for ax in ax_insets]

[ax.set_xlim(-1, 1)   for ax in [ax_inset1,ax_inset3,ax_inset5]]
[ax.set_xticks([-1,0,1])   for ax in [ax_inset1,ax_inset3,ax_inset5,]]
[ax.set_xticklabels(['-1','0',"1"])   for ax in [ax_inset1,ax_inset3,ax_inset5,]]
[ax.set_xlim(-1, 1)    for ax in [ax_inset2,ax_inset4,ax_inset6,]]
[ax.set_xticks([-1,0,1])   for ax in [ax_inset2,ax_inset4,ax_inset6,]]
[ax.set_xticklabels(['-1','0',"1"])   for ax in [ax_inset2,ax_inset4,ax_inset6,]]


#======legend=======#
cbar_time_ax = fig.add_axes([0.16, 0.04, 0.3, 0.010])  # [left, bottom, width, height]
cbar_time=fig.colorbar(im_CRUJRA_ATCc_slope, cax=cbar_time_ax, orientation='horizontal', extend='both')
cbar_time.outline.set_linewidth(0.5)  # 设置线宽
cbar_time.outline.set_edgecolor('gray')  # 设置边框颜色
cbar_time.set_ticks([vmin_time,vmin_time/2,0,vmax_time*0.5,vmax_time])  # 设置刻度位置
cbar_time.set_ticklabels([
    f'{vmin_time:.0f}',
    f'{vmin_time/2:.0f}',
    '0',
    f'{vmax_time*0.5:.0f}',
    f'{vmax_time:.0f}'
])
cbar_time.ax.tick_params(axis='y', length=2, color='gray', width=1,  labelsize=10, labelcolor='black' )
cbar_time.set_label('Sensitivity of ATC occurrence to MAT (°C⁻¹)', fontsize=10, labelpad=-32)



#=====================================间距调整==========================================#
#plt.subplots_adjust(left=0.05, right=0.95, bottom=0.1 , top=0.97,wspace=0.05, hspace=0.1)
   

#plt.tight_layout()
fig1 = plt.gcf()
script_name = os.path.splitext(os.path.basename(__file__))[0]
fig1.savefig(str(current_directory)+f"/{script_name}.png", dpi=300)
#plt.show()


