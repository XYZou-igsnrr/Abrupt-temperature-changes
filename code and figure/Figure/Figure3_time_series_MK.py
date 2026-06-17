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
import matplotlib.patches as mpatches
import pymannkendall as mk


current_directory = os.path.dirname(os.path.abspath(__file__))

def Stats(data):
    data = np.asarray(data)
    mean = np.nanmean(data, axis=0) if data.size > 0 else np.nan
    std  = np.nanstd(data, axis=0) if data.size > 0 else np.nan
    min_value  = np.nanmin(data, axis=0) if data.size > 0 else np.nan
    max_value  = np.nanmax(data, axis=0) if data.size > 0 else np.nan

    return mean,std,min_value,max_value


models=['ACCESS-ESM1-5','AWI-CM-1-1-MR','BCC-CSM2-MR','CanESM5','CESM2-WACCM','CMCC-ESM2','E3SM-1-0','EC-Earth3','FGOALS-g3','GFDL-ESM4',
        'IITM-ESM','INM-CM5-0','IPSL-CM6A','KACE-1-0-G','KIOST-ESM','MIROC6','MPI-ESM1-2-HR','NESM3','NorESM2','TaiESM1',]

CMIP6_Global_ATCw   = []
CMIP6_Global_ATCc   = []
CMIP6_NH_ATCw = []
CMIP6_NH_ATCc = []
CMIP6_SH_ATCw = []
CMIP6_SH_ATCc = []

Global_ATCw_slope_CMIP6=[]
Global_ATCc_slope_CMIP6=[]
Northern_ATCw_slope_CMIP6=[]
Northern_ATCc_slope_CMIP6=[]
Southern_ATCw_slope_CMIP6=[]
Southern_ATCc_slope_CMIP6=[]

for i, model in enumerate(models):
    print(model)
    sudden_Tmean_change_csv = pd.read_csv("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/multi-threshold/"+str(model)+"_T_sudden_change_±10°C_1970_2015.csv")
    Global_ATCw = sudden_Tmean_change_csv ['Global_ATCw']*365
    Global_ATCc = sudden_Tmean_change_csv ['Global_ATCc']*365
    NH_ATCw    = sudden_Tmean_change_csv ['Northern_ATCw']*365
    NH_ATCc    = sudden_Tmean_change_csv ['Northern_ATCc']*365
    SH_ATCw    = sudden_Tmean_change_csv ['Southern_ATCw']*365
    SH_ATCc    = sudden_Tmean_change_csv ['Southern_ATCc']*365
    
    CMIP6_Global_ATCw  .append(Global_ATCw)
    CMIP6_Global_ATCc  .append(Global_ATCc)
    CMIP6_NH_ATCw.append(NH_ATCw)
    CMIP6_NH_ATCc.append(NH_ATCc)
    CMIP6_SH_ATCw.append(SH_ATCw)  
    CMIP6_SH_ATCc.append(SH_ATCc)

    years = np.arange(1970, 2015)
    Global_ATCw_slope, Global_ATCw_pValue, = mk.original_test(Global_ATCw).slope, mk.original_test(Global_ATCw).p,
    Global_ATCc_slope, Global_ATCc_pValue, = mk.original_test(Global_ATCc).slope, mk.original_test(Global_ATCc).p,
    Northern_ATCw_slope, Northern_ATCw_pValue, = mk.original_test(NH_ATCw).slope, mk.original_test(NH_ATCw).p,
    Northern_ATCc_slope, Northern_ATCc_pValue, = mk.original_test(NH_ATCc).slope, mk.original_test(NH_ATCc).p,
    Southern_ATCw_slope, Southern_ATCw_pValue, = mk.original_test(SH_ATCw).slope, mk.original_test(SH_ATCw).p,
    Southern_ATCc_slope, Southern_ATCc_pValue, = mk.original_test(SH_ATCc).slope, mk.original_test(SH_ATCc).p,

    Global_ATCw_slope_CMIP6.append(Global_ATCw_slope if Global_ATCw_pValue < 0.05 else np.nan)
    Global_ATCc_slope_CMIP6.append(Global_ATCc_slope if Global_ATCc_pValue < 0.05 else np.nan)
    Northern_ATCw_slope_CMIP6.append(Northern_ATCw_slope if Northern_ATCw_pValue < 0.05 else np.nan)
    Northern_ATCc_slope_CMIP6.append(Northern_ATCc_slope if Northern_ATCc_pValue < 0.05 else np.nan)
    Southern_ATCw_slope_CMIP6.append(Southern_ATCw_slope if Southern_ATCw_pValue < 0.05 else np.nan)
    Southern_ATCc_slope_CMIP6.append(Southern_ATCc_slope if Southern_ATCc_pValue < 0.05 else np.nan)  



