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
from scipy import stats
from matplotlib.colors import TwoSlopeNorm

current_directory = os.path.dirname(os.path.abspath(__file__))
dataset_ref = nc.Dataset("/data1/zxy/sudden_temp_change/spatial_pattern_correlations/spatial_pattern_correlations_monthly_seamask.nc")
seamask=dataset_ref['topo'][:]

dataset = nc.Dataset("/data1/zxy/sudden_temp_change/spatial_pattern_correlations/spatial_pattern_correlations_monthly.nc")

CRUJRA_C_up_set=dataset['CRUJRA_C_up_set'][:]
CRUJRA_C_down_set=dataset['CRUJRA_C_down_set'][:]
CRUJRA_R_up_set=dataset['CRUJRA_R_up_set'][:]
CRUJRA_R_down_set=dataset['CRUJRA_R_down_set'][:]

ERA5_C_up_set=dataset['ERA5_C_up_set'][:]
ERA5_C_down_set=dataset['ERA5_C_down_set'][:]
ERA5_R_up_set=dataset['ERA5_R_up_set'][:]
ERA5_R_down_set=dataset['ERA5_R_down_set'][:]

CMIP6_C_up_set=dataset['CMIP6_C_up_set'][:]
CMIP6_C_down_set=dataset['CMIP6_C_down_set'][:]
CMIP6_R_up_set=dataset['CMIP6_R_up_set'][:]
CMIP6_R_down_set=dataset['CMIP6_R_down_set'][:]

lfps_up_CRUJRA  =dataset['lfps_up_CRUJRA'][:]*364
lfps_down_CRUJRA=dataset['lfps_down_CRUJRA'][:]*364
lfps_up_ERA5  =dataset['lfps_up_ERA5'][:]*364
lfps_down_ERA5=dataset['lfps_down_ERA5'][:]*364
lfps_up_cmip6   =dataset['lfps_up_cmip6'][:]*364
lfps_down_cmip6 =dataset['lfps_down_cmip6'][:]*364

lfps_up_CRUJRA[seamask.mask]=np.nan
lfps_down_CRUJRA[seamask.mask]=np.nan
lfps_up_ERA5[seamask.mask]=np.nan
lfps_down_ERA5[seamask.mask]=np.nan
lfps_up_cmip6[seamask.mask]=np.nan
lfps_down_cmip6[seamask.mask]=np.nan

C_up_CRUJRA = dataset.getncattr('C_up_CRUJRA')
C_down_CRUJRA  = dataset.getncattr('C_down_CRUJRA')
R_up_CRUJRA  = dataset.getncattr('R_up_CRUJRA')
R_down_CRUJRA  = dataset.getncattr('R_down_CRUJRA')

C_up_ERA5 = dataset.getncattr('C_up_ERA5')
C_down_ERA5  = dataset.getncattr('C_down_ERA5')
R_up_ERA5  = dataset.getncattr('R_up_ERA5')
R_down_ERA5  = dataset.getncattr('R_down_ERA5')

CRUJRA_C_up_set_p = stats.percentileofscore(CRUJRA_C_up_set, C_up_CRUJRA)
CRUJRA_C_down_set_p = stats.percentileofscore(CRUJRA_C_down_set, C_down_CRUJRA)
CRUJRA_R_up_set_p = stats.percentileofscore(CRUJRA_R_up_set, R_up_CRUJRA)
CRUJRA_R_down_set_p = stats.percentileofscore(CRUJRA_R_down_set, R_down_CRUJRA)

ERA5_C_up_set_p = stats.percentileofscore(ERA5_C_up_set, C_up_ERA5)
ERA5_C_down_set_p = stats.percentileofscore(ERA5_C_down_set, C_down_ERA5)
ERA5_R_up_set_p = stats.percentileofscore(ERA5_R_up_set, R_up_ERA5)
ERA5_R_down_set_p = stats.percentileofscore(ERA5_R_down_set, R_down_ERA5)

CMIP6_C_up_set_p = stats.percentileofscore(CMIP6_C_up_set, C_up_CRUJRA)
CMIP6_C_down_set_p = stats.percentileofscore(CMIP6_C_down_set, C_down_CRUJRA)
CMIP6_R_up_set_p = stats.percentileofscore(CMIP6_R_up_set, R_up_CRUJRA)
CMIP6_R_down_set_p = stats.percentileofscore(CMIP6_R_down_set, R_down_CRUJRA)


print("CRUJRA_C_up_set_p",CRUJRA_C_up_set_p)
print("CRUJRA_C_down_set_p",CRUJRA_C_down_set_p)
print("CRUJRA_R_up_set_p",CRUJRA_R_up_set_p)
print("CRUJRA_R_down_set_p",CRUJRA_R_down_set_p)

