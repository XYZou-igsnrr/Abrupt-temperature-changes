import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import netCDF4 as nc

current_directory = os.path.dirname(os.path.abspath(__file__))

models=['CRUJRA', 'ERA5', 'ACCESS-ESM1-5','AWI-CM-1-1-MR','BCC-CSM2-MR','CanESM5','CESM2-WACCM','CMCC-ESM2','E3SM-1-0','EC-Earth3','FGOALS-g3','GFDL-ESM4',
        'IITM-ESM','INM-CM5-0','IPSL-CM6A','KACE-1-0-G','KIOST-ESM','MIROC6','MPI-ESM1-2-HR','NESM3','NorESM2','TaiESM1',]

all_data = []
for i, model in enumerate(models):
    print(model)
    print(i)
    if model=='CRUJRA':
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/ATC_trend_spatial_±10°C_1970_2020_MK.nc")
        
        ATCc_slope=dataset['T_change_down_freq_trend_slope'][:]*365
        ATCw_slope=dataset['T_change_up_freq_trend_slope'][:]*365
        ATCc_pvalue=dataset['T_change_down_freq_trend_p_value'][:]
        ATCw_pvalue=dataset['T_change_up_freq_trend_p_value'][:]

        ATCw_slope[ATCw_pvalue > 0.05] = 0
        ATCc_slope[ATCc_pvalue > 0.05] = 0
        ATCw_slope[ATCw_pvalue == 1] = np.nan
        ATCc_slope[ATCc_pvalue == 1] = np.nan

    elif model=='ERA5':
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/ERA5_ATC_trend_1970_2020_mk.nc")
        ATCc_slope=dataset['T_change_down_freq_trend_slope'][:]*365
        ATCw_slope=dataset['T_change_up_freq_trend_slope'][:]*365
        ATCc_pvalue=dataset['T_change_down_freq_trend_p_value'][:]
        ATCw_pvalue=dataset['T_change_up_freq_trend_p_value'][:]

        ATCw_slope[ATCw_pvalue > 0.05] = 0
        ATCc_slope[ATCc_pvalue > 0.05] = 0
        ATCw_slope[ATCw_pvalue == 1] = np.nan
        ATCc_slope[ATCc_pvalue == 1] = np.nan

    else:
        dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/T_change_freq_"+str(model)+"_yearly_1970-2015_mk.nc")

        ATCc_slope=dataset['T_change_down_freq_trend_slope'][:]*365
        ATCw_slope=dataset['T_change_up_freq_trend_slope'][:]*365
        ATCc_pvalue=dataset['T_change_down_freq_trend_p_value'][:]
        ATCw_pvalue=dataset['T_change_up_freq_trend_p_value'][:]

        ATCw_slope[ATCw_pvalue > 0.05] = 0
        ATCc_slope[ATCc_pvalue > 0.05] = 0

    if 'latitude' in dataset.variables:
        lat = dataset['latitude'][:]
        lon = dataset['longitude'][:]
    elif 'lat' in dataset.variables:
        lat = dataset['lat'][:]
        lon = dataset['lon'][:]



    ATCw_slope_global=np.nanmean(ATCw_slope[lat>-60,:])
    ATCw_slope_NH=np.nanmean(ATCw_slope[lat>0,:])
    ATCw_slope_SH=np.nanmean(ATCw_slope[(lat<0)&(lat>-60),:])

    ATCc_slope_global=np.nanmean(ATCc_slope[lat>-60,:])
    ATCc_slope_NH=np.nanmean(ATCc_slope[lat>0,:])
    ATCc_slope_SH=np.nanmean(ATCc_slope[(lat<0)&(lat>-60),:])
    

    all_data.extend([
            {'Model': model, 'Region': 'Globe', 'ATC_Type': 'ATCw', 'Value': ATCw_slope_global},
            {'Model': model, 'Region': 'Globe', 'ATC_Type': 'ATCc', 'Value': ATCc_slope_global},
            {'Model': model, 'Region': 'NH'    , 'ATC_Type': 'ATCw', 'Value': ATCw_slope_NH},
            {'Model': model, 'Region': 'NH'    , 'ATC_Type': 'ATCc', 'Value': ATCc_slope_NH},
            {'Model': model, 'Region': 'SH'    , 'ATC_Type': 'ATCw', 'Value': ATCw_slope_SH},
            {'Model': model, 'Region': 'SH'    , 'ATC_Type': 'ATCc', 'Value': ATCc_slope_SH}
        ])

