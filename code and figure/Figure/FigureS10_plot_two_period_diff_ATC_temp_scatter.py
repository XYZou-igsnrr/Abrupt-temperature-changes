import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import sys
import os
import seaborn as sns
import string
import netCDF4 as nc
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D

current_directory = os.path.dirname(os.path.abspath(__file__))

models=['CRUJRA','ERA5','ACCESS-ESM1-5','AWI-CM-1-1-MR','BCC-CSM2-MR','CanESM5','CESM2-WACCM','CMCC-ESM2','E3SM-1-0','EC-Earth3','FGOALS-g3','GFDL-ESM4',
        'IITM-ESM','INM-CM5-0','IPSL-CM6A','KACE-1-0-G','KIOST-ESM','MIROC6','MPI-ESM1-2-HR','NESM3','NorESM2','TaiESM1',]
labels = [f'({letter})' for letter in string.ascii_lowercase[:22]]


markers = ['d', '*','o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 
           'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o']
           
markers = ['d', '*'] + ['o'] * 20

colors = ['#DD8452', '#DD8452'] + ['#4C90B0'] * 20  

data = []
data_ssp585 = []

for i, model in enumerate(models):
    print(model)
    year=1
    if model=='CRUJRA':
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/CRUJRA_sudden_T_change_freq_1970_2020.nc")
        year = 51        
    elif model=='ERA5':
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/ERA5_sudden_T_change_freq_1970_2020.nc")
        year = 51 

    else:
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/"+str(model)+"_sudden_T_change_freq_1970_2014.nc")
        year = 40
   
         
    Global_ATCw_diff   = dataset.getncattr('Global ATCw frequency two period diff')*365/year
    Northern_ATCw_diff = dataset.getncattr('Northern ATCw frequency two period diff')*365/year
    Southern_ATCw_diff = dataset.getncattr('Southern ATCw frequency two period diff')*365/year
    print(Global_ATCw_diff)
    
    Global_ATCc_diff   = dataset.getncattr('Global ATCc frequency two period diff')*365/year
    Northern_ATCc_diff = dataset.getncattr('Northern ATCc frequency two period diff')*365/year
    Southern_ATCc_diff = dataset.getncattr('Southern ATCc frequency two period diff')*365/year
    
    Global_temp_diff    = dataset.getncattr('Global Temp yearly two period diff')*10/year
    Northern_temp_diff  = dataset.getncattr('Northern Temp yearly two period diff')*10/year
    Southern_temp_diff  = dataset.getncattr('Southern Temp yearly two period diff')*10/year
    
    data.append({
        'Model': model,
        'Global_ATCw_diff':   Global_ATCw_diff,
        'Northern_ATCw_diff': Northern_ATCw_diff,
        'Southern_ATCw_diff': Southern_ATCw_diff,
        
        'Global_ATCc_diff':   Global_ATCc_diff,
        'Northern_ATCc_diff': Northern_ATCc_diff,
        'Southern_ATCc_diff': Southern_ATCc_diff,
        
        'Global_temp_diff':   Global_temp_diff,
        'Northern_temp_diff': Northern_temp_diff,
        'Southern_temp_diff': Southern_temp_diff,
    }) 
    
    if model=='CRUJRA':
        continue         
    elif model=='ERA5':
        continue
    else:
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_ssp585/"+str(model)+"/"+str(model)+"_sudden_T_change_freq_2015_2100.nc")
        year=85
    

    Global_ATCw_diff_ssp585   = dataset.getncattr('Global ATCw frequency two period diff')*365/year
    Northern_ATCw_diff_ssp585 = dataset.getncattr('Northern ATCw frequency two period diff')*365/year
    Southern_ATCw_diff_ssp585 = dataset.getncattr('Southern ATCw frequency two period diff')*365/year
    
    Global_ATCc_diff_ssp585   = dataset.getncattr('Global ATCc frequency two period diff')*365/year
    Northern_ATCc_diff_ssp585 = dataset.getncattr('Northern ATCc frequency two period diff')*365/year
    Southern_ATCc_diff_ssp585 = dataset.getncattr('Southern ATCc frequency two period diff')*365/year
    
    Global_temp_diff_ssp585    = dataset.getncattr('Global Temp yearly two period diff')*10/year
    Northern_temp_diff_ssp585  = dataset.getncattr('Northern Temp yearly two period diff')*10/year
    Southern_temp_diff_ssp585  = dataset.getncattr('Southern Temp yearly two period diff')*10/year
    
    data_ssp585.append({
        'Model': model+'_ssp585',
        'Global_ATCw_diff_ssp585':   Global_ATCw_diff_ssp585,
        'Northern_ATCw_diff_ssp585': Northern_ATCw_diff_ssp585,
        'Southern_ATCw_diff_ssp585': Southern_ATCw_diff_ssp585,
        
        'Global_ATCc_diff_ssp585':   Global_ATCc_diff_ssp585,
        'Northern_ATCc_diff_ssp585': Northern_ATCc_diff_ssp585,
        'Southern_ATCc_diff_ssp585': Southern_ATCc_diff_ssp585,
        
        'Global_temp_diff_ssp585':   Global_temp_diff_ssp585,
        'Northern_temp_diff_ssp585': Northern_temp_diff_ssp585,
        'Southern_temp_diff_ssp585': Southern_temp_diff_ssp585,
    })


