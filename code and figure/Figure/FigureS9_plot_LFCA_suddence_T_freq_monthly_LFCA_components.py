# -*- coding: utf-8 -*-
import os
from eofs.standard import Eof
import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.gridspec as gridspec
import seaborn as sns
import pandas as pd
from scipy.ndimage import uniform_filter1d
import matplotlib.dates as mdates


current_directory = os.path.dirname(os.path.abspath(__file__))

dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/LFCA/LFCA_result_monthly_1970_2020.nc")
lat = dataset["lat"][:]
lon = dataset["lon"][:]


eof2_up=dataset["lfps_up"][1,:]
eof3_up=dataset["lfps_up"][2,:]
eof4_up=dataset["lfps_up"][3,:]


eof2_down=dataset["lfps_down"][1,:]
eof3_down=dataset["lfps_down"][2,:]
eof4_down=dataset["lfps_down"][3,:]


eof_pc2_up=dataset["lfcs_up"][1,:]
eof_pc3_up=dataset["lfcs_up"][2,:]
eof_pc4_up=dataset["lfcs_up"][3,:]


eof_pc2_down=dataset["lfcs_down"][1,:]
eof_pc3_down=dataset["lfcs_down"][2,:]
eof_pc4_down=dataset["lfcs_down"][3,:]



#===============================================plot====================================================#
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['axes.labelsize']  = 12
plt.rcParams['axes.titlesize']  = 12


fig = plt.figure(figsize=(13.5, 10))# figsize=(width, height)

axes = np.array([
    [fig.add_subplot(4, 3, 1, projection=ccrs.PlateCarree()),
     fig.add_subplot(4, 3, 2, projection=ccrs.PlateCarree()),
     fig.add_subplot(4, 3, 3, projection=ccrs.PlateCarree())],

    [fig.add_subplot(4, 3, 4),
     fig.add_subplot(4, 3, 5),
     fig.add_subplot(4, 3, 6)],

    [fig.add_subplot(4, 3, 7, projection=ccrs.PlateCarree()),
     fig.add_subplot(4, 3, 8, projection=ccrs.PlateCarree()),
     fig.add_subplot(4, 3, 9, projection=ccrs.PlateCarree())],

    [fig.add_subplot(4, 3, 10),
     fig.add_subplot(4, 3, 11),
     fig.add_subplot(4, 3, 12)]
])


cmap='RdBu_r'
vmin_spatial=-0.01
vmax_spatial=0.01
linewidth=1.5

vmin_time=-2
vmax_time=2
#==============================================map ATCw=====================================================#
im_eof2_up = axes[0,0].pcolormesh(lon, lat, eof2_up, transform=ccrs.PlateCarree(), cmap=cmap,vmin=vmin_spatial, vmax=vmax_spatial)
axes[0,0].add_feature(cfeature.COASTLINE)
axes[0,0].set_title(r'ATC$_w$ LFP-2',fontsize=16, )
axes[0,0].text(0, 1.04, "a", transform=axes[0,0].transAxes, fontsize=axes[0,0].title.get_fontsize()+2, verticalalignment='bottom', horizontalalignment='left', fontweight='bold',)
axes[0,0].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree(central_longitude=0))
axes[0,0].set_xticks([-180, -90, 0, 90, 180], crs=ccrs.PlateCarree())
axes[0,0].set_yticks([-60,-30, 0, 30, 60,90], crs=ccrs.PlateCarree())
axes[0,0].set_xticklabels(['180°W', '90°W', '0°', '90°E', '180°E'])
axes[0,0].set_yticklabels(['60°S', '30°S', '0°', '30°N', '60°N', '90°N'])

im_eof3_up = axes[0,1].pcolormesh(lon, lat, eof3_up, transform=ccrs.PlateCarree(), cmap=cmap,vmin=vmin_spatial, vmax=vmax_spatial)
axes[0,1].add_feature(cfeature.COASTLINE)
axes[0,1].set_title(r'ATC$_w$ LFP-3',fontsize=16)
axes[0,1].text(0, 1.04, "b", transform=axes[0,1].transAxes, fontsize=axes[0,1].title.get_fontsize()+2, verticalalignment='bottom', horizontalalignment='left', fontweight='bold',)
axes[0,1].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree(central_longitude=0))
axes[0,1].set_xticks([-180, -90, 0, 90, 180], crs=ccrs.PlateCarree())
axes[0,1].set_yticks([-60,-30, 0, 30, 60,90], crs=ccrs.PlateCarree())
axes[0,1].set_xticklabels(['180°W', '90°W', '0°', '90°E', '180°E'])
axes[0,1].set_yticklabels(['60°S', '30°S', '0°', '30°N', '60°N', '90°N'])