df = pd.DataFrame(all_data)
print(df.head(12).sort_values(['Model', 'Region']))

exclude_models = ['ISD', 'CRUJRA', 'ERA5']
df_filtered = df[~df['Model'].isin(exclude_models)]

cmip6_avg = df_filtered.groupby(['Region', 'ATC_Type'], as_index=False)['Value'].mean()
cmip6_avg['Model'] = 'CMIP6'
print(cmip6_avg)

sns.set_theme(style="whitegrid")

# 创建更结构化的数据（每个模型作为一列，每个区域作为一行）
# 先创建数据透视表
df_pivot = df.pivot_table(index='Model', columns=['Region', 'ATC_Type'], values='Value').reset_index()

# 为每个区域创建单独的DataFrame
regions_data = {}
for region in ['Globe', 'NH', 'SH']:
    region_df = df[df['Region'] == region]
    regions_data[region] = region_df.pivot(index='Model', columns='ATC_Type', values='Value').reset_index()
    regions_data[region]['Region'] = region

# 合并数据
combined_df = pd.concat([regions_data[r] for r in ['Globe', 'NH', 'SH']])

# 创建图形 - 类似原示例的布局
fig, axes = plt.subplots(1, 3, figsize=(9.6, 8.5))#figsize=(width, height)

for idx, region in enumerate(['Globe', 'NH', 'SH']):
    ax = axes[idx]

    region_data = combined_df[combined_df['Region'] == region]

    # 将数据转换为长格式用于当前区域
    region_long = region_data.melt(id_vars=['Model', 'Region'], value_vars=['ATCw', 'ATCc'], var_name='ATC_Type', value_name='Value')
    region_long = region_long[region_long['Value'] != 0]

    # 创建点图
    sns.stripplot(data=region_long, x='Value', y='Model',
                  hue='ATC_Type', order=models,
                  size=8, orient='h', jitter=False,
                  palette={'ATCc': '#4ECDC4', 'ATCw': '#FF6B6B'},
                  linewidth=1, edgecolor='w', dodge=True, ax=ax)

    ax.set_title(f'{region}', fontsize=14, fontweight='bold')
    ax.set_xlabel('')
    ax.set_ylabel('' if idx == 0 else '')
    ax.tick_params(axis='x', which='both', length=5, width=1, color='black', bottom=True)
    ax.spines['bottom'].set_color('black')

    ax.xaxis.grid(False)
    ax.yaxis.grid(True)
    ax.axvline(x=0, color='black', linestyle='--', linewidth=1, alpha=0.7)
    if idx==2:
        ticks  = [-0.01, 0, 0.01]
        ax.set_xlim(-0.012, 0.012)
        ax.set_xticks(ticks)
        ax.set_xticklabels([f'{t:.2f}'.replace('-0', '0') if t != 0 else '0' for t in ticks])
    else:
        ticks  = [-0.02, 0, 0.02]
        ax.set_xlim(-0.024, 0.024)
        ax.set_xticks(ticks)
        ax.set_xticklabels([f'{t:.2f}'.replace('-0', '0') if t != 0 else '0' for t in ticks])

    if idx > 0:
        ax.legend_.remove()
    else:
        ax.legend(loc='lower right',handletextpad=0.2, bbox_to_anchor=(1.3, 0))

fig.text(0.58, 0.02, 'ATC trend (yr⁻²)', ha='center', fontsize=12)

plt.subplots_adjust(left=0.16, right=0.98, bottom=0.08 , top=0.96,wspace=1.1,)

sns.despine(left=True, bottom=False)
script_name = os.path.splitext(os.path.basename(__file__))[0]
fig.savefig(str(current_directory)+f"/{script_name}.png", dpi=300)
#plt.show()