print("ERA5_C_up_set_p",ERA5_C_up_set_p)
print("ERA5_C_down_set_p",ERA5_C_down_set_p)
print("ERA5_R_up_set_p",ERA5_R_up_set_p)
print("ERA5_R_down_set_p",ERA5_R_down_set_p)

print("CMIP6_C_up_set_p",CMIP6_C_up_set_p)
print("CMIP6_C_down_set_p",CMIP6_C_down_set_p)
print("CMIP6_R_up_set_p",CMIP6_R_up_set_p)
print("CMIP6_R_down_set_p",CMIP6_R_down_set_p)



#===========================================plot data====================================#

fig = plt.figure(figsize=(12, 7))#figsize=(width, height)
gs = gridspec.GridSpec(3, 4, width_ratios=[1, 1, 0.15, 0.15], height_ratios=[1, 1, 1],figure=fig)
ax1 = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
ax2 = fig.add_subplot(gs[0, 1], projection=ccrs.PlateCarree())
ax3 = fig.add_subplot(gs[1, 0], projection=ccrs.PlateCarree())
ax4 = fig.add_subplot(gs[1, 1], projection=ccrs.PlateCarree())
ax5 = fig.add_subplot(gs[2, 0], projection=ccrs.PlateCarree())
ax6 = fig.add_subplot(gs[2, 1], projection=ccrs.PlateCarree())
ax7 = fig.add_subplot(gs[0, 2])  # 散点图1
ax8 = fig.add_subplot(gs[0, 3])  # 散点图2
ax9 = fig.add_subplot(gs[1, 2])  # 散点图1
ax10 = fig.add_subplot(gs[1, 3])  # 散点图2
axes = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9, ax10]

plt.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'axes.titlepad': 12,
})


vmin, vmax, zero = -0.08,0.02, 0

norm = TwoSlopeNorm(vmin=vmin, vcenter=zero, vmax=vmax)
base_cmap = plt.get_cmap('coolwarm')

#===========================================spatial distribution plot====================================#
#CRUJRA
im_lfps_up_CRUJRA = ax1.pcolormesh(dataset["lon"][:], dataset["lat"][:], lfps_up_CRUJRA, transform=ccrs.PlateCarree(), cmap=base_cmap,norm=norm)
ax1.add_feature(cfeature.COASTLINE,linewidth=0.3,edgecolor='black')
ax1.set_title(r'CRUJRA 1970-2020 ATCw LFCA',y=0.95)
ax1.text(0, 1.02, "a", transform=ax1.transAxes, fontsize=ax1.title.get_fontsize()+2, fontweight='bold', verticalalignment='bottom', horizontalalignment='left')
ax1.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())

im_lfps_down_CRUJRA = ax2.pcolormesh(dataset["lon"][:], dataset["lat"][:], lfps_down_CRUJRA, transform=ccrs.PlateCarree(), cmap=base_cmap,norm=norm)
ax2.add_feature(cfeature.COASTLINE,linewidth=0.3,edgecolor='black')
ax2.set_title(r'CRUJRA 1970-2020 ATCc LFCA',y=0.95)
ax2.text(0, 1.02, "b", transform=ax2.transAxes, fontsize=ax3.title.get_fontsize()+2, fontweight='bold', verticalalignment='bottom', horizontalalignment='left')
ax2.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())

#ERA5
im_lfps_up_ERA5 = ax3.pcolormesh(dataset["lon"][:], dataset["lat"][:], lfps_up_ERA5, transform=ccrs.PlateCarree(), cmap=base_cmap,norm=norm)
ax3.add_feature(cfeature.COASTLINE,linewidth=0.3,edgecolor='black')
ax3.set_title(r'ERA5 1970-2020 ATCw LFCA',y=0.95)
ax3.text(0, 1.05, "e", transform=ax3.transAxes, fontsize=ax1.title.get_fontsize()+2, fontweight='bold', verticalalignment='bottom', horizontalalignment='left')
ax3.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())

im_lfps_down_ERA5 = ax4.pcolormesh(dataset["lon"][:], dataset["lat"][:], lfps_down_ERA5, transform=ccrs.PlateCarree(), cmap=base_cmap,norm=norm)
ax4.add_feature(cfeature.COASTLINE,linewidth=0.3,edgecolor='black')
ax4.set_title(r'ERA5 1970-2020 ATCc LFCA',y=0.95)
ax4.text(0, 1.05, "f", transform=ax4.transAxes, fontsize=ax3.title.get_fontsize()+2, fontweight='bold', verticalalignment='bottom', horizontalalignment='left')
ax4.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())