#======================================================plot barplot====================================================#
plt.rcParams['xtick.labelsize'] = 8  
plt.rcParams['ytick.labelsize'] = 8 
plt.rcParams['font.size'] = 8 

models=['ISD','CRUJRA','ERA5','CMIP6']
fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(7, 5),gridspec_kw={'width_ratios': [1, 1, 0.6]})#figsize=(width, height)

all_data = []
colors = sns.color_palette("husl", 4) 
colors =['#D55E00', '#0072B2', '#009E73', '#000000']
colors =['#DC143C', 'blue', 'orange', 'black']

bars_Global_ATCw_slope = []
bars_Global_ATCc_slope = []
bars_Northern_ATCw_slope = []
bars_Northern_ATCc_slope = []
bars_Southern_ATCw_slope = []
bars_Southern_ATCc_slope = []

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
        
        bars_Global_ATCw_slope.append(Global_ATCw_slope)
        bars_Global_ATCc_slope.append(Global_ATCc_slope)
        bars_Northern_ATCw_slope.append(Northern_ATCw_slope)
        bars_Northern_ATCc_slope.append(Northern_ATCc_slope)
        bars_Southern_ATCw_slope.append(Southern_ATCw_slope)
        bars_Southern_ATCc_slope.append(Southern_ATCc_slope) 
        
        size=3        
        Global_ATCw = uniform_filter1d(Global_ATCw, size=size, mode='reflect')
        Global_ATCc = uniform_filter1d(Global_ATCc, size=size, mode='reflect')
        NH_ATCw = uniform_filter1d(NH_ATCw, size=size, mode='reflect')
        NH_ATCc = uniform_filter1d(NH_ATCc, size=size, mode='reflect')
        SH_ATCw = uniform_filter1d(SH_ATCw, size=size, mode='reflect')
        SH_ATCc = uniform_filter1d(SH_ATCc, size=size, mode='reflect') 
        
        #plot time series
        years = np.arange(1970, 2021)
        sns.lineplot(x=years, y=Global_ATCw, ax=axes[0,0], label='global ATCw',color=colors[1], zorder=1)
        sns.lineplot(x=years, y=Global_ATCc, ax=axes[0,1], label='global ATCc',color=colors[1], zorder=1) 
        sns.lineplot(x=years, y=NH_ATCw, ax=axes[1,0], label='NH ATCw',color=colors[1], zorder=1)
        sns.lineplot(x=years, y=NH_ATCc, ax=axes[1,1], label='NH ATCc',color=colors[1], zorder=1)               
        sns.lineplot(x=years, y=SH_ATCw, ax=axes[2,0], label='SH ATCw',color=colors[1], zorder=1)
        sns.lineplot(x=years, y=SH_ATCc, ax=axes[2,1], label='SH ATCc',color=colors[1], zorder=1) 
                   

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
        
        bars_Global_ATCw_slope.append(Global_ATCw_slope)
        bars_Global_ATCc_slope.append(Global_ATCc_slope)
        bars_Northern_ATCw_slope.append(Northern_ATCw_slope)
        bars_Northern_ATCc_slope.append(Northern_ATCc_slope)
        bars_Southern_ATCw_slope.append(Southern_ATCw_slope)
        bars_Southern_ATCc_slope.append(Southern_ATCc_slope) 
        
        size=3        
        Global_ATCw = uniform_filter1d(Global_ATCw, size=size, mode='reflect')
        Global_ATCc = uniform_filter1d(Global_ATCc, size=size, mode='reflect')
        NH_ATCw = uniform_filter1d(NH_ATCw, size=size, mode='reflect')
        NH_ATCc = uniform_filter1d(NH_ATCc, size=size, mode='reflect')
        SH_ATCw = uniform_filter1d(SH_ATCw, size=size, mode='reflect')
        SH_ATCc = uniform_filter1d(SH_ATCc, size=size, mode='reflect')        
        
        years = np.arange(1970, 2021)
        sns.lineplot(x=years, y=Global_ATCw, ax=axes[0,0], label='global ATCw',color=colors[2], zorder=1)
        sns.lineplot(x=years, y=Global_ATCc, ax=axes[0,1], label='global ATCc',color=colors[2], zorder=1) 
        sns.lineplot(x=years, y=NH_ATCw, ax=axes[1,0], label='NH ATCw',color=colors[2], zorder=1)
        sns.lineplot(x=years, y=NH_ATCc, ax=axes[1,1], label='NH ATCc',color=colors[2], zorder=1)               
        sns.lineplot(x=years, y=SH_ATCw, ax=axes[2,0], label='SH ATCw',color=colors[2], zorder=1)
        sns.lineplot(x=years, y=SH_ATCc, ax=axes[2,1], label='SH ATCc',color=colors[2], zorder=1)  
        
              
        
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
        
        bars_Global_ATCw_slope.append(Global_ATCw_slope)
        bars_Global_ATCc_slope.append(Global_ATCc_slope)
        bars_Northern_ATCw_slope.append(Northern_ATCw_slope)
        bars_Northern_ATCc_slope.append(Northern_ATCc_slope)
        bars_Southern_ATCw_slope.append(Southern_ATCw_slope)
        bars_Southern_ATCc_slope.append(Southern_ATCc_slope)    
        
        size=3        
        Global_ATCw = uniform_filter1d(Global_ATCw, size=size, mode='reflect')
        Global_ATCc = uniform_filter1d(Global_ATCc, size=size, mode='reflect')
        NH_ATCw = uniform_filter1d(NH_ATCw, size=size, mode='reflect')
        NH_ATCc = uniform_filter1d(NH_ATCc, size=size, mode='reflect')
        SH_ATCw = uniform_filter1d(SH_ATCw, size=size, mode='reflect')
        SH_ATCc = uniform_filter1d(SH_ATCc, size=size, mode='reflect')
        
        years = np.arange(1973, 2024)
        sns.lineplot(x=years, y=Global_ATCw, ax=axes[0,0], label='global ATCw',color=colors[0], zorder=1)
        sns.lineplot(x=years, y=Global_ATCc, ax=axes[0,1], label='global ATCc',color=colors[0], zorder=1) 
        sns.lineplot(x=years, y=NH_ATCw, ax=axes[1,0], label='NH ATCw',color=colors[0], zorder=1)
        sns.lineplot(x=years, y=NH_ATCc, ax=axes[1,1], label='NH ATCc',color=colors[0], zorder=1)               
        sns.lineplot(x=years, y=SH_ATCw, ax=axes[2,0], label='SH ATCw',color=colors[0], zorder=1)
        sns.lineplot(x=years, y=SH_ATCc, ax=axes[2,1], label='SH ATCc',color=colors[0], zorder=1)                                   

    else:
        years = np.arange(1970, 2015)
        alpha = 0.15
        mean_CMIP6_Global_ATCw,std_CMIP6_Global_ATCw,min_CMIP6_Global_ATCw,max_CMIP6_Global_ATCw = Stats(CMIP6_Global_ATCw)
        mean_CMIP6_Global_ATCc,std_CMIP6_Global_ATCc,min_CMIP6_Global_ATCc,max_CMIP6_Global_ATCc = Stats(CMIP6_Global_ATCc)
        mean_CMIP6_NH_ATCw,std_CMIP6_NH_ATCw,min_CMIP6_NH_ATCw,max_CMIP6_NH_ATCw = Stats(CMIP6_NH_ATCw)
        mean_CMIP6_NH_ATCc,std_CMIP6_NH_ATCc,min_CMIP6_NH_ATCc,max_CMIP6_NH_ATCc = Stats(CMIP6_NH_ATCc)
        mean_CMIP6_SH_ATCw,std_CMIP6_SH_ATCw,min_CMIP6_SH_ATCw,max_CMIP6_SH_ATCw = Stats(CMIP6_SH_ATCw)
        mean_CMIP6_SH_ATCc,std_CMIP6_SH_ATCc,min_CMIP6_SH_ATCc,max_CMIP6_SH_ATCc = Stats(CMIP6_SH_ATCc) 

        size=3        
        mean_CMIP6_Global_ATCw = uniform_filter1d(mean_CMIP6_Global_ATCw, size=size, mode='reflect')
        mean_CMIP6_Global_ATCc = uniform_filter1d(mean_CMIP6_Global_ATCc, size=size, mode='reflect')
        mean_CMIP6_NH_ATCw = uniform_filter1d(mean_CMIP6_NH_ATCw, size=size, mode='reflect')
        mean_CMIP6_NH_ATCc = uniform_filter1d(mean_CMIP6_NH_ATCc, size=size, mode='reflect')
        mean_CMIP6_SH_ATCw = uniform_filter1d(mean_CMIP6_SH_ATCw, size=size, mode='reflect')
        mean_CMIP6_SH_ATCc = uniform_filter1d(mean_CMIP6_SH_ATCc, size=size, mode='reflect')        
        
        sns.lineplot(x=years, y=mean_CMIP6_Global_ATCw, ax=axes[0,0], label='global ATCw',color=colors[3], zorder=2)
        sns.lineplot(x=years, y=mean_CMIP6_Global_ATCc, ax=axes[0,1], label='global ATCc',color=colors[3], zorder=2)
        sns.lineplot(x=years, y=mean_CMIP6_NH_ATCw, ax=axes[1,0], label='NH ATCw',color=colors[3], zorder=2)
        sns.lineplot(x=years, y=mean_CMIP6_NH_ATCc, ax=axes[1,1], label='NH ATCc',color=colors[3], zorder=2)
        sns.lineplot(x=years, y=mean_CMIP6_SH_ATCw, ax=axes[2,0], label='SH ATCw',color=colors[3], zorder=2)
        sns.lineplot(x=years, y=mean_CMIP6_SH_ATCc, ax=axes[2,1], label='SH ATCc',color=colors[3], zorder=2)


        axes[0,0].fill_between(years, uniform_filter1d(mean_CMIP6_Global_ATCw-std_CMIP6_Global_ATCw, size=size, mode='reflect'),
                                      uniform_filter1d(mean_CMIP6_Global_ATCw+std_CMIP6_Global_ATCw,size=size, mode='reflect'), color='gray', alpha=alpha, label='CMIP6', zorder=1)
        axes[0,1].fill_between(years, uniform_filter1d(mean_CMIP6_Global_ATCc-std_CMIP6_Global_ATCc,size=size, mode='reflect'),
                                      uniform_filter1d(mean_CMIP6_Global_ATCc+std_CMIP6_Global_ATCc, size=size, mode='reflect'),color='gray', alpha=alpha, label='CMIP6', zorder=1)
        
        axes[1,0].fill_between(years, uniform_filter1d(mean_CMIP6_NH_ATCw-std_CMIP6_NH_ATCw,size=size, mode='reflect'),
                                      uniform_filter1d(mean_CMIP6_NH_ATCw+std_CMIP6_NH_ATCw,size=size, mode='reflect'),color='gray', alpha=alpha, label='CMIP6', zorder=1)
        axes[1,1].fill_between(years, uniform_filter1d(mean_CMIP6_NH_ATCc-std_CMIP6_NH_ATCc,size=size, mode='reflect'),
                                      uniform_filter1d(mean_CMIP6_NH_ATCc+std_CMIP6_NH_ATCc,size=size, mode='reflect'), color='gray', alpha=alpha, label='CMIP6', zorder=1)
        
        axes[2,0].fill_between(years, uniform_filter1d(mean_CMIP6_SH_ATCw-std_CMIP6_SH_ATCw,size=size, mode='reflect'),
                                      uniform_filter1d(mean_CMIP6_SH_ATCw+std_CMIP6_SH_ATCw,size=size, mode='reflect'), color='gray', alpha=alpha, label='CMIP6', zorder=1)
        axes[2,1].fill_between(years, uniform_filter1d(mean_CMIP6_SH_ATCc-std_CMIP6_SH_ATCc,size=size, mode='reflect'),
                                      uniform_filter1d(mean_CMIP6_SH_ATCc+std_CMIP6_SH_ATCc,size=size, mode='reflect'), color='gray', alpha=alpha, label='CMIP6', zorder=1)

        Global_ATCw_slope=np.nanmean(Global_ATCw_slope_CMIP6)
        Global_ATCc_slope=np.nanmean(Global_ATCc_slope_CMIP6)
        Northern_ATCw_slope=np.nanmean(Northern_ATCw_slope_CMIP6)
        Northern_ATCc_slope=np.nanmean(Northern_ATCc_slope_CMIP6)
        Southern_ATCw_slope=np.nanmean(Southern_ATCw_slope_CMIP6)
        Southern_ATCc_slope=np.nanmean(Southern_ATCc_slope_CMIP6)
        
        bars_Global_ATCw_slope.append(Global_ATCw_slope)
        bars_Global_ATCc_slope.append(Global_ATCc_slope)
        bars_Northern_ATCw_slope.append(Northern_ATCw_slope)
        bars_Northern_ATCc_slope.append(Northern_ATCc_slope)
        bars_Southern_ATCw_slope.append(Southern_ATCw_slope)
        bars_Southern_ATCc_slope.append(Southern_ATCc_slope)


