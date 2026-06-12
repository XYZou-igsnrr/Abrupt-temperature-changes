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
from matplotlib.colors import TwoSlopeNorm


current_directory = os.path.dirname(os.path.abspath(__file__))

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

CRUJRA_dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/ATC_trend_spatial_±10°C_1970_2020_MK.nc")

CRUJRA_ATC_pvalue=CRUJRA_dataset['ATC_trend_p_value'][:]
CRUJRA_ATC_slope=CRUJRA_dataset['ATC_trend_slope'][:]*365
lat=CRUJRA_dataset['lat'][:]

dataset_ref = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/CRUJRA_sudden_T_change_freq_1970_2020.nc")

CRUJRA_mask=dataset_ref['T_change_up_freq'][:]

#CRUJRA_ATCw_slope[(lat < -60),:]=np.nan
#CRUJRA_ATCc_slope[(lat < -60),:]=np.nan

#CRUJRA_ATC_slope[CRUJRA_mask.mask]=np.nan

CRUJRA_dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/EOF/CRUJRA_sudden_T_change_freq_trend_±10°C_1970_2020_yearly.nc")

CRUJRA_ATCw=CRUJRA_dataset['T_change_up_freq'][:]
CRUJRA_ATCc=CRUJRA_dataset['T_change_down_freq'][:]
CRUJRA_ATC_frac=CRUJRA_ATCc[:]/(CRUJRA_ATCw[:]+CRUJRA_ATCc[:])
CRUJRA_ATC_frac_d=(np.nanmean(CRUJRA_ATC_frac[-10:,:,:],axis=0)-np.nanmean(CRUJRA_ATC_frac[:10,:,:],axis=0))/CRUJRA_ATC_frac.shape[0]


#==========================================load ERA5 data===========================================#

ERA5_dataset = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/ERA5_ATC_trend_1970_2020_mk.nc")

ERA5_ATC_pvalue=ERA5_dataset['ATC_trend_p_value'][:]
ERA5_ATC_slope=ERA5_dataset['ATC_trend_slope'][:]*365

ERA5_dataset = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/LFCA/T_change_freq_ERA5_yearly_1970-2020.nc")

ERA5_ATCw=ERA5_dataset['T_change_up_freq'][:]
ERA5_ATCc=ERA5_dataset['T_change_down_freq'][:]
ERA5_ATC_frac=ERA5_ATCc[:]/(ERA5_ATCw[:]+ERA5_ATCc[:])
ERA5_ATC_frac_d=(np.nanmean(ERA5_ATC_frac[-10:,:,:],axis=0)-np.nanmean(ERA5_ATC_frac[:10,:,:],axis=0))/ERA5_ATC_frac.shape[0]

#==========================================load CMIP6 data===========================================#

models=['ACCESS-ESM1-5','AWI-CM-1-1-MR','BCC-CSM2-MR','CanESM5','CESM2-WACCM','CMCC-ESM2','E3SM-1-0','EC-Earth3','FGOALS-g3','GFDL-ESM4',
        'IITM-ESM','INM-CM5-0','IPSL-CM6A','KACE-1-0-G','KIOST-ESM','MIROC6','MPI-ESM1-2-HR','NESM3','NorESM2','TaiESM1',]

ATC_slope_CMIP6=[]
ATC_pvalue_CMIP6=[]

Global_ATC_slope_CMIP6=[]
NH_ATC_slope_CMIP6=[]
SH_ATC_slope_CMIP6=[]

CMIP6_ATC_frac_d=[]

for i, model in enumerate(models):
    print(model)
    dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/T_change_freq_"+str(model)+"_yearly_1970-2015_mk-rescale.nc")
    if 'latitude' in dataset.variables:
        lat = dataset['latitude'][:]
        lon = dataset['longitude'][:]
    elif 'lat' in dataset.variables:
        lat = dataset['lat'][:]
        lon = dataset['lon'][:]
    
    ATC_slope_CMIP6.append(dataset['ATC_trend_slope'][:]*365)
    ATC_pvalue_CMIP6.append(dataset['ATC_trend_p_value'][:])

    ATCw = np.array(dataset['T_change_up_freq'][:])
    ATCc = np.array(dataset['T_change_down_freq'][:])
    ATC_frac=ATCc[:]/(ATCw[:]+ATCc[:])
    ATC_frac_d=(np.nanmean(ATC_frac[-10:,:,:],axis=0)-np.nanmean(ATC_frac[:10,:,:],axis=0))/ATC_frac.shape[0]

    CMIP6_ATC_frac_d.append(ATC_frac_d)

    