data_all = pd.DataFrame(data)
data_ssp585_all = pd.DataFrame(data_ssp585)

data = data_all[data_all['Model'].isin(models[2:])]

data_ssp585 = data_ssp585_all[data_ssp585_all['Model'].isin([m + '_ssp585' for m in models[2:]])]

markers=markers[2:]
colors=colors[2:]

plt.rcParams.update({
    'font.size': 10,           # 控制所有文本的默认大小
    'axes.titlesize': 10,      # 坐标轴标题大小
    'axes.labelsize': 10,      # 坐标轴标签大小
    'xtick.labelsize': 10,     # x轴刻度标签大小
    'ytick.labelsize': 10,     # y轴刻度标签大小
    'legend.fontsize': 10,     # 图例字体大小
    'figure.titlesize': 10     # 图形标题大小
})

fig, axes = plt.subplots(3, 2, figsize=(6.5, 7))

alpha=0.7
size=50


sns.scatterplot(data=data, x='Global_temp_diff',   y='Global_ATCw_diff',   ax=axes[0,0], markers=markers, hue='Model',style='Model', palette=colors, s=size, alpha=alpha, legend=True)
sns.scatterplot(data=data, x='Global_temp_diff',   y='Global_ATCc_diff',   ax=axes[0,1], markers=markers, hue='Model',style='Model', palette=colors, s=size, alpha=alpha, legend=False)
sns.scatterplot(data=data, x='Northern_temp_diff', y='Northern_ATCw_diff', ax=axes[1,0], markers=markers, hue='Model',style='Model', palette=colors, s=size, alpha=alpha, legend=False )
sns.scatterplot(data=data, x='Northern_temp_diff', y='Northern_ATCc_diff', ax=axes[1,1], markers=markers, hue='Model',style='Model', palette=colors, s=size, alpha=alpha, legend=False )
sns.scatterplot(data=data, x='Southern_temp_diff', y='Southern_ATCw_diff', ax=axes[2,0], markers=markers, hue='Model',style='Model', palette=colors, s=size, alpha=alpha, legend=False )
sns.scatterplot(data=data, x='Southern_temp_diff', y='Southern_ATCc_diff', ax=axes[2,1], markers=markers, hue='Model',style='Model', palette=colors, s=size, alpha=alpha, legend=False )