im_eof4_up = axes[0,2].pcolormesh(lon, lat, eof4_up, transform=ccrs.PlateCarree(), cmap=cmap,vmin=vmin_spatial, vmax=vmax_spatial)
axes[0,2].add_feature(cfeature.COASTLINE)
axes[0,2].set_title(r'ATC$_w$ LFP-4',fontsize=16)
axes[0,2].text(0, 1.04, "c", transform=axes[0,2].transAxes, fontsize=axes[0,2].title.get_fontsize()+2, verticalalignment='bottom', horizontalalignment='left', fontweight='bold',)
axes[0,2].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree(central_longitude=0))
axes[0,2].set_xticks([-180, -90, 0, 90, 180], crs=ccrs.PlateCarree())
axes[0,2].set_yticks([-60,-30, 0, 30, 60,90], crs=ccrs.PlateCarree())
axes[0,2].set_xticklabels(['180°W', '90°W', '0°', '90°E', '180°E'])
axes[0,2].set_yticklabels(['60°S', '30°S', '0°', '30°N', '60°N', '90°N'])


#===================================line ATCw=====================================================#
date_range = pd.date_range('1970-01-01', '2020-12-31', freq='ME')

sns.lineplot(x=date_range, y=eof_pc2_up, ax=axes[1,0],linewidth=linewidth, alpha=0.5,color='lightgray')
sns.lineplot(x=date_range, y=uniform_filter1d(eof_pc2_up, size=10, mode='nearest'), ax=axes[1,0],linewidth=linewidth, alpha=0.8,color='black')
axes[1,0].axhline(0, color='red', linestyle='--', alpha=0.5)
axes[1,0].set_title(r'ATC$_w$ LFC-2',fontsize=16)
axes[1,0].text(0, 1.04, "d", transform=axes[1,0].transAxes, fontsize=axes[1,0].title.get_fontsize()+2, verticalalignment='bottom', horizontalalignment='left', fontweight='bold',)
axes[1,0].set_xlabel('')
#axes[0,1].set_xlim(1970, 2020)
axes[1,0].set_ylim(-2.8, 2.8)
axes[1,0].xaxis.set_major_locator(mdates.YearLocator(10))  # 每10年一个主刻度
axes[1,0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # 只显示年份
axes[1,0].set_xlim([pd.Timestamp('1970-01-01'), pd.Timestamp('2020-12-31')])

sns.lineplot(x=date_range, y=eof_pc3_up, ax=axes[1, 1],linewidth=linewidth, alpha=0.5,color='lightgray')
sns.lineplot(x=date_range, y=uniform_filter1d(eof_pc3_up, size=10, mode='nearest'), ax=axes[1, 1],linewidth=linewidth, alpha=0.8,color='black')
axes[1, 1].axhline(0, color='red', linestyle='--', alpha=0.5)
axes[1, 1].set_title(r'ATC$_w$ LFC-3',fontsize=16)
axes[1,1].text(0, 1.04, "e", transform=axes[1,1].transAxes, fontsize=axes[1,1].title.get_fontsize()+2, verticalalignment='bottom', horizontalalignment='left', fontweight='bold',)
axes[1, 1].set_xlabel('')
#axes[1, 1].set_xlim(1970, 2020)
axes[1, 1].set_ylim(-2.8, 2.8)
axes[1,1].xaxis.set_major_locator(mdates.YearLocator(10))  # 每10年一个主刻度
axes[1,1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # 只显示年份
axes[1,1].set_xlim([pd.Timestamp('1970-01-01'), pd.Timestamp('2020-12-31')])

sns.lineplot(x=date_range, y=eof_pc4_up, ax=axes[1,2],linewidth=linewidth, alpha=0.5,color='lightgray')
sns.lineplot(x=date_range, y=uniform_filter1d(eof_pc4_up, size=10, mode='nearest'), ax=axes[1,2],linewidth=linewidth, alpha=0.8,color='black')
axes[1,2].axhline(0, color='red', linestyle='--', alpha=0.5)
axes[1,2].set_title(r'ATC$_w$ LFC-4',fontsize=16)
axes[1,2].text(0, 1.04, "f", transform=axes[1,2].transAxes, fontsize=axes[1,2].title.get_fontsize()+2, verticalalignment='bottom', horizontalalignment='left', fontweight='bold',)
axes[1,2].set_xlabel('')
#axes[2, 1].set_xlim(1970, 2020)
axes[1,2].set_ylim(-2.8, 2.8)
axes[1,2].xaxis.set_major_locator(mdates.YearLocator(10))  # 每10年一个主刻度
axes[1,2].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # 只显示年份
axes[1,2].set_xlim([pd.Timestamp('1970-01-01'), pd.Timestamp('2020-12-31')])


#===================================map ATCc=====================================================#
im_eof2_down = axes[2,0].pcolormesh(lon, lat, eof2_down, transform=ccrs.PlateCarree(), cmap=cmap,vmin=vmin_spatial, vmax=vmax_spatial)
axes[2,0].add_feature(cfeature.COASTLINE)
axes[2,0].set_title(r'ATC$_c$ LFP-2',fontsize=16)
axes[2,0].text(0, 1.04, "g", transform=axes[2,0].transAxes, fontsize=axes[2,0].title.get_fontsize()+2, verticalalignment='bottom', horizontalalignment='left', fontweight='bold',)
axes[2,0].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree(central_longitude=0))
axes[2,0].set_xticks([-180, -90, 0, 90, 180], crs=ccrs.PlateCarree())
axes[2,0].set_yticks([-60,-30, 0, 30, 60,90], crs=ccrs.PlateCarree())
axes[2,0].set_xticklabels(['180°W', '90°W', '0°', '90°E', '180°E'])
axes[2,0].set_yticklabels(['60°S', '30°S', '0°', '30°N', '60°N', '90°N'])

im_eof3_down = axes[2,1].pcolormesh(lon, lat, eof3_down, transform=ccrs.PlateCarree(), cmap=cmap,vmin=vmin_spatial, vmax=vmax_spatial)
axes[2,1].add_feature(cfeature.COASTLINE)
axes[2,1].set_title(r'ATC$_c$ LFP-3',fontsize=16)
axes[2,1].text(0, 1.04, "h", transform=axes[2,1].transAxes, fontsize=axes[2,1].title.get_fontsize()+2, verticalalignment='bottom', horizontalalignment='left', fontweight='bold',)
axes[2,1].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree(central_longitude=0))
axes[2,1].set_xticks([-180, -90, 0, 90, 180], crs=ccrs.PlateCarree())
axes[2,1].set_yticks([-60,-30, 0, 30, 60,90], crs=ccrs.PlateCarree())
axes[2,1].set_xticklabels(['180°W', '90°W', '0°', '90°E', '180°E'])
axes[2,1].set_yticklabels(['60°S', '30°S', '0°', '30°N', '60°N', '90°N'])