ATC_slope_CMIP6 = np.array(ATC_slope_CMIP6)
ATC_pvalue_CMIP6 = np.array(ATC_pvalue_CMIP6)<= 0.05

ATC_ave_CMIP6, ATC_sig_mask = aggregate_slopes(ATC_slope_CMIP6, ATC_pvalue_CMIP6)

CMIP6_ATC_frac_d=np.nanmean(CMIP6_ATC_frac_d,axis=0)


models=['CRUJRA','ERA5','CMIP6']
Global_ATC_slope_std  =None
Northern_ATC_slope_std=None
Southern_ATC_slope_std=None


all_data = []
for i, model in enumerate(models):
    print(model)
    if model=='CRUJRA':
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/CRUJRA_sudden_T_change_freq_trend_±10°C_1970_2020.nc")
        ATC_slope=CRUJRA_ATC_slope.copy()
        ATC_pvalue=CRUJRA_ATC_pvalue.copy()
        ATC_slope[ATC_pvalue > 0.05] = 0
        ATC_slope[ATC_pvalue == 1] = np.nan
        ATC_frac_d  =CRUJRA_ATC_frac_d.copy()


    elif model=='ERA5':
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/ERA5_ATC_trend_1970_2020_mk.nc")
        ATC_slope=ERA5_ATC_slope.copy()
        ATC_pvalue=ERA5_ATC_pvalue.copy()
        ATC_slope[ATC_pvalue > 0.05] = 0
        ATC_slope[ATC_pvalue == 1] = np.nan
        ATC_frac_d  =ERA5_ATC_frac_d.copy()


    else:
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/ACCESS-ESM1-5/T_change_freq_ACCESS-ESM1-5_yearly_1970-2015_mk-rescale.nc")
        ATC_slope=ATC_ave_CMIP6.copy()
        ATC_slope[~np.isnan(ATC_slope) & ~ATC_sig_mask] = 0
        ATC_frac_d  =CMIP6_ATC_frac_d.copy()


    if 'latitude' in dataset.variables:
        lat = dataset['latitude'][:]
        lon = dataset['longitude'][:]
    elif 'lat' in dataset.variables:
        lat = dataset['lat'][:]
        lon = dataset['lon'][:]


    #stats.sem(data_2d, nan_policy=nan_policy)

    ATC_slope_global_mean=np.nanmean(ATC_slope[lat>-60,:])
    ATC_slope_NH_mean    =np.nanmean(ATC_slope[lat>0,:])
    ATC_slope_SH_mean    =np.nanmean(ATC_slope[(lat<0)&(lat>-60),:])
    ATC_slope_global_std =np.nanstd(ATC_slope[lat>-60,:])
    ATC_slope_NH_std     =np.nanstd(ATC_slope[lat>0,:])
    ATC_slope_SH_std     =np.nanstd(ATC_slope[(lat<0)&(lat>-60),:])

    global_ATC_frac_d_mean  =np.nanmean(ATC_frac_d[lat>-60,:])
    NH_ATC_frac_d_mean=np.nanmean(ATC_frac_d[lat>0,:])
    SH_ATC_frac_d_mean=np.nanmean(ATC_frac_d[(lat > -60) & (lat < 0),:])
    global_ATC_frac_d_std   =np.nanstd(ATC_frac_d[lat>-60,:])
    NH_ATC_frac_d_std =np.nanstd(ATC_frac_d[lat>0,:])
    SH_ATC_frac_d_std =np.nanstd(ATC_frac_d[(lat<0)&(lat>-60),:])


    all_data.extend([
            {'Model': model, 'Region': 'Globe', 'Type': 'ATC_slope_sp', 'Value': ATC_slope_global_mean,'error': ATC_slope_global_std},
            {'Model': model, 'Region': 'NH'    , 'Type': 'ATC_slope_sp', 'Value': ATC_slope_NH_mean,'error': ATC_slope_NH_std},
            {'Model': model, 'Region': 'SH'    , 'Type': 'ATC_slope_sp', 'Value': ATC_slope_SH_mean,'error': ATC_slope_SH_std},

            {'Model': model, 'Region': 'Globe', 'Type': 'ATC_frac_d', 'Value': global_ATC_frac_d_mean,'error': global_ATC_frac_d_std},
            {'Model': model, 'Region': 'NH'    , 'Type': 'ATC_frac_d', 'Value': NH_ATC_frac_d_mean,'error': NH_ATC_frac_d_std},
            {'Model': model, 'Region': 'SH'    , 'Type': 'ATC_frac_d', 'Value': SH_ATC_frac_d_mean,'error': SH_ATC_frac_d_std},
        ])

