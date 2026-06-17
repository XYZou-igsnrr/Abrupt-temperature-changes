import netCDF4 as nc
import numpy as np
import os
import multiprocessing
import sys
from scipy.stats import linregress
import pymannkendall as mk

current_directory = os.path.dirname(os.path.abspath(__file__))


#T_change_up_freq_years = np.ma.masked_array(np.zeros((120, 360, 720)))
#T_change_down_freq_years = np.ma.masked_array(np.zeros((120, 360, 720)))

def compute_trend(series):
    try:
        result = mk.original_test(series)
        return (result.slope, result.p)
    except:
        return (np.nan, np.nan)

def cal_trends(freq_data,lat_len,lon_len):

    result_slope=np.full((lat_len, lon_len), np.nan)
    result_p_value=np.full((lat_len, lon_len), np.nan)

    valid_positions = []
    valid_series = []

    for lat in range(lat_len):
        print(lat)
        for lon in range(lon_len):
            y_values = freq_data[:, lat, lon]
            if not np.any(np.isnan(y_values)):
                valid_positions.append((lat, lon))
                valid_series.append(y_values)
    #mk_cal
    print('star mk')
    pool = multiprocessing.Pool(processes=50)
    results = pool.map(compute_trend, valid_series)
    pool.close()
    pool.join()
    print('finish mk')

    for (lat, lon), (slope, p_val) in zip(valid_positions, results):
        result_slope[lat, lon] = slope
        result_p_value[lat, lon] = p_val

    return result_slope,result_p_value

def process_nc_file(year):
    print(str(year)+'star')
    sys.stdout.flush()
    dataset = nc.Dataset("/data4/share/CRUJRA/v2.2/crujra.v2.2.5d.tmp."+str(year)+".365d.noc.nc")
    tmp = dataset['tmp'][:]

#    data_area = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/CRUJRA_area.nc")
#    area=data_area['cell_area'][:]
#    area_weight=area/np.nanmean(area)
    
    tmp_change = np.ma.masked_array(np.zeros((1456, 360, 720), dtype=np.float16))
    for time in range(0, 1456):
        tmp_change[time, :] = tmp[time + 4, :] - tmp[time, :]

    sudden_tmp_change_up_10 = np.ma.masked_where(tmp_change.mask, np.where(tmp_change > 10, 1, 0))
    sudden_tmp_change_down_10 = np.ma.masked_where(tmp_change.mask, np.where(tmp_change < -10, 1, 0))
    
#    print(str(year)+'finish')
#    sys.stdout.flush()
    
    year_index = year
    return (year_index,np.nanmean(sudden_tmp_change_up_10,axis=0),np.nanmean(sudden_tmp_change_down_10,axis=0))


