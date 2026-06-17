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
from matplotlib.colors import TwoSlopeNorm


current_directory = os.path.dirname(os.path.abspath(__file__))

#==========================================load data===========================================#


fig, axes = plt.subplots(nrows=8, ncols=3, figsize=(7, 10), subplot_kw={'projection': ccrs.PlateCarree()})#figsize=(width, height)
axes = axes.flatten()

axes[22].remove()
axes[22] = fig.add_subplot(8, 3, 23)


models=['CRUJRA','ERA5','ACCESS-ESM1-5','AWI-CM-1-1-MR','BCC-CSM2-MR','CanESM5','CESM2-WACCM','CMCC-ESM2','E3SM-1-0','EC-Earth3','FGOALS-g3','GFDL-ESM4',
        'IITM-ESM','INM-CM5-0','IPSL-CM6A','KACE-1-0-G','KIOST-ESM','MIROC6','MPI-ESM1-2-HR','NESM3','NorESM2','TaiESM1',]
labels = [f'{letter}' for letter in string.ascii_lowercase[:23]]

vmin, vmax, zero = -0.08,0.02, 0

norm = TwoSlopeNorm(vmin=vmin, vcenter=zero, vmax=vmax)
base_cmap = plt.get_cmap('coolwarm')

        
for i, model in enumerate(models):
    print(model)
    print(i)
    if model=='CRUJRA':
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/LFCA/LFCA_result_monthly_1970_2020.nc")
        time = 1970
        light='lightblue'
        black='blue'
        zorder=10
    elif model=='ERA5':
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/LFCA/LFCA_result_ERA5_1970_2020_monthly.nc")
        time=1970
        light='peachpuff'
        black='orange'
        zorder=10
    else:
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_ssp585/"+str(model)+"/LFCA/LFCA_result_"+str(model)+"_1970_2100_monthly.nc")
        time=1970
        light='lightgray'
        black='black'
        zorder=1
    lfps_down = dataset['lfps_down'][0,:]*364
    lfcs_down = dataset['lfcs_down'][0,:]
    lfps_down = lfps_down*(np.nanmean(lfcs_down[-120:])-np.nanmean(lfcs_down[:120]))  / ((len(lfcs_down)-120) /12)
    print(len(lfcs_down))
    time = [time + (t / 12.0) for t in range(len(lfcs_down))]
    
    #im_lfps_up_CRUJRA = axes[i].pcolormesh(dataset["lon"][:], dataset["lat"][:], lfps_down, transform=ccrs.PlateCarree(), cmap='coolwarm',vmin=vmin,vmax=vmax,)
    im_lfps_up_CRUJRA = axes[i].pcolormesh(dataset["lon"][:], dataset["lat"][:], lfps_down, transform=ccrs.PlateCarree(), cmap=base_cmap,norm=norm)
    axes[i].add_feature(cfeature.COASTLINE,linewidth=0.3,edgecolor='black')
    title_text = axes[i].set_title(str(model))
    axes[i].text(0, 1.08, f"{labels[i]}", transform=axes[i].transAxes, fontsize=axes[i].title.get_fontsize()+2, fontweight='bold',verticalalignment='bottom', horizontalalignment='left')
    axes[i].set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
    axes[i].set_frame_on(False)
    

    sns.lineplot(x=time, y=lfcs_down,  ax=axes[22], color=light, alpha=0.4, lw=0.5,zorder=zorder)
    smoothed_values = uniform_filter1d(lfcs_down, size=10, mode='nearest')
    sns.lineplot(x=time, y=smoothed_values, ax=axes[22],color=black, alpha=0.8, lw=1,zorder=zorder)


[(spine.set_linewidth(0.3),spine.set_color('black')) for ax in axes for spine in ax.spines.values()]
    
axes[22].yaxis.set_label_position("right")
axes[22].yaxis.tick_right()
axes[22].axhline(0, color='red', ls='--', lw=1, alpha=0.6)
axes[22].set_title("LFC-1")
axes[22].text(0, 1.08, f"{labels[22]}", transform=axes[22].transAxes, fontsize=axes[22].title.get_fontsize()+2, fontweight='bold',verticalalignment='bottom', horizontalalignment='left')
axes[22].set_xlim(1970, 2100)
axes[22].set_xticks([1970, 2010, 2050, 2100])
axes[22].set_ylim(-3, 3)

axes[23].remove()

#print(pos.width,pos.height)

cbar_ax = fig.add_axes([0.70, 0.08, 0.22, 0.01])  # [left, bottom, width, height]
cbar=fig.colorbar(im_lfps_up_CRUJRA, cax=cbar_ax, orientation='horizontal', extend='both')
#cbar.set_label(r'change in ATCc occurrence (yr⁻¹)', labelpad=-40,  horizontalalignment='left')
cbar.ax.set_xlabel(r'change in ATCc occurrence (yr⁻²)', labelpad=-40, ha='left', x=-0.20)
cbar.set_ticks([vmin, 0, vmax])
cbar.set_ticklabels([f'{vmin:.2f}', '0', f'{vmax:.2f}'])
cbar.ax.xaxis.set_minor_locator(plt.NullLocator())

plt.subplots_adjust(left=0.03, right=0.94, bottom=0.02, top=0.98, wspace=0.06, hspace=0.02)
pos1 = axes[1].get_position()
pos2 = axes[2].get_position()
pos21 = axes[21].get_position()
axes[22].set_position([pos1.x0, pos21.y0, pos1.width, pos1.height])


fig.savefig(str(current_directory)+"/Figure4_plot_LFCA_3x8_ATCc.png", dpi=300)
#plt.show()
    
    