df = pd.DataFrame(all_data)
models = df['Model'].unique()
region = ['Globe', 'NH', 'SH']

print(df)

#=========================================================plot======================================================#
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['axes.labelsize']  = 10
plt.rcParams['axes.titlesize']  = 10


fig = plt.figure(figsize=(7, 5)) # figsize=(width, heigh)
gs_top = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1], width_ratios=[1, 1], hspace=0.02, wspace=0.15,top=0.98,bottom=0.1,left=0.06,right=0.98)

axes = np.empty((3, 2), dtype=object)

for row in range(3):
    axes[row, 0] = fig.add_subplot(gs_top[row, 0], projection=ccrs.PlateCarree())  # 地图投影
    axes[row, 1] = fig.add_subplot(gs_top[row, 1], projection=ccrs.PlateCarree())  # 地图投影





vmin_time=-0.10
vmax_time=0.04

vmin_d=-0.004
vmax_d=0.004


cmap=mcolors.ListedColormap(sns.color_palette("RdBu_r", as_cmap=True)(np.linspace(0.2, 0.8, 256)))
norm = TwoSlopeNorm(vmin=vmin_time, vcenter=0, vmax=vmax_time)


#==================================================CRUJRA trend============================================================#
lon=CRUJRA_dataset['lon'][:]
lat=CRUJRA_dataset['lat'][:]
lon2d, lat2d = np.meshgrid(lon, lat)

im_CRUJRA_ATC_slope = axes[0, 0].pcolormesh(lon, lat, CRUJRA_ATC_slope, transform=ccrs.PlateCarree(), cmap=cmap,norm=norm)
interval = 4
alpha=1
mask = (CRUJRA_ATC_pvalue <= 0.05)
sample = np.zeros_like(mask)
sample[::interval, ::interval] = mask[::interval, ::interval]

# ← 用 lon2d 而不是 lon
axes[0, 0].scatter(lon2d[sample], lat2d[sample], s=0.2,color='black',transform=ccrs.PlateCarree(),linewidths=0,alpha=alpha)
axes[0, 0].add_feature(cfeature.COASTLINE,linewidth=0.2,edgecolor='black',alpha=0.6)
axes[0, 0].set_frame_on(False)
axes[0, 0].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())

axes[0,0].text(0.02, 1.02, "a", ha="left", va="top", transform=axes[0,0].transAxes, fontsize=14, weight='bold' )


im_CRUJRA_ATC_frac_d = axes[0, 1].pcolormesh(lon, lat, CRUJRA_ATC_frac_d, transform=ccrs.PlateCarree(), cmap=cmap,vmin=vmin_d, vmax=vmax_d)
axes[0, 1].add_feature(cfeature.COASTLINE,linewidth=0.2,edgecolor='black',alpha=0.6)
axes[0, 1].add_feature(cfeature.LAND, facecolor='gray', alpha=0.3, zorder=0)
axes[0, 1].set_frame_on(False)
axes[0, 1].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[0,1].text(0.02, 1.02, "b", ha="left", va="top", transform=axes[0,1].transAxes, fontsize=14, weight='bold' )

