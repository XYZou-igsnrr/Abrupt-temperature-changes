# srun --nodelist=node01 --cpus-per-task=40

import netCDF4 as nc
import numpy as np
import os
import multiprocessing
import sys
from scipy.stats import linregress

current_directory = os.path.dirname(os.path.abspath(__file__))
model='ERA5'

dataset_ref = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/ERA5_t2m_daily/ERA5_t2m_1950_daily.nc")
lon_dim = dataset_ref.dimensions['longitude'].size
lat_dim = dataset_ref.dimensions['latitude'].size


month_day =[range(0,30),range(31,58),
                range(59,89),range(90,119),
                range(120,150),range(151,180),
                range(181,211),range(212,242),
                range(243,272),range(273,303),
                range(304,333),range(334,363),#温度突变是两天差值，实际只有364个时间点，少的时间点放在12月
              ]


def write_nc_file(freq_up,freq_down,year):

    new = nc.Dataset(str(current_directory)+"/ATC_monthly/T_change_freq_monthly_"+str(model)+"_"+str(year)+".nc", 'w')

    new.createDimension("lat", lat_dim)
    new.createDimension("lon", lon_dim)
    new.createDimension("time", 12)

    new.createVariable("lat", "float64", ("lat",))
    new.createVariable("lon", "float64", ("lon",))
    new.createVariable("time", "float64", ("time",))

    new.variables['lat'].__setattr__("long_name", "Latitude")
    new.variables['lat'].__setattr__("standard_name", "latitude")
    new.variables['lat'].__setattr__("axis", "Y")
    new.variables['lat'].__setattr__("units", "degrees_north")

    new.variables['lon'].__setattr__("long_name", "Longitude")
    new.variables['lon'].__setattr__("standard_name", "longitude")
    new.variables['lon'].__setattr__("axis", "X")
    new.variables['lon'].__setattr__("units", "degrees_east")

    new.variables['time'].__setattr__("long_name", "month")
    new.variables['time'].__setattr__("standard_name", "month")
    new.variables['time'].__setattr__("units", "months since 1850-01-01 00:00:00")
    new.variables['time'].__setattr__("calendar", "gregorian")

    new.variables['lat'][:] = dataset_ref['latitude'][:]
    new.variables['lon'][:] = dataset_ref['longitude'][:]

    months_since_base = [(year - 1850) * 12 + m for m in range(0, 12)]
    new.variables['time'][:] = months_since_base

    new.createVariable("T_change_up_freq","float32", (u'time',u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_up_freq"][:,:]=freq_up
    new.variables["T_change_up_freq"].__setattr__("standard_name","T_change_up_freq_monthly")

    new.createVariable("T_change_down_freq","float32", (u'time',u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq"][:,:]=freq_down
    new.variables["T_change_down_freq"].__setattr__("standard_name","T_change_down_freq_monthly")

    new.close()


def process_nc_file(year):
    print(str(year)+'star')
    sys.stdout.flush()
    dataset = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/ERA5_t2m_daily/"+str(model)+"_t2m_"+str(year)+"_daily.nc")
    tmp = dataset['t2m'][:]
    
    tmp_change = np.ma.masked_array(np.zeros((364, lat_dim, lon_dim), dtype=np.float16))
    tmp_change_monthly_up = np.ma.masked_array(np.zeros((12, lat_dim, lon_dim), dtype=np.float16))
    tmp_change_monthly_down = np.ma.masked_array(np.zeros((12, lat_dim, lon_dim), dtype=np.float16))
    for time in range(0, 363):
        tmp_change[time, :] = tmp[time + 1, :] - tmp[time, :]

    sudden_tmp_change_up_10 = np.ma.masked_where(tmp_change.mask, np.where(tmp_change > 10, 1, 0))
    sudden_tmp_change_down_10 = np.ma.masked_where(tmp_change.mask, np.where(tmp_change < -10, 1, 0))
    
    data_area = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/ERA5_area.nc")
    area=data_area['cell_area'][:]
    area_weight=area/np.nanmean(area)

    for month in range(0,12):
        tmp_change_monthly_up[month, :]=np.ma.masked_where(tmp_change[0,:].mask, np.nanmean(sudden_tmp_change_up_10[month_day[month],:],axis=0))
        tmp_change_monthly_down[month, :]=np.ma.masked_where(tmp_change[0,:].mask, np.nanmean(sudden_tmp_change_down_10[month_day[month],:],axis=0))

    write_nc_file(tmp_change_monthly_up*area_weight,tmp_change_monthly_down*area_weight,year)
    
#    print(str(year)+'finish')
#    sys.stdout.flush()
    
    year_index = year - 1850
    return (year_index)


if __name__ == "__main__":
    
    year = list(range(1970,2024))

    #num_processes = min(len(nc_files), multiprocessing.cpu_count()) 
    
    #Number of processes
    num_processes=3
    pool = multiprocessing.Pool(processes=num_processes)
    print("process star")
    sys.stdout.flush() 
    result=pool.map(process_nc_file, year)

    pool.close()
    pool.join()
       