#CMIP6
im_lfps_up_cmip6 = ax5.pcolormesh(dataset["lon"][:], dataset["lat"][:], lfps_up_cmip6, transform=ccrs.PlateCarree(), cmap=base_cmap,norm=norm)
ax5.add_feature(cfeature.COASTLINE,linewidth=0.3,edgecolor='black')
ax5.set_title(r'CMIP6 1970-2100 ATCw LFCA',y=0.95)
ax5.text(0, 1.05, "i", transform=ax5.transAxes, fontsize=ax2.title.get_fontsize()+2, fontweight='bold', verticalalignment='bottom', horizontalalignment='left')
ax5.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())


im_lfps_down_cmip6 = ax6.pcolormesh(dataset["lon"][:], dataset["lat"][:], lfps_down_cmip6, transform=ccrs.PlateCarree(), cmap=base_cmap,norm=norm)
ax6.add_feature(cfeature.COASTLINE,linewidth=0.3,edgecolor='black')
ax6.set_title(r'CMIP6 1970-2100 ATCc LFCA',y=0.95)
ax6.text(0, 1.05, "j", transform=ax6.transAxes, fontsize=ax4.title.get_fontsize()+2, fontweight='bold', verticalalignment='bottom', horizontalalignment='left')
ax6.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())

ax1.set_aspect(1.05)
ax2.set_aspect(1.05)
ax3.set_aspect(1.05)
ax4.set_aspect(1.05)
ax5.set_aspect(1.05)
ax6.set_aspect(1.05)

ax1.set_frame_on(False)
ax2.set_frame_on(False)
ax3.set_frame_on(False)
ax4.set_frame_on(False)
ax5.set_frame_on(False)
ax6.set_frame_on(False)


#===========================================scatter plot====================================#
x_pos1 = np.zeros(len(CRUJRA_C_up_set))
x_pos2 = np.zeros(len(CRUJRA_C_up_set))+1
sns.scatterplot(ax=ax7, x=x_pos1, y=CRUJRA_C_up_set, alpha=0.1, s=70, color='skyblue', marker='o',edgecolor='none',)
sns.scatterplot(ax=ax7, x=x_pos2, y=CRUJRA_R_up_set, alpha=0.1, s=70, color='skyblue', marker='o',edgecolor='none',)
sns.scatterplot(ax=ax7, x=[0], y=[C_up_CRUJRA], alpha=0.8, s=70, color='red', marker='o',edgecolor='none',)
sns.scatterplot(ax=ax7, x=[1], y=[R_up_CRUJRA], alpha=0.8, s=70, color='red', marker='o',edgecolor='none',)
ax7.set_title(r'ATCw',y=0.95)
ax7.text(-0.4, 0.9, "c", transform=ax7.transAxes, fontsize=ax5.title.get_fontsize()+2, fontweight='bold', verticalalignment='bottom', horizontalalignment='left')
ax7.set_xlim(-1, 2)
ax7.set_xticks([0, 1])
ax7.set_xticklabels(['C', 'R'])
ax7.set_ylim(-1, 1)
ax7.set_ylim(-0.9, 0.9)
ax7.set_yticks([-0.8,-0.4,0,0.4,0.8])
ax7.tick_params(axis='y', which='both', left=False, right=True, labelleft=False, labelright=True)

sns.scatterplot(ax=ax8, x=x_pos1, y=CRUJRA_C_down_set, alpha=0.1, s=70, color='skyblue', marker='o',edgecolor='none',)
sns.scatterplot(ax=ax8, x=x_pos2, y=CRUJRA_R_down_set, alpha=0.1, s=70, color='skyblue', marker='o',edgecolor='none',)
sns.scatterplot(ax=ax8, x=[0], y=[C_down_CRUJRA], alpha=0.8, s=70, color='red', marker='o',edgecolor='none',)
sns.scatterplot(ax=ax8, x=[1], y=[R_down_CRUJRA], alpha=0.8, s=70, color='red', marker='o',edgecolor='none',)
ax8.set_title(r'ATCc',y=0.95)
ax8.text(-0.4, 0.9, "d", transform=ax8.transAxes, fontsize=ax6.title.get_fontsize()+2, fontweight='bold', verticalalignment='bottom', horizontalalignment='left')
ax8.set_xlim(-1, 2)
ax8.set_xticks([0, 1])  
ax8.set_xticklabels(['C', 'R'])
#ax6.yaxis.tick_right()  
#ax6.yaxis.set_label_position("right")
ax8.set_ylim(-0.9, 0.9)
ax8.set_yticks([-0.8,-0.4,0,0.4,0.8])
ax8.tick_params(axis='y', which='both', left=False, right=True, labelleft=False, labelright=True)