CRUJRA_df = df[df['Model'] == 'CRUJRA']
ATC_data = CRUJRA_df[CRUJRA_df['Type'] == 'ATC_slope_sp']
ATCc_frac_data = CRUJRA_df[CRUJRA_df['Type'] == 'ATC_frac_d']
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

im_ERA5_ATC_slope = axes[1, 0].pcolormesh(lon, lat, ERA5_ATC_slope, transform=ccrs.PlateCarree(), cmap=cmap,norm=norm)
mask = (ERA5_ATC_pvalue <= 0.05)
sample = np.zeros_like(mask)
sample[::interval, ::interval] = mask[::interval, ::interval]

axes[1, 0].scatter(lon2d[sample], lat2d[sample], s=0.2,color='black',transform=ccrs.PlateCarree(),linewidths=0,alpha=alpha)
axes[1, 0].add_feature(cfeature.COASTLINE,linewidth=0.2,edgecolor='black',alpha=0.6)
axes[1, 0].set_frame_on(False)
axes[1, 0].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[1, 0].text(0.02, 1.02, "c", ha="left", va="top", transform=axes[1, 0].transAxes, fontsize=14, weight='bold' )

im_ERA5_ATC_frac_d = axes[1, 1].pcolormesh(lon, lat, ERA5_ATC_frac_d, transform=ccrs.PlateCarree(), cmap=cmap,vmin=vmin_d, vmax=vmax_d)
axes[1, 1].add_feature(cfeature.COASTLINE,linewidth=0.2,edgecolor='black',alpha=0.6)
axes[1, 1].add_feature(cfeature.LAND, facecolor='gray', alpha=0.3, zorder=0)
axes[1, 1].set_frame_on(False)
axes[1, 1].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[1, 1].text(0.02, 1.02, "d", ha="left", va="top", transform=axes[1,1].transAxes, fontsize=14, weight='bold' )

ERA5_df = df[df['Model'] == 'ERA5']
ATC_data = ERA5_df[ERA5_df['Type'] == 'ATC_slope_sp']
ATCc_frac_data = ERA5_df[ERA5_df['Type'] == 'ATC_frac_d']
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
interval = 4
lon=dataset['lon'][:]
lat=dataset['lat'][:]
lon2d, lat2d = np.meshgrid(lon, lat)

im_CMIP6_ATC_slope = axes[2, 0].pcolormesh(lon, lat, ATC_ave_CMIP6, transform=ccrs.PlateCarree(), cmap=cmap,norm=norm)
mask = ATC_sig_mask
sample = np.zeros_like(mask)
sample[::interval, ::interval] = mask[::interval, ::interval]

total = np.sum(~np.isnan(ATC_ave_CMIP6))
points = np.sum((mask == 1) & (~np.isnan(ATC_ave_CMIP6)))
ratio = points / total * 100
print(f"打点占比: {ratio:.2f}% ({points}/{total})")

axes[2, 0].scatter(lon2d[sample], lat2d[sample], s=0.2,color='black',transform=ccrs.PlateCarree(),linewidths=0,alpha=alpha)
axes[2, 0].add_feature(cfeature.COASTLINE,linewidth=0.2,edgecolor='black',alpha=0.6)
axes[2, 0].set_frame_on(False)
axes[2, 0].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[2, 0].text(0.02, 1.02, "e", ha="left", va="top", transform=axes[2, 0].transAxes, fontsize=14, weight='bold' )

im_CMIP6_ATC_frac_d = axes[2, 1].pcolormesh(lon, lat, CMIP6_ATC_frac_d, transform=ccrs.PlateCarree(), cmap=cmap,vmin=vmin_d, vmax=vmax_d)
axes[2, 1].add_feature(cfeature.COASTLINE,linewidth=0.2,edgecolor='black',alpha=0.6)
axes[2, 1].add_feature(cfeature.LAND, facecolor='gray', alpha=0.3, zorder=0)
axes[2, 1].set_frame_on(False)
axes[2, 1].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
axes[2, 1].text(0.02, 1.02, "f", ha="left", va="top", transform=axes[2, 1].transAxes, fontsize=14, weight='bold' )

