import os
import sys
import csv
from collections import Counter
import pandas as pd
import multiprocessing
from datetime import datetime
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress
import pymannkendall as mk
import matplotlib.ticker as ticker
from matplotlib.ticker import FuncFormatter
import string
from matplotlib.lines import Line2D


current_directory = os.path.dirname(os.path.abspath(__file__))

plt.rcParams['xtick.labelsize'] = 13  
plt.rcParams['ytick.labelsize'] = 13 
plt.rcParams['font.size'] = 13 

fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(7.5, 8))#figsize=(width, height)
#axes = axes.flatten()


def plot_line(axes,ATC_csv_dataset,label):

    linestyle_map = {'ISD': '-',
                     'CRUJRA': '--', 
                     'ERA5': ':',
                     }
    
    linestyle = linestyle_map.get(label, '-')

    gradient=ATC_csv_dataset['Temperature threshold']
    
    global_ATC_ave  =ATC_csv_dataset['global_ave_freq_up']+ATC_csv_dataset['global_ave_freq_down']
    Northern_ATC_ave=ATC_csv_dataset['Northern_ave_freq_up']+ATC_csv_dataset['Northern_ave_freq_down']
    Southern_ATC_ave=ATC_csv_dataset['Southern_ave_freq_up']+ATC_csv_dataset['Southern_ave_freq_down']
    
    global_rel_change  =(ATC_csv_dataset['global_d_freq_up']+ATC_csv_dataset['global_d_freq_down'])/global_ATC_ave
    Northern_rel_change=(ATC_csv_dataset['Northern_d_freq_up']+ATC_csv_dataset['Northern_d_freq_down'])/Northern_ATC_ave
    Southern_rel_change=(ATC_csv_dataset['Southern_d_freq_up']+ATC_csv_dataset['Southern_d_freq_down'])/Southern_ATC_ave
   
    global_rel_change_up    =ATC_csv_dataset['global_d_freq_up']    /ATC_csv_dataset['global_ave_freq_up']
    global_rel_change_down  =ATC_csv_dataset['global_d_freq_down']  /ATC_csv_dataset['global_ave_freq_down']
    Northern_rel_change_up  =ATC_csv_dataset['Northern_d_freq_up']  /ATC_csv_dataset['Northern_ave_freq_up']
    Northern_rel_change_down=ATC_csv_dataset['Northern_d_freq_down']/ATC_csv_dataset['Northern_ave_freq_down']
    Southern_rel_change_up  =ATC_csv_dataset['Southern_d_freq_up']  /ATC_csv_dataset['Southern_ave_freq_up']
    Southern_rel_change_down=ATC_csv_dataset['Southern_d_freq_down']/ATC_csv_dataset['Southern_ave_freq_down']

    global_rel_change_d   = global_rel_change_up - global_rel_change_down 
    Northern_rel_change_d = Northern_rel_change_up - Northern_rel_change_down 
    Southern_rel_change_d = Southern_rel_change_up - Southern_rel_change_down 
    
    xticks = [4,8,12,16]
    xticklabels = [str(x) for x in xticks]
    xticklabels[-1] = f"{xticklabels[-1]}°C"

    
    #===============================================plot ave=========================================================================#
    sns.lineplot(x=gradient, y=global_ATC_ave*364,    ax=axes[0,0], label=label,color='#ff7f0e', zorder=1,linewidth=1.5,
                  marker='o',markersize=3,markerfacecolor='gray',markeredgecolor='none',markeredgewidth=0.8,linestyle=linestyle)
    sns.lineplot(x=gradient, y=Northern_ATC_ave*364,  ax=axes[1,0], label=label,color='#ff7f0e', zorder=1,linewidth=1.5,
                  marker='o',markersize=3,markerfacecolor='gray',markeredgecolor='none',markeredgewidth=0.8,linestyle=linestyle)
    sns.lineplot(x=gradient, y=Southern_ATC_ave*364,  ax=axes[2,0], label=label,color='#ff7f0e', zorder=1,linewidth=1.5,
                  marker='o',markersize=3,markerfacecolor='gray',markeredgecolor='none',markeredgewidth=0.8,linestyle=linestyle)     

    for ax in [axes[0,0],axes[1,0],axes[2,0]]:                
        ax.set_xticks([])
        ax.set_xlabel('')
        ax.set_ylabel("")  
        ax.set_yscale('log')  
        ax.set_ylim(0.002, 1*364)
        yticks=[0.01,0.1, 1,10, 100, 300]
        ax.set_yticks(yticks)
        ax.yaxis.set_minor_locator(ticker.NullLocator())
        ax.set_yticklabels([r'$10^{-2}$',r'$10^{-1}$',r'$10^{0}$', r'$10^{1}$', r'$10^{2}$', '300'])
        ax.set_xlim(1, 17)
        ax.legend().remove()
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels)

    
    #===============================================plot rel=========================================================================#
    
    sns.lineplot(x=gradient, y=global_rel_change,     ax=axes[0,1], label=label,color='#ff7f0e', zorder=1,linewidth=1.5,
                  marker='o',markersize=3,markerfacecolor='gray',markeredgecolor='none',markeredgewidth=0.8,linestyle=linestyle)
    sns.lineplot(x=gradient, y=Northern_rel_change,   ax=axes[1,1], label=label,color='#ff7f0e', zorder=1,linewidth=1.5,
                  marker='o',markersize=3,markerfacecolor='gray',markeredgecolor='none',markeredgewidth=0.8,linestyle=linestyle)
    sns.lineplot(x=gradient, y=Southern_rel_change,   ax=axes[2,1], label=label,color='#ff7f0e', zorder=1,linewidth=1.5,
                  marker='o',markersize=3,markerfacecolor='gray',markeredgecolor='none',markeredgewidth=0.8,linestyle=linestyle)
    for ax in [axes[0,1],axes[1,1],axes[2,1]]:    
        ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.8, zorder=0)
        ax.set_xticks([])
        ax.set_xlabel('')
        ax.set_ylabel("")
            
        ax.set_ylim(-1, 1)
        ax.set_xlim(1, 17)
        ax.legend().remove()
        ax.set_yticks([])
        ax.yaxis.set_major_locator(ticker.MaxNLocator(5))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x*100:.0f}%"))
        #ax.yaxis.set_label_position("right")  # 将y轴标签移到右侧
        #ax.yaxis.tick_right()  # 将y轴刻度移到右侧
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels)
        

