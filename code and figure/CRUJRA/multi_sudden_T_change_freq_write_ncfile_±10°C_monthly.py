# srun --nodelist=node01 --cpus-per-task=40

import netCDF4 as nc
import numpy as np
import os
import multiprocessing
import sys
from scipy.stats import linregress

current_directory = os.path.dirname(os.path.abspath(__file__))


T_change_up_freq_years = np.ma.masked_array(np.zeros((120, 360, 720)))
T_change_down_freq_years = np.ma.masked_array(np.zeros((120, 360, 720)))


month_4hourly =[range(0,123),range(124,235),
                range(236,359),range(360,479),
                range(480,603),range(604,719),
                range(720,843),range(844,967),
                range(968,1087),range(1088,1211),
                range(1212,1327),range(1328,1456),#温度突变是两天差值，实际只有364个时间点，少的时间点放在12月
              ]


def write_nc_file(freq_up,freq_down,year):

    dataset_ref = nc.Dataset(f"/data4/share/CRUJRA/v2.2/crujra.v2.2.5d.tmp.2020.365d.noc.nc")

    new = nc.Dataset(str(current_directory)+"/monthly/T_change_freq_monthly_"+str(year)+".nc", 'w')

    new.createDimension("lat", 360)
    new.createDimension("lon", 720)
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
    new.variables['time'].__setattr__("units", "months since 1900-01-01 00:00:00")
    new.variables['time'].__setattr__("calendar", "gregorian")

    new.variables['lat'][:] = dataset_ref['lat'][:]
    new.variables['lon'][:] = dataset_ref['lon'][:]

    months_since_base = [(year - 1900) * 12 + m for m in range(0, 12)]
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
    dataset = nc.Dataset("/data4/share/CRUJRA/v2.2/crujra.v2.2.5d.tmp."+str(year)+".365d.noc.nc")
    tmp = dataset['tmp'][:]
    
    tmp_change = np.ma.masked_array(np.zeros((1456, 360, 720), dtype=np.float16))
    tmp_change_monthly_up = np.ma.masked_array(np.zeros((12, 360, 720), dtype=np.float16))
    tmp_change_monthly_down = np.ma.masked_array(np.zeros((12, 360, 720), dtype=np.float16))
    for time in range(0, 1456):
        tmp_change[time, :] = tmp[time + 4, :] - tmp[time, :]

    sudden_tmp_change_up_10 = np.ma.masked_where(tmp_change.mask, np.where(tmp_change > 10, 1, 0))
    sudden_tmp_change_down_10 = np.ma.masked_where(tmp_change.mask, np.where(tmp_change < -10, 1, 0))
    
#    data_area = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/CRUJRA_area.nc")
#    area=data_area['cell_area'][:]
#    area_weight=area/np.nanmean(area)    

    for month in range(0,12):
        tmp_change_monthly_up[month, :]=np.ma.masked_where(tmp_change[0,:].mask, np.nanmean(sudden_tmp_change_up_10[month_4hourly[month],:],axis=0))
        tmp_change_monthly_down[month, :]=np.ma.masked_where(tmp_change[0,:].mask, np.nanmean(sudden_tmp_change_down_10[month_4hourly[month],:],axis=0))

    write_nc_file(tmp_change_monthly_up,tmp_change_monthly_down,year)
    
#    print(str(year)+'finish')
#    sys.stdout.flush()
    
    year_index = year - 1901
    return (year_index)


if __name__ == "__main__":
    
    year = list(range(1901,2021))

    #num_processes = min(len(nc_files), multiprocessing.cpu_count()) 
    
    #Number of processes
    num_processes=40
    pool = multiprocessing.Pool(processes=num_processes)
    print("process star")
    sys.stdout.flush() 
    result=pool.map(process_nc_file, year)

    pool.close()
    pool.join()
       