CMIP6_df = df[df['Model'] == 'CMIP6']
ATC_data = CMIP6_df[CMIP6_df['Type'] == 'ATC_slope_sp']
#print(ATC_data)
ATCc_frac_data = CMIP6_df[CMIP6_df['Type'] == 'ATC_frac_d']
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

[ax.set_xlim(-0.08, 0.08)   for ax in [ax_inset1,ax_inset3,ax_inset5]]
[ax.set_xticks([-0.06,0,0.06])   for ax in [ax_inset1,ax_inset3,ax_inset5,]]
[ax.set_xticklabels(['-0.06','0',"0.06"])   for ax in [ax_inset1,ax_inset3,ax_inset5,]]
[ax.set_xlim(-0.005, 0.005)    for ax in [ax_inset2,ax_inset4,ax_inset6,]]
[ax.set_xticks([-0.004,0,0.004])   for ax in [ax_inset2,ax_inset4,ax_inset6,]]
[ax.set_xticklabels(['-0.4%','0',"0.4%"])   for ax in [ax_inset2,ax_inset4,ax_inset6,]]


#======legend=======#
cbar_time_ax = fig.add_axes([0.13, 0.05, 0.3, 0.010])  # [left, bottom, width, height]
cbar_time=fig.colorbar(im_CRUJRA_ATC_slope, cax=cbar_time_ax, orientation='horizontal', extend='both')
cbar_time.outline.set_linewidth(0.5)  # 设置线宽
cbar_time.outline.set_edgecolor('gray')  # 设置边框颜色
cbar_time.set_ticks([vmin_time,vmin_time/2,0,vmax_time*0.5,vmax_time])  # 设置刻度位置
cbar_time.set_ticklabels([
    f'{vmin_time:.2f}',
    f'{vmin_time/2:.2f}',
    '0',
    f'{vmax_time*0.5:.2f}',
    f'{vmax_time:.2f}'
])
cbar_time.ax.tick_params(axis='y', length=2, color='gray', width=1,  labelsize=10, labelcolor='black' )
cbar_time.set_label('ATC trend (yr⁻²)', fontsize=10, labelpad=-32)


cbar_time_ax_d = fig.add_axes([0.65, 0.05, 0.30, 0.010])  # [left, bottom, width, height]
cbar_time_d=fig.colorbar(im_ERA5_ATC_frac_d, cax=cbar_time_ax_d, orientation='horizontal', extend='both')
cbar_time_d.set_ticks([vmin_d,vmin_d/2,0,vmax_d*0.5,vmax_d])  # 设置刻度位置
#cbar_time_d.set_ticklabels([f'{t*100:.2f}%' for t in [vmin_d,vmin_d/2,0,vmax_d*0.5,vmax_d]])
cbar_time_d.set_ticklabels([
    f'{vmin_d*100:.1f}%',
    f'{vmin_d/2*100:.1f}%',
    '0%',
    f'{vmax_d*0.5*100:.1f}%',
    f'{vmax_d*100:.1f}%'
])
cbar_time_d.outline.set_linewidth(0.5)  # 设置线宽
cbar_time_d.outline.set_edgecolor('gray')  # 设置边框颜色
cbar_time_d.ax.tick_params(axis='y', length=2, color='gray', width=1,labelsize=10,)
cbar_time_d.set_label('ATCc fraction change (yr⁻¹)', fontsize=10, labelpad=-32)


#=====================================间距调整==========================================#
#plt.subplots_adjust(left=0.05, right=0.95, bottom=0.1 , top=0.97,wspace=0.05, hspace=0.1)
   

#plt.tight_layout()
fig1 = plt.gcf()
script_name = os.path.splitext(os.path.basename(__file__))[0]
fig1.savefig(str(current_directory)+f"/{script_name}.png", dpi=300)
#plt.show()