error_bars_Global_ATCw_slope=[np.nan,np.nan,np.nan,np.nanstd(Global_ATCw_slope_CMIP6)]
error_bars_Global_ATCc_slope=[np.nan,np.nan,np.nan,np.nanstd(Global_ATCc_slope_CMIP6)]
error_bars_Northern_ATCw_slope=[np.nan,np.nan,np.nan,np.nanstd(Northern_ATCw_slope_CMIP6)]
error_bars_Northern_ATCc_slope=[np.nan,np.nan,np.nan,np.nanstd(Northern_ATCc_slope_CMIP6)]
error_bars_Southern_ATCw_slope=[np.nan,np.nan,np.nan,np.nanstd(Southern_ATCw_slope_CMIP6)]
error_bars_Southern_ATCc_slope=[np.nan,np.nan,np.nan,np.nanstd(Southern_ATCc_slope_CMIP6)]

print('global ATCw', bars_Global_ATCw_slope)
print('global ATCc', bars_Global_ATCc_slope)
print('Northern ATCw', bars_Northern_ATCw_slope)
print('Northern ATCc', bars_Northern_ATCc_slope)
print('Southern ATCw', bars_Southern_ATCw_slope)
print('Southern ATCc', bars_Southern_ATCc_slope)


print('error_global ATCw', error_bars_Global_ATCw_slope)
print('error_global ATCc', error_bars_Global_ATCc_slope)
print('error_Northern ATCw', error_bars_Northern_ATCw_slope)
print('error_Northern ATCc', error_bars_Northern_ATCc_slope)
print('error_Southern ATCw', error_bars_Southern_ATCw_slope)
print('error_Southern ATCc', error_bars_Southern_ATCc_slope)

