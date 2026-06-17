import netCDF4 as nc
import numpy as np
import os
import multiprocessing
import sys
from scipy.stats import linregress
import pymannkendall as mk
from functools import partial
import multiprocessing as mp

current_directory = os.path.dirname(os.path.abspath(__file__))
model='ACCESS-ESM1-5'

data_area = nc.Dataset(str(current_directory)+"/"+str(model)+"_area.nc")
area=data_area['cell_area'][:]
area_weight=area/np.nanmean(area)

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
    pool = mp.Pool(processes=50)
    results = pool.map(compute_trend, valid_series)
    pool.close()
    pool.join()
    print('finish mk')

    for (lat, lon), (slope, p_val) in zip(valid_positions, results):
        result_slope[lat, lon] = slope
        result_p_value[lat, lon] = p_val
#    for lat in range(lat_len):
#        print(lat)
#        for lon in range(lon_len):
#            y_values = freq_data[:, lat, lon]
#            if np.any(np.isnan(y_values)):
#                continue
#            else:
#                result_slope[lat, lon]=mk.original_test(y_values).slope
#                result_p_value[lat, lon]=mk.original_test(y_values).p


    return result_slope,result_p_value


def process_nc_file(year):
    print(str(year)+'start')
    sys.stdout.flush()
    dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/"+str(model)+"_splityear_"+str(year)+".nc")
    tmp = dataset['tas'][:]
    lon_dim = dataset.dimensions['lon'].size
    lat_dim = dataset.dimensions['lat'].size
    
    tmp_change = np.ma.masked_array(np.zeros((363, lat_dim, lon_dim), dtype=np.float16))
    for time in range(0, 363):
        tmp_change[time, :] = tmp[time + 1, :] - tmp[time, :]

    sudden_tmp_change_up_10 = np.ma.masked_where(tmp_change.mask, np.where(tmp_change > 10, 1, 0))
    sudden_tmp_change_down_10 = np.ma.masked_where(tmp_change.mask, np.where(tmp_change < -10, 1, 0))
    
#    print(str(year)+'finish')
#    sys.stdout.flush()
    
    year_index = year
    return (year_index,np.nanmean(sudden_tmp_change_up_10,axis=0),np.nanmean(sudden_tmp_change_down_10,axis=0))


if __name__ == "__main__":
    
    year = list(range(1970,2015))

    #num_processes = min(len(nc_files), multiprocessing.cpu_count()) 
    
    #Number of processes
    num_processes=15
    pool = multiprocessing.Pool(processes=num_processes)
    print("process start")
    sys.stdout.flush() 
    result=pool.map(process_nc_file, year)

    pool.close()
    pool.join()
       
    dataset_ref = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/"+str(model)+"_splityear_seamask.nc")
    tmp=dataset_ref['topo'][:]
    tmp_mask=tmp.mask
    lon_dim = dataset_ref.dimensions['lon'].size
    lat_dim = dataset_ref.dimensions['lat'].size
    lat=dataset_ref['lat'][:]

    year_index=[item[0] for item in result]

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
    print("ATC")

    T_change_up_freq_trend_slope[tmp.mask | (lat < -60)[:, None]]=np.nan
    T_change_up_freq_trend_p_value[tmp.mask | (lat < -60)[:, None]]=np.nan
    T_change_down_freq_trend_slope[tmp.mask | (lat < -60)[:, None]]=np.nan
    T_change_down_freq_trend_p_value[tmp.mask | (lat < -60)[:, None]]=np.nan

    ATC_trend_slope[tmp.mask | (lat < -60)[:, None]]=np.nan
    ATC_trend_p_value[tmp.mask | (lat < -60)[:, None]]=np.nan


    new = nc.Dataset(str(current_directory)+"/T_change_freq_"+str(model)+"_yearly_1970-2015_mk.nc", 'w')

    new.createDimension("lat", lat_dim)
    new.createDimension("lon", lon_dim)
    new.createDimension("time", len(year))

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
    
    new.variables['time'].__setattr__("long_name", "year")

    new.variables['lat'][:] = dataset_ref['lat'][:]
    new.variables['lon'][:] = dataset_ref['lon'][:]
    new.variables['time'][:] = year_index

    new.createVariable("T_change_up_freq","float32", (u'time', u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_up_freq"][:]=T_change_up_freq_dataset
    new.variables["T_change_up_freq"].__setattr__("standard_name","T_change_up_freq")
    
    new.createVariable("T_change_down_freq","float32", (u'time', u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq"][:]=T_change_down_freq_dataset
    new.variables["T_change_down_freq"].__setattr__("standard_name","T_change_down_freq")
    
    new.createVariable("T_change_up_freq_trend_slope","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_up_freq_trend_slope"][:,:]=T_change_up_freq_trend_slope
    new.variables["T_change_up_freq_trend_slope"].__setattr__("standard_name","T_change_up_freq_trend_slope_1970-2020")
    
    
    new.createVariable("T_change_up_freq_trend_p_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_up_freq_trend_p_value"][:,:]=T_change_up_freq_trend_p_value
    new.variables["T_change_up_freq_trend_p_value"].__setattr__("standard_name","T_change_up_freq_trend_p_value_1970-2020")
    
    new.createVariable("T_change_down_freq_trend_slope","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq_trend_slope"][:,:]=T_change_down_freq_trend_slope
    new.variables["T_change_down_freq_trend_slope"].__setattr__("standard_name","T_change_down_freq_trend_slope_1970-2020")
    
    new.createVariable("T_change_down_freq_trend_p_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq_trend_p_value"][:,:]=T_change_down_freq_trend_p_value
    new.variables["T_change_down_freq_trend_p_value"].__setattr__("standard_name","T_change_down_freq_trend_p_value_1970-2020") 

    new.createVariable("ATC","float32", (u'time', u'lat', u'lon'),fill_value=np.nan )
    new.variables["ATC"][:]=ATC
    new.variables["ATC"].__setattr__("standard_name","ATC_freq: ATCc+ATCw")

    new.createVariable("ATC_trend_slope","float32", ( u'lat', u'lon'),fill_value=np.nan )
    new.variables["ATC_trend_slope"][:]=ATC_trend_slope
    new.variables["ATC_trend_slope"].__setattr__("standard_name","ATC_trend_slope")

    new.createVariable("ATC_trend_p_value","float32", ( u'lat', u'lon'),fill_value=np.nan )
    new.variables["ATC_trend_p_value"][:]=ATC_trend_p_value
    new.variables["ATC_trend_p_value"].__setattr__("standard_name","ATC_trend_p_value")

