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


#==========================================load CMIP6 data===========================================#

fig, axes = plt.subplots(nrows=7, ncols=3, figsize=(7, 8.6), subplot_kw={'projection': ccrs.PlateCarree()})#figsize=(width, height)
axes = axes.flatten()

axes[20].remove()


models=['ACCESS-ESM1-5','AWI-CM-1-1-MR','BCC-CSM2-MR','CanESM5','CESM2-WACCM','CMCC-ESM2','E3SM-1-0','EC-Earth3','FGOALS-g3','GFDL-ESM4',
        'IITM-ESM','INM-CM5-0','IPSL-CM6A','KACE-1-0-G','KIOST-ESM','MIROC6','MPI-ESM1-2-HR','NESM3','NorESM2','TaiESM1',]
labels = [f'{letter}' for letter in string.ascii_lowercase[:23]]


vmin_time=-0.10
vmax_time=0.04
cmap=mcolors.ListedColormap(sns.color_palette("RdBu_r", as_cmap=True)(np.linspace(0.2, 0.8, 256)))
norm = TwoSlopeNorm(vmin=vmin_time, vcenter=0, vmax=vmax_time)


for i, model in enumerate(models):
    print(model)
    dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/T_change_freq_"+str(model)+"_yearly_1970-2015_mk-rescale.nc")
    if 'latitude' in dataset.variables:
        lat = dataset['latitude'][:]
        lon = dataset['longitude'][:]
    elif 'lat' in dataset.variables:
        lat = dataset['lat'][:]
        lon = dataset['lon'][:]
        
    ATC_trend_CMIP6 = dataset['ATC_trend_slope'][:]*365
    ATC_pvalue_CMIP6 = dataset['ATC_trend_p_value'][:]
    
    count_trend = (~np.isnan(ATC_trend_CMIP6)).sum()
    count_pvalue = (ATC_pvalue_CMIP6 < 0.05).sum()
    print(count_trend)
    print(count_pvalue)
    print(count_pvalue/count_trend)
    
    #================plot=======================
    interval = 4
    lon2d, lat2d = np.meshgrid(lon, lat)
    mask = (ATC_pvalue_CMIP6 <= 0.05)
    sample = np.zeros_like(mask)
    sample[::interval, ::interval] = mask[::interval, ::interval]
    
    im_CMIP6_trend = axes[i].pcolormesh(lon, lat, ATC_trend_CMIP6, transform=ccrs.PlateCarree(), cmap=cmap,norm=norm)
    axes[i].scatter(lon2d[sample], lat2d[sample], s=0.2,color='black',transform=ccrs.PlateCarree(),linewidths=0,alpha=1)
    axes[i].add_feature(cfeature.COASTLINE,linewidth=0.2,edgecolor='black',alpha=0.6)
    axes[i].set_frame_on(False)
    axes[i].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
    axes[i].set_title(str(model))
    axes[i].text(0, 1.08, f"{labels[i]}", transform=axes[i].transAxes, fontsize=axes[i].title.get_fontsize()+2, fontweight='bold',verticalalignment='bottom', horizontalalignment='left')   
    
#======legend=======#
cbar_time_ax = fig.add_axes([0.68, 0.1, 0.3, 0.010])  # [left, bottom, width, height]
cbar_time=fig.colorbar(im_CMIP6_trend, cax=cbar_time_ax, orientation='horizontal', extend='both')
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
cbar_time.set_label('ATC trend (yr⁻²)', fontsize=10, labelpad=-36) 

plt.subplots_adjust(left=0.03, right=0.98, bottom=0.01, top=0.98, wspace=0.06, hspace=0.02)

fig1 = plt.gcf()
script_name = os.path.splitext(os.path.basename(__file__))[0]
fig1.savefig(str(current_directory)+f"/{script_name}.png", dpi=300)
#plt.show()