#barchart
width = 0.3
x=np.arange(4)
ATCw_color='#fdaba1'
ATCc_color='#a1c4d7'
axes[0, 2].barh(y=x - width/2, width=bars_Global_ATCw_slope, height=width, label='ATCw', color=ATCw_color,alpha=1,zorder=2)
axes[0, 2].barh(y=x + width/2, width=bars_Global_ATCc_slope, height=width, label='ATCc', color=ATCc_color,alpha=1,zorder=2)
axes[0, 2].errorbar(y=3 - width/2, x=bars_Global_ATCw_slope[3], xerr=[[np.nanstd(Global_ATCw_slope_CMIP6)], [0]], capsize=3,  fmt='none', ecolor='gray', alpha=1,elinewidth=1,zorder=1)
axes[0, 2].errorbar(y=3 + width/2, x=bars_Global_ATCc_slope[3], xerr=[[np.nanstd(Global_ATCc_slope_CMIP6)], [0]], capsize=3,  fmt='none', ecolor='gray', alpha=1,elinewidth=1,zorder=1)
#axes[0, 2].text(-0.1, 0.98, "(c)", ha="left", va="bottom", transform=axes[0,1].transAxes, fontsize=13, ) 


axes[1, 2].barh(y=x - width/2, width=bars_Northern_ATCw_slope, height=width, label='ATCw', color=ATCw_color,alpha=1,zorder=2)
axes[1, 2].barh(y=x + width/2, width=bars_Northern_ATCc_slope, height=width, label='ATCc', color=ATCc_color,alpha=1,zorder=2)
axes[1, 2].errorbar(y=3 - width/2, x=bars_Northern_ATCw_slope[3], xerr=[[np.nanstd(Northern_ATCw_slope_CMIP6)], [0]], capsize=3,  fmt='none', ecolor='gray', alpha=1,elinewidth=1,zorder=1)
axes[1, 2].errorbar(y=3 + width/2, x=bars_Northern_ATCc_slope[3], xerr=[[np.nanstd(Northern_ATCc_slope_CMIP6)], [0]], capsize=3,  fmt='none', ecolor='gray', alpha=1,elinewidth=1,zorder=1)


