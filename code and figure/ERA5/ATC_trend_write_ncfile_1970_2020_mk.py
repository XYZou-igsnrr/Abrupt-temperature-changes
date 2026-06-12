import netCDF4 as nc
import numpy as np
import os
import multiprocessing
import sys
import glob
import csv
from scipy.stats import linregress
import pymannkendall as mk
import sys

current_directory = os.path.dirname(os.path.abspath(__file__))

#dataset_ref = nc.Dataset(seamask_file)
#lat_len =len(dataset_ref.dimensions['lat'])
#lon_len =len(dataset_ref.dimensions['lon'])

def compute_trend(series):
    try:
        result = mk.original_test(series)
        return (result.slope, result.p)
    except:
        return (np.nan, np.nan)

def cal_trends(freq_data,lat_len,lon_len):

    result_slope=np.full((lat_len, lon_len), np.nan)
    result_p_value=np.full((lat_len, lon_len), np.nan)

    data_2d = freq_data.reshape(freq_data.shape[0], -1)
    valid_cols = ~np.isnan(data_2d).any(axis=0)
    valid_idx = np.where(valid_cols)[0]

    print('star mk')
    pool = multiprocessing.Pool(processes=100)
    #results = pool.map(compute_trend, data_2d[:, valid_idx].T)
    results = []
    for i, result in enumerate(pool.imap(compute_trend, data_2d[:, valid_idx].T)):
        results.append(result)
        if (i + 1) % 100000 == 0:
            print(i)
            sys.stdout.flush()
    pool.close()
    pool.join()

    print('fill result')
    for idx, (slope, p_val) in zip(valid_idx, results):
        result_slope[idx // lon_len, idx % lon_len] = slope
        result_p_value[idx // lon_len, idx % lon_len] = p_val

    return result_slope,result_p_value

if __name__ == "__main__":
    
    dataset_ref = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/LFCA/T_change_freq_ERA5_yearly_1970-2020.nc")
    lat_len =len(dataset_ref.dimensions['lat'])
    lon_len =len(dataset_ref.dimensions['lon'])
    lat=dataset_ref['lat'][:]
    ref_t2m=dataset_ref['T_change_up_freq'][0,:]
     
    seamask=ref_t2m

    T_change_up_freq_dataset=dataset_ref['T_change_up_freq'][:]
    T_change_down_freq_dataset=dataset_ref['T_change_down_freq'][:]
    tmp_mask = np.broadcast_to(seamask.mask, T_change_up_freq_dataset.shape)
    
    T_change_up_freq_dataset[:,(lat<-60),:]=np.nan
    T_change_down_freq_dataset[:,(lat<-60),:]=np.nan    
    
    T_change_up_freq_trend_slope,T_change_up_freq_trend_p_value=cal_trends(T_change_up_freq_dataset, lat_len,lon_len)
    print("T_change_up_freq_trend")

    T_change_down_freq_trend_slope,T_change_down_freq_trend_p_value=cal_trends(T_change_down_freq_dataset, lat_len,lon_len)
    print("T_change_down_freq_trend")

    ATC=np.nansum([T_change_down_freq_dataset, T_change_up_freq_dataset], axis=0)
    ATC=np.ma.masked_where(tmp_mask,ATC)
    
    ATC_trend_slope,ATC_trend_p_value=cal_trends(ATC, lat_len,lon_len)
    print("ATC_trend")

    ATC_trend_slope[seamask.mask | (lat < -60)[:, None]]=np.nan
    ATC_trend_p_value[seamask.mask | (lat < -60)[:, None]]=np.nan


    #===============================write nc file===================================================#
    
    new = nc.Dataset(str(current_directory)+"/ERA5_ATC_trend_1970_2020_mk.nc", 'w')

    new.createDimension("lat", lat_len)
    new.createDimension("lon", lon_len)

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