#=======================================================plot ISD======================================================================#
ATC_csv_dataset_ISD = pd.read_csv("/data1/zxy/sudden_temp_change/ISD-global-daily/multi-threshold/ATC_multi_thresholds_time_trend.csv")
plot_line(axes,ATC_csv_dataset_ISD,'ISD')

axes[0,0].text(0.96, 0.92, "a", ha="right", va="center", transform=axes[0,0].transAxes, fontsize=16, weight='bold')
axes[0,0].text(0.50, 0.92, "Globe", ha="center", va="center", transform=axes[0,0].transAxes, fontsize=13, )
axes[0,1].text(0.96, 0.92, "b", ha="right", va="center", transform=axes[0,1].transAxes, fontsize=16, weight='bold')
axes[0,1].text(0.50, 0.92, "Globe", ha="center", va="center", transform=axes[0,1].transAxes, fontsize=13, )

#=======================================================plot CRUJRA======================================================================#
ATC_csv_dataset_CRUJRA = pd.read_csv("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/multi-threshold/ATC_multi_thresholds_time_trend_1970_2020.csv")
plot_line(axes,ATC_csv_dataset_CRUJRA,'CRUJRA')
axes[1,0].text(0.96, 0.92, "c ", ha="right", va="center", transform=axes[1,0].transAxes, fontsize=16, weight='bold')
axes[1,0].text(0.50, 0.92, "NH", ha="center", va="center", transform=axes[1,0].transAxes, fontsize=13, )
axes[1,1].text(0.96, 0.92, "d ", ha="right", va="center", transform=axes[1,1].transAxes, fontsize=16, weight='bold')
axes[1,1].text(0.50, 0.92, "NH", ha="center", va="center", transform=axes[1,1].transAxes, fontsize=13, )

#=======================================================plot ERA5======================================================================#
ATC_csv_dataset_ERA5 = pd.read_csv("/data1/zxy/sudden_temp_change/ERA5_tmp/multi-threshold/ATC_multi_thresholds_time_trend_1970_2020.csv")
plot_line(axes,ATC_csv_dataset_ERA5,'ERA5')
axes[2,0].text(0.96, 0.92, "e", ha="right", va="center", transform=axes[2,0].transAxes, fontsize=16, weight='bold')
axes[2,0].text(0.50, 0.92, "SH", ha="center", va="center", transform=axes[2,0].transAxes, fontsize=13, )
axes[2,1].text(0.96, 0.92, "f ", ha="right", va="center", transform=axes[2,1].transAxes, fontsize=16, weight='bold')
axes[2,1].text(0.50, 0.92, "SH", ha="center", va="center", transform=axes[2,1].transAxes, fontsize=13, )

#=======================================================CMIP6 models======================================================================#