#axes[1, 2].text(-0.1, 0.98, "(f)", ha="left", va="bottom", transform=axes[0,1].transAxes, fontsize=13, ) 

axes[2, 2].barh(y=x - width/2, width=bars_Southern_ATCw_slope, height=width, label='ATCw', color=ATCw_color,alpha=1,zorder=2)
axes[2, 2].barh(y=x + width/2, width=bars_Southern_ATCc_slope, height=width, label='ATCc', color=ATCc_color,alpha=1,zorder=2)
axes[2, 2].errorbar(y=3 - width/2, x=bars_Southern_ATCw_slope[3], xerr=[[0], [np.nanstd(Southern_ATCw_slope_CMIP6)]], capsize=3,  fmt='none', ecolor='gray', alpha=1,elinewidth=1,zorder=1)
axes[2, 2].errorbar(y=3 + width/2, x=bars_Southern_ATCc_slope[3], xerr=[[0], [np.nanstd(Southern_ATCc_slope_CMIP6)]], capsize=3,  fmt='none', ecolor='gray', alpha=1,elinewidth=1,zorder=1)

#axes[2, 2].text(-0.1, 0.98, "(i)", ha="left", va="bottom", transform=axes[0,1].transAxes, fontsize=13, ) 


axes[0,0].set_ylabel('Global ATC occurrence',)
axes[1,0].set_ylabel('NH  ATC occurrence', ) 
axes[2,0].set_ylabel('SH  ATC occurrence', )
axes[0,1].set_ylabel('', ) 
axes[1,1].set_ylabel('', ) 
axes[2,1].set_ylabel('', )  
axes[0,0].set_title('ATCw', )  
axes[0,1].set_title('ATCc', )  