sns.scatterplot(ax=ax9, x=x_pos1, y=ERA5_C_up_set, alpha=0.1, s=70, color='skyblue', marker='o',edgecolor='none',)
sns.scatterplot(ax=ax9, x=x_pos2, y=ERA5_R_up_set, alpha=0.1, s=70, color='skyblue', marker='o',edgecolor='none',)
sns.scatterplot(ax=ax9, x=[0], y=[C_up_ERA5], alpha=0.8, s=70, color='orange', marker='o',edgecolor='none',)
sns.scatterplot(ax=ax9, x=[1], y=[R_up_ERA5], alpha=0.8, s=70, color='orange', marker='o',edgecolor='none',)
#ax9.set_title(r'ATCw')
ax9.text(-0.4, 0.9, "g", transform=ax9.transAxes, fontsize=ax5.title.get_fontsize()+2, fontweight='bold', verticalalignment='bottom', horizontalalignment='left')
ax9.set_xlim(-1, 2)
ax9.set_xticks([0, 1])
ax9.set_xticklabels(['C', 'R'])
#ax9.set_ylim(-1, 1)
ax9.set_ylim(-2, 2)
ax9.set_yticks([-1.6,-0.8,0,0.8,1.6])
ax9.tick_params(axis='y', which='both', left=False, right=True, labelleft=False, labelright=True)

sns.scatterplot(ax=ax10, x=x_pos1, y=ERA5_C_down_set, alpha=0.1, s=70, color='skyblue', marker='o',edgecolor='none',)
sns.scatterplot(ax=ax10, x=x_pos2, y=ERA5_R_down_set, alpha=0.1, s=70, color='skyblue', marker='o',edgecolor='none',)
sns.scatterplot(ax=ax10, x=[0], y=[C_down_ERA5], alpha=0.8, s=70, color='orange', marker='o',edgecolor='none',)
sns.scatterplot(ax=ax10, x=[1], y=[R_down_ERA5], alpha=0.8, s=70, color='orange', marker='o',edgecolor='none',)
#ax10.set_title(r'ATCc')
ax10.text(-0.4, 0.9, "h", transform=ax10.transAxes, fontsize=ax6.title.get_fontsize()+2, fontweight='bold', verticalalignment='bottom', horizontalalignment='left')
ax10.set_xlim(-1, 2)
ax10.set_xticks([0, 1])  
ax10.set_xticklabels(['C', 'R'])
#ax6.yaxis.tick_right()  
#ax6.yaxis.set_label_position("right")
ax10.set_ylim(-2, 2)
ax10.set_yticks([-1.6,-0.8,0,0.8,1.6])
ax10.tick_params(axis='y', which='both', left=False, right=True, labelleft=False, labelright=True)

[(spine.set_linewidth(0.3),spine.set_color('black')) for ax in axes for spine in ax.spines.values()]

plt.subplots_adjust(left=0.01, right=0.86, bottom=0.02, top=0.95, wspace=0.04, hspace=0.10)

pos1 = ax1.get_position()
pos3 = ax3.get_position()

pos7 = ax7.get_position()
ax7.set_position([pos7.x0 + 0.03, pos1.y0, pos7.width, pos1.height])  # 向右移动

pos8 = ax8.get_position()
ax8.set_position([pos8.x0 + 0.09, pos1.y0, pos8.width, pos1.height])  # 向右移动

pos9 = ax9.get_position()
ax9.set_position([pos9.x0 + 0.03, pos3.y0, pos9.width, pos1.height])  # 向右移动

pos10 = ax10.get_position()
ax10.set_position([pos10.x0 + 0.09, pos3.y0, pos10.width, pos1.height])  # 向右移动

#==============================add legend========================================#

cbar_ax = fig.add_axes([0.76, 0.10, 0.2, 0.02])  # [left, bottom, width, height]
cbar = fig.colorbar(im_lfps_up_CRUJRA, cax=cbar_ax, orientation='horizontal',extend='both')
cbar.set_label(r'change in ATC occurrence (yr⁻²)', labelpad=-42)

cbar.set_ticks([vmin, vmin/2, 0, vmax/2, vmax])
cbar.set_ticklabels([f'{vmin:.2f}', f'{vmin/2:.2f}','0',f'{vmax/2:.2f}', f'{vmax:.2f}'])

legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8,                label='CRUJRA vs Forced CMIP6'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=8,             label='ERA5     vs Forced CMIP6'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='skyblue', markersize=8, alpha=0.5, label='CRUJRA/ERA5 vs Unforced CMIP6')
    ]
 

legend = fig.legend(handles=legend_elements,  loc='lower left',  bbox_to_anchor=(0.745, 0.18), frameon=True, bbox_transform=fig.transFigure,fontsize=10)


fig1 = plt.gcf()
fig.savefig(str(current_directory)+"/Figure5_plot_pattern-correlation_monthly_new_occurrence.png", dpi=300)
#plt.show()