if __name__ == "__main__":
    
    year = list(range(1970,2021))

    #num_processes = min(len(nc_files), multiprocessing.cpu_count()) 
    
    #Number of processes
    num_processes=20
    pool = multiprocessing.Pool(processes=num_processes)
    print("process star")
    sys.stdout.flush() 
    result=pool.map(process_nc_file, year)

    pool.close()
    pool.join()
       
    dataset_ref = nc.Dataset(f"/data4/share/CRUJRA/v2.2/crujra.v2.2.5d.tmp.2020.365d.noc.nc")
    tmp=dataset_ref['tmp'][0,:]
    lat=dataset_ref['lat'][:]
    lon_dim = dataset_ref.dimensions['lon'].size
    lat_dim = dataset_ref.dimensions['lat'].size
    tmp_mask=tmp.mask
    print(tmp)
    
    T_change_up_freq_dataset=np.stack([item[1] for item in result])
    T_change_down_freq_dataset=np.stack([item[2] for item in result])
    tmp_mask = np.broadcast_to(tmp_mask, T_change_up_freq_dataset.shape)
    T_change_up_freq_dataset=np.ma.masked_where(tmp_mask,T_change_up_freq_dataset)
    T_change_down_freq_dataset=np.ma.masked_where(tmp_mask,T_change_down_freq_dataset)

    T_change_up_freq_trend_slope,T_change_up_freq_trend_p_value=cal_trends(T_change_up_freq_dataset, lat_dim,lon_dim)
    print("T_change_up_freq_trend")

    T_change_down_freq_trend_slope,T_change_down_freq_trend_p_value=cal_trends(T_change_down_freq_dataset, lat_dim,lon_dim)
    print("T_change_down_freq_trend")
    
    ATC=np.nansum([T_change_down_freq_dataset, T_change_up_freq_dataset], axis=0)
    ATC=np.ma.masked_where(tmp_mask,ATC)
    
    ATC_trend_slope,ATC_trend_p_value=cal_trends(ATC, lat_dim,lon_dim)
    print("ATC_trend")   
    
    ATC_trend_slope[tmp.mask | (lat < -60)[:, None]]=np.nan
    ATC_trend_p_value[tmp.mask | (lat < -60)[:, None]]=np.nan 
    
    
     
    T_change_up_freq = np.ma.masked_where(tmp.mask,np.nanmean([item[1] for item in result], axis=0))
    T_change_down_freq = np.ma.masked_where(tmp.mask,np.nanmean([item[2] for item in result], axis=0))

    new = nc.Dataset(f"{current_directory}/ATC_trend_spatial_±10°C_1970_2020_MK.nc", 'w')

    new.createDimension("lat", 360)
    new.createDimension("lon", 720)

    new.createVariable("lat", "float64", ("lat",))
    new.createVariable("lon", "float64", ("lon",))

    new.variables['lat'].__setattr__("long_name", "Latitude")
    new.variables['lat'].__setattr__("standard_name", "latitude")
    new.variables['lat'].__setattr__("axis", "Y")
    new.variables['lat'].__setattr__("units", "degrees_north")

    new.variables['lon'].__setattr__("long_name", "Longitude")
    new.variables['lon'].__setattr__("standard_name", "longitude")
    new.variables['lon'].__setattr__("axis", "X")
    new.variables['lon'].__setattr__("units", "degrees_east")

    new.variables['lat'][:] = dataset_ref['lat'][:]
    new.variables['lon'][:] = dataset_ref['lon'][:]

    new.createVariable("T_change_up_freq", "float32", ("lat", "lon"), fill_value=np.nan)
    new.variables["T_change_up_freq"][:, :] = T_change_up_freq
    new.variables["T_change_up_freq"].__setattr__("standard_name", "T_change_up_freq")

    new.createVariable("T_change_down_freq", "float32", ("lat", "lon"), fill_value=np.nan)
    new.variables["T_change_down_freq"][:, :] = T_change_down_freq
    new.variables["T_change_down_freq"].__setattr__("standard_name", "T_change_down_freq")

    new.createVariable("T_change_up_freq_trend_slope","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_up_freq_trend_slope"][:,:]=T_change_up_freq_trend_slope
    new.variables["T_change_up_freq_trend_slope"].__setattr__("standard_name","T_change_up_freq_trend_slope")
    
    new.createVariable("T_change_up_freq_trend_p_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_up_freq_trend_p_value"][:,:]=T_change_up_freq_trend_p_value
    new.variables["T_change_up_freq_trend_p_value"].__setattr__("standard_name","T_change_up_freq_trend_p_value")
    
    new.createVariable("T_change_down_freq_trend_slope","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq_trend_slope"][:,:]=T_change_down_freq_trend_slope
    new.variables["T_change_down_freq_trend_slope"].__setattr__("standard_name","T_change_down_freq_trend_slope")
    
    new.createVariable("T_change_down_freq_trend_p_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq_trend_p_value"][:,:]=T_change_down_freq_trend_p_value
    new.variables["T_change_down_freq_trend_p_value"].__setattr__("standard_name","T_change_down_freq_trend_p_value")
    
    new.createVariable("ATC_trend_slope","float32", ( u'lat', u'lon'),fill_value=np.nan )
    new.variables["ATC_trend_slope"][:]=ATC_trend_slope
    new.variables["ATC_trend_slope"].__setattr__("standard_name","ATC_trend_slope")

    new.createVariable("ATC_trend_p_value","float32", ( u'lat', u'lon'),fill_value=np.nan )
    new.variables["ATC_trend_p_value"][:]=ATC_trend_p_value
    new.variables["ATC_trend_p_value"].__setattr__("standard_name","ATC_trend_p_value")