sns.scatterplot(data=data_ssp585, x='Global_temp_diff_ssp585',   y='Global_ATCw_diff_ssp585',   ax=axes[0,0], marker='o', color='#8C8C8C', s=size, alpha=alpha, legend=False)
sns.scatterplot(data=data_ssp585, x='Global_temp_diff_ssp585',   y='Global_ATCc_diff_ssp585',   ax=axes[0,1], marker='o', color='#8C8C8C', s=size, alpha=alpha, )
sns.scatterplot(data=data_ssp585, x='Northern_temp_diff_ssp585', y='Northern_ATCw_diff_ssp585', ax=axes[1,0], marker='o', color='#8C8C8C', s=size, alpha=alpha, legend=False )
sns.scatterplot(data=data_ssp585, x='Northern_temp_diff_ssp585', y='Northern_ATCc_diff_ssp585', ax=axes[1,1], marker='o', color='#8C8C8C', s=size, alpha=alpha, legend=False )
sns.scatterplot(data=data_ssp585, x='Southern_temp_diff_ssp585', y='Southern_ATCw_diff_ssp585', ax=axes[2,0], marker='o', color='#8C8C8C', s=size, alpha=alpha, legend=False )
sns.scatterplot(data=data_ssp585, x='Southern_temp_diff_ssp585', y='Southern_ATCc_diff_ssp585', ax=axes[2,1], marker='o', color='#8C8C8C', s=size, alpha=alpha, legend=False )

sns.regplot(data=data, x='Global_temp_diff',   y='Global_ATCw_diff',   ax=axes[0,0], scatter=False, color=colors[2], line_kws={'linewidth': 2, 'alpha': 0.8})
sns.regplot(data=data, x='Global_temp_diff',   y='Global_ATCc_diff',   ax=axes[0,1], scatter=False, color=colors[2], line_kws={'linewidth': 2, 'alpha': 0.8})
sns.regplot(data=data, x='Northern_temp_diff', y='Northern_ATCw_diff', ax=axes[1,0], scatter=False, color=colors[2], line_kws={'linewidth': 2, 'alpha': 0.8} )
sns.regplot(data=data, x='Northern_temp_diff', y='Northern_ATCc_diff', ax=axes[1,1], scatter=False, color=colors[2], line_kws={'linewidth': 2, 'alpha': 0.8} )
sns.regplot(data=data, x='Southern_temp_diff', y='Southern_ATCw_diff', ax=axes[2,0], scatter=False, color=colors[2], line_kws={'linewidth': 2, 'alpha': 0.8} )
sns.regplot(data=data, x='Southern_temp_diff', y='Southern_ATCc_diff', ax=axes[2,1], scatter=False, color=colors[2], line_kws={'linewidth': 2, 'alpha': 0.8} )

sns.regplot(data=data_ssp585, x='Global_temp_diff_ssp585',   y='Global_ATCw_diff_ssp585',   ax=axes[0,0], scatter=False, color='#8C8C8C', line_kws={'linewidth': 2, 'alpha': 0.8})
sns.regplot(data=data_ssp585, x='Global_temp_diff_ssp585',   y='Global_ATCc_diff_ssp585',   ax=axes[0,1], scatter=False, color='#8C8C8C', line_kws={'linewidth': 2, 'alpha': 0.8} )
sns.regplot(data=data_ssp585, x='Northern_temp_diff_ssp585', y='Northern_ATCw_diff_ssp585', ax=axes[1,0], scatter=False, color='#8C8C8C', line_kws={'linewidth': 2, 'alpha': 0.8} )
sns.regplot(data=data_ssp585, x='Northern_temp_diff_ssp585', y='Northern_ATCc_diff_ssp585', ax=axes[1,1], scatter=False, color='#8C8C8C', line_kws={'linewidth': 2, 'alpha': 0.8} )
sns.regplot(data=data_ssp585, x='Southern_temp_diff_ssp585', y='Southern_ATCw_diff_ssp585', ax=axes[2,0], scatter=False, color='#8C8C8C', line_kws={'linewidth': 2, 'alpha': 0.8} )
sns.regplot(data=data_ssp585, x='Southern_temp_diff_ssp585', y='Southern_ATCc_diff_ssp585', ax=axes[2,1], scatter=False, color='#8C8C8C', line_kws={'linewidth': 2, 'alpha': 0.8} )