im_eof4_down = axes[2,2].pcolormesh(lon, lat, eof4_down, transform=ccrs.PlateCarree(), cmap=cmap,vmin=vmin_spatial, vmax=vmax_spatial)
axes[2,2].add_feature(cfeature.COASTLINE)
axes[2,2].set_title(r'ATC$_c$ LFP-4',fontsize=16)
axes[2,2].text(0, 1.04, "i", transform=axes[2,2].transAxes, fontsize=axes[2,2].title.get_fontsize()+2, verticalalignment='bottom', horizontalalignment='left', fontweight='bold',)
axes[2,2].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree(central_longitude=0))
axes[2,2].set_xticks([-180, -90, 0, 90, 180], crs=ccrs.PlateCarree())
axes[2,2].set_yticks([-60,-30, 0, 30, 60,90], crs=ccrs.PlateCarree())
axes[2,2].set_xticklabels(['180°W', '90°W', '0°', '90°E', '180°E'])
axes[2,2].set_yticklabels(['60°S', '30°S', '0°', '30°N', '60°N', '90°N'])


#===================================line ATCc=====================================================#
sns.lineplot(x=date_range, y=eof_pc2_down, ax=axes[3,0],linewidth=linewidth, alpha=0.5,color='lightgray')
sns.lineplot(x=date_range, y=uniform_filter1d(eof_pc2_down, size=10, mode='nearest'), ax=axes[3,0],linewidth=linewidth, alpha=0.8,color='black')
axes[3,0].axhline(0, color='red', linestyle='--', alpha=0.5)
axes[3,0].set_title(r'ATC$_c$ LFC-2',fontsize=16)
axes[3,0].text(0, 1.04, "j", transform=axes[3,0].transAxes, fontsize=axes[3,0].title.get_fontsize()+2, verticalalignment='bottom', horizontalalignment='left', fontweight='bold',)
axes[3,0].set_xlabel('')
#axes[0,1].set_xlim(1970, 2020)
axes[3,0].set_ylim(-2.8, 2.8)
axes[3,0].xaxis.set_major_locator(mdates.YearLocator(10))  # 每10年一个主刻度
axes[3,0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # 只显示年份
axes[3,0].set_xlim([pd.Timestamp('1970-01-01'), pd.Timestamp('2020-12-31')])


sns.lineplot(x=date_range, y=eof_pc3_down, ax=axes[3,1],linewidth=linewidth, alpha=0.5,color='lightgray')
sns.lineplot(x=date_range, y=uniform_filter1d(eof_pc3_down, size=10, mode='nearest'), ax=axes[3,1],linewidth=linewidth, alpha=0.8,color='black')
axes[3,1].axhline(0, color='red', linestyle='--', alpha=0.5)
axes[3,1].set_title(r'ATC$_c$ LFC-3',fontsize=16)
axes[3,1].text(0, 1.04, "k", transform=axes[3,1].transAxes, fontsize=axes[3,1].title.get_fontsize()+2, verticalalignment='bottom', horizontalalignment='left', fontweight='bold',)
axes[3,1].set_xlabel('')
#axes[1, 1].set_xlim(1970, 2020)
axes[3,1].set_ylim(-2.8, 2.8)
axes[3,1].xaxis.set_major_locator(mdates.YearLocator(10))  # 每10年一个主刻度
axes[3,1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # 只显示年份
axes[3,1].set_xlim([pd.Timestamp('1970-01-01'), pd.Timestamp('2020-12-31')])

sns.lineplot(x=date_range, y=eof_pc4_down, ax=axes[3,2],linewidth=linewidth, alpha=0.5,color='lightgray')
sns.lineplot(x=date_range, y=uniform_filter1d(eof_pc4_down, size=10, mode='nearest'), ax=axes[3,2],linewidth=linewidth, alpha=0.8,color='black')
axes[3,2].axhline(0, color='red', linestyle='--', alpha=0.5)
axes[3,2].set_title(r'ATC$_c$ LFC-4',fontsize=16)
axes[3,2].text(0, 1.04, "l", transform=axes[3,2].transAxes, fontsize=axes[3,2].title.get_fontsize()+2, verticalalignment='bottom', horizontalalignment='left', fontweight='bold',)
axes[3,2].set_xlabel('')
#axes[2, 1].set_xlim(1970, 2020)
axes[3,2].set_ylim(-2.8, 2.8)
axes[3,2].xaxis.set_major_locator(mdates.YearLocator(10))  # 每10年一个主刻度
axes[3,2].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # 只显示年份
axes[3,2].set_xlim([pd.Timestamp('1970-01-01'), pd.Timestamp('2020-12-31')])

cax_1 = fig.add_axes([0.94, 0.77, 0.01, 0.18])  # [left, bottom, width, height]
cbar_1=fig.colorbar(im_eof2_up, cax=cax_1, orientation='vertical', extend='both')
cbar_1.set_ticks([vmin_spatial,vmin_spatial/2,0,vmax_spatial/2,vmax_spatial])  # 设置刻度位置
cbar_1.set_ticklabels([vmin_spatial,vmin_spatial/2,0,vmax_spatial/2,vmax_spatial])  # 设置刻度标签

plt.subplots_adjust(left=0.04,right=0.91,top=0.96,bottom=0.04, hspace=0.36, wspace=0.18)#hspace垂直间距，wspace水平间距

script_name = os.path.splitext(os.path.basename(__file__))[0]
plt.savefig(str(current_directory)+f"/{script_name}.png", dpi=300)

plt.close()