axes[0,0].set_ylim(0, 4.2) 
axes[0,1].set_ylim(0, 4.2)
axes[1,0].set_ylim(0, 4.2)
axes[1,1].set_ylim(0, 4.2)
axes[2,0].set_ylim(0, 2.8)
axes[2,1].set_ylim(0, 2.8)

axes[0,0].set_xlim(1970, 2023)
axes[0,1].set_xlim(1970, 2023)
axes[1,0].set_xlim(1970, 2023)
axes[1,1].set_xlim(1970, 2023)
axes[2,0].set_xlim(1970, 2023)
axes[2,1].set_xlim(1970, 2023)
      
for ax in axes[:, :2].flat:
    ax.legend_.remove() 
  
    
legend_handles = []
legend_labels = []

legend_handles.append(Line2D([0], [0], color=colors[0], lw=2, label='ISD'))
legend_handles.append(Line2D([0], [0], color=colors[1], lw=2, label='CRUJRA'))
legend_handles.append(Line2D([0], [0], color=colors[2], lw=2, label='ERA5'))
legend_handles.append(Line2D([0], [0], color=colors[3], lw=2, label='CMIP6'))
legend_handles.append(mpatches.Patch(color='gray', alpha=0.3, label='CMIP6 SD'))

axes[2,0].legend(handles=legend_handles, loc='upper right', frameon=True, fontsize=8,handletextpad=0.1, handlelength=1,labelspacing=0.5,columnspacing=0.5,ncol=2)
axes[0,2].legend(loc='lower right', bbox_to_anchor=(1.22, 0.00),handletextpad=0.1, fontsize=7,handlelength=0.6,title='ATC trend (yr⁻²)',title_fontsize=7 ,alignment='left' )

plt.subplots_adjust(left=0.06,right=0.99,top=0.95,bottom=0.05, hspace=0.25, wspace=0.2)#wspace 水平间距   hspace垂直间距


for ax in axes[:, 2].flat:
    ax.set_xlim(-0.03, 0.03)
    ax.set_yticks([-0.03, 0,0.03])
    ax.set_yticks(x)
    ax.set_yticklabels(models)
    #ax.tick_params(axis='y', length=0, labelleft=False, labelright=True, pad=-106)  # 隐藏刻度线
    ax.tick_params(axis='y', length=0, labelleft=True, labelright=False, pad=-25)
    ax.axvline(x=0, color='gray', linewidth=0.8, linestyle='-', alpha=0.7)
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    pos = ax.get_position()
    ax.set_position([pos.x0 - 0.03, pos.y0, pos.width, pos.height])  # 左移0.1


plt.savefig(str(current_directory)+'/Figure3_time_series_MK.png',dpi=300)
#plt.show()