target_models = ['CRUJRA','ERA5']
for target_model in target_models:
    target_data = data_all[data_all['Model'] == target_model]
    if target_model=='CRUJRA':
        marker='d'
    else:
        marker='*'
    if not target_data.empty:
        axes[0,0].scatter(target_data['Global_temp_diff'], target_data['Global_ATCw_diff'], marker=marker, color='#DD8452', s=size*3, alpha=0.8, zorder=10)
        axes[0,1].scatter(target_data['Global_temp_diff'], target_data['Global_ATCc_diff'], marker=marker, color='#DD8452', s=size*3, alpha=0.8, zorder=10)
        axes[1,0].scatter(target_data['Northern_temp_diff'], target_data['Northern_ATCw_diff'], marker=marker, color='#DD8452', s=size*3, alpha=0.8, zorder=10)
        axes[1,1].scatter(target_data['Northern_temp_diff'], target_data['Northern_ATCc_diff'], marker=marker, color='#DD8452', s=size*3, alpha=0.8, zorder=10)
        axes[2,0].scatter(target_data['Southern_temp_diff'], target_data['Southern_ATCw_diff'], marker=marker, color='#DD8452', s=size*3, alpha=0.8, zorder=10)
        axes[2,1].scatter(target_data['Southern_temp_diff'], target_data['Southern_ATCc_diff'], marker=marker, color='#DD8452', s=size*3, alpha=0.8, zorder=10)




axes[0,0].set_xlabel('')
axes[0,0].set_ylabel('')
axes[0,0].set_ylim(-0.025, 0.003)
axes[0,0].set_yticks([-0.02,-0.01,-0.015,-0.005, 0,])

axes[0,1].set_xlabel('')
axes[0,1].set_ylabel('')
axes[0,1].set_ylim(-0.025, 0.003)
axes[0,1].set_yticks([-0.02,-0.015,-0.01,-0.005, 0,])

axes[1,0].set_xlabel('')
axes[1,0].set_ylabel('ATC occurrence change (yr⁻²)')
axes[1,0].set_ylim(-0.032, 0.0035)
axes[1,0].set_yticks([-0.03,-0.02,-0.01,0,])

axes[1,1].set_xlabel('')
axes[1,1].set_ylabel('')
axes[1,1].set_ylim(-0.032, 0.0035)
axes[1,1].set_yticks([-0.03,-0.02,-0.01,0,])


axes[2,0].set_xlabel('warming per decade (°C)')
axes[2,0].set_ylabel('')
axes[2,0].set_ylim(-0.00018, 0.001)
axes[2,0].set_yticks([0, 0.0004,0.0008,])

axes[2,1].set_xlabel('warming per decade (°C)')
axes[2,1].set_ylabel('')
axes[2,1].set_ylim(-0.0009, 0.005)
axes[2,1].set_yticks([0, 0.002,0.004,])

axes[0,0].text(0.96, 0.92, "a", ha="right", va="center", transform=axes[0,0].transAxes, fontsize=16, weight='bold')
axes[0,0].text(0.50, 0.92, "Globe", ha="center", va="center", transform=axes[0,0].transAxes, fontsize=13, )
axes[0,1].text(0.96, 0.92, "b", ha="right", va="center", transform=axes[0,1].transAxes, fontsize=16, weight='bold')
axes[0,1].text(0.50, 0.92, "Globe", ha="center", va="center", transform=axes[0,1].transAxes, fontsize=13, )
axes[1,0].text(0.96, 0.92, "c ", ha="right", va="center", transform=axes[1,0].transAxes, fontsize=16, weight='bold')
axes[1,0].text(0.50, 0.92, "NH", ha="center", va="center", transform=axes[1,0].transAxes, fontsize=13, )
axes[1,1].text(0.96, 0.92, "d ", ha="right", va="center", transform=axes[1,1].transAxes, fontsize=16, weight='bold')
axes[1,1].text(0.50, 0.92, "NH", ha="center", va="center", transform=axes[1,1].transAxes, fontsize=13, )
axes[2,0].text(0.96, 0.92, "e", ha="right", va="center", transform=axes[2,0].transAxes, fontsize=16, weight='bold')
axes[2,0].text(0.50, 0.92, "SH", ha="center", va="center", transform=axes[2,0].transAxes, fontsize=13, )
axes[2,1].text(0.96, 0.92, "f ", ha="right", va="center", transform=axes[2,1].transAxes, fontsize=16, weight='bold')
axes[2,1].text(0.50, 0.92, "SH", ha="center", va="center", transform=axes[2,1].transAxes, fontsize=13, )

