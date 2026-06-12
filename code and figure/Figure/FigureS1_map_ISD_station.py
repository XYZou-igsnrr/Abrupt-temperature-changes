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
from matplotlib.ticker import FuncFormatter
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter


current_directory = os.path.dirname(os.path.abspath(__file__))

#=========================================load xlsx data===================================================#
xlsx_file = "/data1/zxy/sudden_temp_change/station-count.xlsx"  
variable_col = "length"   
lat_col = "LAT"
lon_col = "LON"
year_col = "year"
count_col = "station_count"
xls = pd.ExcelFile(xlsx_file)
df_map = pd.read_excel(xlsx_file, sheet_name="station_length", engine="openpyxl")
df_bar = pd.read_excel(xlsx_file, sheet_name="global-daily", engine="openpyxl")
df_bar = df_bar.sort_values(by=year_col)
lons = df_map[lon_col].values
lats = df_map[lat_col].values
vals = df_map[variable_col].values

sort_idx = np.argsort(vals)
lons = lons[sort_idx]
lats = lats[sort_idx]
vals = vals[sort_idx]

years = df_bar[year_col].values
counts = df_bar[count_col].values


#=======================plot====================================#
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['axes.labelsize']  = 10
plt.rcParams['axes.titlesize']  = 10

fig = plt.figure(figsize=(7, 4.9)) # figsize=(width, heigh)
ax = fig.add_subplot(projection=ccrs.PlateCarree())


cmap = ListedColormap([
    "#5A8CFF", "#00B4F0", "#00D68F", "#F0E600",
    "#FFB300", "#FF7043", "#B0001B"
])
xls_vmin = 0
xls_vmax = 70
xls_bounds = np.linspace(xls_vmin, xls_vmax, 8)
xls_norm = BoundaryNorm(xls_bounds, cmap.N)


#===================================================================map ISD station==========================================================#
print('map ISD length')
im_station_length = ax.scatter(lons, lats, c=vals, transform=ccrs.PlateCarree(), cmap=cmap,vmin=xls_vmin, vmax=xls_vmax, s=5,alpha=0.7,edgecolors='none')
ax.add_feature(cfeature.COASTLINE)
#ax.set_title(r'ISD site record lengths', fontsize=17)
ax.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
ax.text(0.02, 0.91, "a", ha="left", va="bottom", transform=ax.transAxes, fontsize=14, fontweight='bold',)

ax.set_xticks([-180, -120, -60, 0, 60, 120, 180], crs=ccrs.PlateCarree())
ax.set_yticks([-60, -30, 0, 30, 60, 90], crs=ccrs.PlateCarree())
ax.set_xticklabels(['180W°', '120°W', '60°W', '0°', '60°E', '120°E', '180E°'])
ax.set_yticklabels(['60°S', '30°S', '0°', '30°N', '60°N', '90°N'])
ax.tick_params(axis='both', which='major', length=5, width=0.5, colors='black')

#===================================================================bar plot==========================================================#
print(' plot')

ax_bar = inset_axes(ax, width="100%", height="65%", loc='upper left', bbox_to_anchor=(0, -1.15, 1, 1), bbox_transform=ax.transAxes, borderpad=0)

#ax_bar.plot(years, counts, color='#5A8CFF', linewidth=1.1, marker='o', markersize=0.5, alpha=0.8)
ax_bar.bar(years, counts, color='#9C27B0', width=0.7, alpha=0.5,edgecolor='none')
ax_bar.text(0.02, 0.85, "b", ha="left", va="bottom", transform=ax_bar.transAxes, fontsize=14, fontweight='bold',)
ax_bar.tick_params(axis='both', labelsize=11)
ax_bar.yaxis.tick_left()
ax_bar.yaxis.set_label_position("left")
ax_bar.set_xlim(1930, 2024)
decade_ticks = np.arange(1930, 2021, 10)
ax_bar.set_xticks(decade_ticks)
ax_bar.set_xticklabels([str(int(t)) for t in decade_ticks])
ax_bar.grid(axis='y', linestyle=':', linewidth=0.5, zorder=0)
ax_bar.set_ylabel('count', fontsize=12)
# ax_bar.set_title("Global station counts", fontsize=9)
#===============================================xlsx colorbar============================================================#
xls_cax = inset_axes(ax, width="1.5%", height="100%", loc='lower left',  bbox_to_anchor=(1.001, 0.0, 1, 1),  bbox_transform=ax.transAxes, borderpad=0)

xls_cb = plt.colorbar(im_station_length, cax=xls_cax,  orientation='vertical', boundaries=xls_bounds, spacing='uniform', extend='max')

xls_cb.set_ticks(xls_bounds)
xls_cb.ax.set_yticklabels([f"{int(b)}" for b in xls_bounds])
xls_cb.ax.tick_params(labelsize=12, width=0.6, length=2)
xls_cb.set_label("Record Length (year)", fontsize=12, labelpad=5)




#===============================================save figure============================================================#
plt.subplots_adjust(left=0.13, right=0.91, bottom=0.40 , top=0.99,wspace=0.03, hspace=0.0003)#wspace 水平间距   hspace垂直间距

fig1 = plt.gcf()
script_name = os.path.splitext(os.path.basename(__file__))[0]
fig1.savefig(str(current_directory)+f"/{script_name}.png", dpi=300)