def Stats(data):

    mean = np.mean(data, axis=0)
    std  = np.std(data, axis=0)
    min_value  = np.min(data, axis=0)
    max_value = np.max(data, axis=0)

    return mean,std,min_value,max_value

models=['ACCESS-ESM1-5','AWI-CM-1-1-MR','BCC-CSM2-MR','CanESM5','CESM2-WACCM','CMCC-ESM2','E3SM-1-0','EC-Earth3','FGOALS-g3','GFDL-ESM4',
        'IITM-ESM','INM-CM5-0','IPSL-CM6A','KACE-1-0-G','KIOST-ESM','MIROC6','MPI-ESM1-2-HR','NESM3','NorESM2','TaiESM1',]
        
CMIP6_data_global_ave   = []
CMIP6_data_Northern_ave = []
CMIP6_data_Southern_ave = []

CMIP6_data_global_rel   = []
CMIP6_data_Northern_rel = []
CMIP6_data_Southern_rel = []

CMIP6_data_global_rel_d   = []
CMIP6_data_Northern_rel_d = []
CMIP6_data_Southern_rel_d = []

for i, model in enumerate(models):
    print(model)
    print(i)
    ATC_csv_dataset = pd.read_csv("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/multi-threshold/ATC_multi_thresholds_time_trend_1970_2015.csv")


    gradient=ATC_csv_dataset['Temperature threshold']

    global_ATC_ave  =ATC_csv_dataset['global_ave_freq_up']+ATC_csv_dataset['global_ave_freq_down']
    Northern_ATC_ave=ATC_csv_dataset['Northern_ave_freq_up']+ATC_csv_dataset['Northern_ave_freq_down']
    Southern_ATC_ave=ATC_csv_dataset['Southern_ave_freq_up']+ATC_csv_dataset['Southern_ave_freq_down']
    
    global_rel_change  =(ATC_csv_dataset['global_d_freq_up']+ATC_csv_dataset['global_d_freq_down'])/global_ATC_ave
    Northern_rel_change=(ATC_csv_dataset['Northern_d_freq_up']+ATC_csv_dataset['Northern_d_freq_down'])/Northern_ATC_ave
    Southern_rel_change=(ATC_csv_dataset['Southern_d_freq_up']+ATC_csv_dataset['Southern_d_freq_down'])/Southern_ATC_ave
   
    global_rel_change_up    =ATC_csv_dataset['global_d_freq_up']    /ATC_csv_dataset['global_ave_freq_up']
    global_rel_change_down  =ATC_csv_dataset['global_d_freq_down']  /ATC_csv_dataset['global_ave_freq_down']
    Northern_rel_change_up  =ATC_csv_dataset['Northern_d_freq_up']  /ATC_csv_dataset['Northern_ave_freq_up']
    Northern_rel_change_down=ATC_csv_dataset['Northern_d_freq_down']/ATC_csv_dataset['Northern_ave_freq_down']
    Southern_rel_change_up  =ATC_csv_dataset['Southern_d_freq_up']  /ATC_csv_dataset['Southern_ave_freq_up']
    Southern_rel_change_down=ATC_csv_dataset['Southern_d_freq_down']/ATC_csv_dataset['Southern_ave_freq_down']

    global_rel_change_d   = global_rel_change_up - global_rel_change_down 
    Northern_rel_change_d = Northern_rel_change_up - Northern_rel_change_down 
    Southern_rel_change_d = Southern_rel_change_up - Southern_rel_change_down 

    CMIP6_data_global_ave  .append(global_ATC_ave)
    CMIP6_data_Northern_ave.append(Northern_ATC_ave)
    CMIP6_data_Southern_ave.append(Southern_ATC_ave)
    
    CMIP6_data_global_rel  .append(global_rel_change)
    CMIP6_data_Northern_rel.append(Northern_rel_change)
    CMIP6_data_Southern_rel.append(Southern_rel_change)
    
    CMIP6_data_global_rel_d  .append(global_rel_change_d)
    CMIP6_data_Northern_rel_d.append(Northern_rel_change_d)
    CMIP6_data_Southern_rel_d.append(Southern_rel_change_d)            
    

#xticks = [4,8,12,16]
#xticklabels = [str(x) for x in xticks]
#xticklabels[-1] = f"{xticklabels[-1]}°C"
    
CMIP6_data_global_ave = np.array(CMIP6_data_global_ave) *364
CMIP6_data_Northern_ave = np.array(CMIP6_data_Northern_ave) *364
CMIP6_data_Southern_ave = np.array(CMIP6_data_Southern_ave)*364

CMIP6_data_global_rel = np.array(CMIP6_data_global_rel) 
CMIP6_data_Northern_rel = np.array(CMIP6_data_Northern_rel) 
CMIP6_data_Southern_rel = np.array(CMIP6_data_Southern_rel)