x_min, x_max = min(data['Global_temp_diff'].min(), data_ssp585['Global_temp_diff_ssp585'].min()), max(data['Global_temp_diff'].max(), data_ssp585['Global_temp_diff_ssp585'].max())
x_min, x_max = 0+0.02, 1+0.02
#margin = 0.1 * (x_max - x_min)  
axes[0,0].set_xlim(x_min, x_max)
axes[0,1].set_xlim(x_min, x_max)
axes[0,0].set_xticks([0.1, 0.3, 0.5, 0.7, 0.9 ])
axes[0,1].set_xticks([0.1, 0.3, 0.5, 0.7, 0.9 ])

x_min, x_max = min(data['Northern_temp_diff'].min(), data_ssp585['Northern_temp_diff_ssp585'].min()), max(data['Northern_temp_diff'].max(), data_ssp585['Northern_temp_diff_ssp585'].max())

x_min, x_max = 0+0.02, 1+0.02
#margin = 0.1 * (x_max - x_min)
axes[1,0].set_xlim(x_min, x_max)
axes[1,1].set_xlim(x_min, x_max)
axes[1,0].set_xticks([0.1, 0.3, 0.5, 0.7, 0.90  ])
axes[1,1].set_xticks([0.1, 0.3, 0.5, 0.7, 0.9  ])

x_min, x_max = min(data['Southern_temp_diff'].min(), data_ssp585['Southern_temp_diff_ssp585'].min()), max(data['Southern_temp_diff'].max(), data_ssp585['Southern_temp_diff_ssp585'].max())

#x_min, x_max = data['Southern_temp_diff'].min(), data['Southern_temp_diff'].max()
x_min, x_max = 0, 0.75
#margin = 0.1 * (x_max - x_min)
axes[2,0].set_xlim(x_min, x_max)
axes[2,1].set_xlim(x_min, x_max)
axes[2,0].set_xticks([0.1, 0.3, 0.5, 0.7])
axes[2,1].set_xticks([0.1, 0.3, 0.5, 0.7])


custom_handles = [
    Line2D([0], [0], marker='d',color='#DD8452', label='CURJRA', linestyle='None', markersize=6),    
    Line2D([0], [0], marker='*',color='#DD8452', label='ERA5', linestyle='None', markersize=7),    
    Line2D([0], [0], marker=markers[2],color=colors[2], label='CMIP6—historical', linestyle='None', markersize=6),
    Line2D([0], [0], marker=markers[2],color='#8C8C8C', label='CMIP6—ssp585', linestyle='None', markersize=6)
]


handles, labels = axes[0,0].get_legend_handles_labels()
axes[0,0].get_legend().remove()
legend = axes[0,0].legend(handles=custom_handles, framealpha=0.8, bbox_to_anchor=(0.00, 0.00), loc='lower left',fontsize=9,handletextpad=0.3,labelspacing=0.2)


plt.subplots_adjust(left=0.14,right=0.98,top=0.97,bottom=0.08, hspace=0.15, wspace=0.31)#hspace垂直间距   wspace 水平间距
script_name = os.path.splitext(os.path.basename(__file__))[0]
plt.savefig(str(current_directory)+f"/{script_name}.png", dpi=300)
#plt.show()

