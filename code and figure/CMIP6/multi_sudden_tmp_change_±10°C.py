# srun --nodelist=node01 --cpus-per-task=40 

import netCDF4 as nc
import numpy as np
import csv
import os
import multiprocessing
import sys

current_directory = os.path.dirname(os.path.abspath(__file__))

#date_area = nc.Dataset("/data1/zxy/runcable-access-esm/grid_area_0.5°_-y.nc")
#area_weight=date_area['area_weight'][:]

#ATC threshold
threshold=10
model='ACCESS-ESM1-5'

dataset_ref = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/"+str(model)+"_splityear_seamask.nc")
topo=dataset_ref['topo'][:]
mask=topo.mask

def process_nc_file(year):

    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/"+str(model)+"_splityear_"+str(year)+".nc")
    tmp = dataset['tas'][:]
    lat = dataset['lat'][:]
    time_len = len(dataset.dimensions['time'])
    lat_len =len(dataset.dimensions['lat'])
    lon_len =len(dataset.dimensions['lon'])

    tmp_change=np.ma.masked_array(np.zeros((time_len, lat_len, lon_len), dtype=np.float16))
    
    for time in range(0,time_len-1):
        tmp_change[time,:]=tmp[time+1,:]-tmp[time,:]

    #freq in each cell
    ATCw=np.nanmean(np.where(tmp_change>threshold,1,0),axis=0)
    ATCc=np.nanmean(np.where(tmp_change<(-threshold),1,0),axis=0)
    
    ATCw=np.ma.masked_where(topo.mask,ATCw)
    ATCc=np.ma.masked_where(topo.mask,ATCc)    

    Global_ATCw=np.nanmean(ATCw[lat>-60,:])
    Global_ATCc=np.nanmean(ATCc[lat>-60,:])
    Southern_ATCw=np.nanmean(ATCw[(lat < 0) & (lat > -60),:])
    Southern_ATCc=np.nanmean(ATCc[(lat < 0) & (lat > -60),:])
    Northern_ATCw=np.nanmean(ATCw[lat>0,:])
    Northern_ATCc=np.nanmean(ATCc[lat>0,:])
    
    print(str(year)+'finish')
    sys.stdout.flush()
    return [year,Global_ATCw,Global_ATCc,Northern_ATCw,Northern_ATCc,Southern_ATCw,Southern_ATCc]



if __name__ == "__main__":
    
    year = list(range(1970,2015))

    #Number of processes
    num_processes=10
    pool = multiprocessing.Pool(processes=num_processes)
    
    result=pool.map(process_nc_file, year)

    pool.close()
    pool.join()

    current_directory = os.path.dirname(os.path.abspath(__file__))
    #csv
    csv_file = open(str(current_directory)+"/"+str(model)+"_T_sudden_change_±"+str(threshold)+"°C_1970_2015.csv", 'w', newline='', encoding='utf-8')
    header=['year','Global_ATCw','Global_ATCc','Northern_ATCw','Northern_ATCc','Southern_ATCw','Southern_ATCc']
    csv.writer(csv_file).writerow(header)
    csv.writer(csv_file).writerows(result)