CMIP6_data_global_rel_d = np.array(CMIP6_data_global_rel_d) 
CMIP6_data_Northern_rel_d = np.array(CMIP6_data_Northern_rel_d) 
CMIP6_data_Southern_rel_d = np.array(CMIP6_data_Southern_rel_d)

mean_CMIP6_global_ave,std_CMIP6_global_ave,min_CMIP6_global_ave,max_CMIP6_global_ave = Stats(CMIP6_data_global_ave)
mean_CMIP6_Northern_ave,std_CMIP6_Northern_ave,min_CMIP6_Northern_ave,max_CMIP6_Northern_ave = Stats(CMIP6_data_Northern_ave)
mean_CMIP6_Southern_ave,std_CMIP6_Southern_ave,min_CMIP6_Southern_ave,max_CMIP6_Southern_ave = Stats(CMIP6_data_Southern_ave)

mean_CMIP6_global_rel,std_CMIP6_global_rel,min_CMIP6_global_rel,max_CMIP6_global_rel = Stats(CMIP6_data_global_rel)
mean_CMIP6_Northern_rel,std_CMIP6_Northern_rel,min_CMIP6_Northern_rel,max_CMIP6_Northern_rel = Stats(CMIP6_data_Northern_rel)
mean_CMIP6_Southern_rel,std_CMIP6_Southern_rel,min_CMIP6_Southern_rel,max_CMIP6_Southern_rel = Stats(CMIP6_data_Southern_rel)

mean_CMIP6_global_rel_d,std_CMIP6_global_rel_d,min_CMIP6_global_rel_d,max_CMIP6_global_rel_d = Stats(CMIP6_data_global_rel_d)
mean_CMIP6_Northern_rel_d,std_CMIP6_Northern_rel_d,min_CMIP6_Northern_rel_d,max_CMIP6_Northern_rel_d = Stats(CMIP6_data_Northern_rel_d)
mean_CMIP6_Southern_rel_d,std_CMIP6_Southern_rel_d,min_CMIP6_Southern_rel_d,max_CMIP6_Southern_rel_d = Stats(CMIP6_data_Southern_rel_d)

alpha=0.15
axes[0,0].fill_between(gradient, min_CMIP6_global_ave, max_CMIP6_global_ave, color='gray', alpha=alpha, label='CMIP6', zorder=1)
axes[1,0].fill_between(gradient, min_CMIP6_Northern_ave, max_CMIP6_Northern_ave, color='gray', alpha=alpha, label='CMIP6', zorder=1)
axes[2,0].fill_between(gradient, min_CMIP6_Southern_ave, max_CMIP6_Southern_ave, color='gray', alpha=alpha, label='CMIP6', zorder=1)

axes[0,1].fill_between(gradient, min_CMIP6_global_rel, max_CMIP6_global_rel, color='gray', alpha=alpha, label='CMIP6', zorder=1)
axes[1,1].fill_between(gradient, min_CMIP6_Northern_rel, max_CMIP6_Northern_rel, color='gray', alpha=alpha, label='CMIP6', zorder=1)
axes[2,1].fill_between(gradient, min_CMIP6_Southern_rel, max_CMIP6_Southern_rel, color='gray', alpha=alpha, label='CMIP6', zorder=1)

axes[2,1].set_ylim(-2.4, 2.4)
axes[2,0].set_ylim(0.002, 1*364)
axes[2,0].set_yticks([0.01,0.1, 1,10, 100, 300])
axes[2,0].set_yticklabels([r'$10^{-2}$',r'$10^{-1}$',r'$10^{0}$', r'$10^{1}$', r'$10^{2}$', '300'])


#axes[0,0].set_title('Occurrence (yr⁻¹) ', fontsize=13)
#axes[0,1].set_title('Relative changes', fontsize=13)

#axes[0,0].set_ylabel('Global')
axes[1,0].set_ylabel('Occurrence (yr⁻¹)')
axes[1,1].set_ylabel('Relative changes')
axes[2,0].set_xlabel('temperature threshold')
axes[2,1].set_xlabel('temperature threshold')
#axes[2,0].set_ylabel('SH')

axes[0,0].legend(loc='lower left',fontsize=12)



plt.subplots_adjust(left=0.12,right=0.97,top=0.98,bottom=0.07, hspace=0.2, wspace=0.4)#wspace 水平间距   hspace垂直间距

script_name = os.path.splitext(os.path.basename(__file__))[0]
plt.savefig(str(current_directory)+f"/{script_name}.png", dpi=300)
#plt.show()

