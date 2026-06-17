import netCDF4 as nc
import numpy as np
import os
import multiprocessing
import sys
import glob
import csv
from scipy.stats import linregress

current_directory = os.path.dirname(os.path.abspath(__file__))

#dataset_ref = nc.Dataset(seamask_file)
#lat_len =len(dataset_ref.dimensions['lat'])
#lon_len =len(dataset_ref.dimensions['lon'])

def cal_trends(freq_data,MAT_data,lat_len,lon_len):

    result_slope=np.zeros((lat_len, lon_len))
    result_r_value=np.zeros((lat_len, lon_len))
    result_p_value=np.zeros((lat_len, lon_len))
    for lat in range(lat_len):
        print(lat)
        sys.stdout.flush()
        for lon in range(lon_len):
            x_values = MAT_data[:, lat, lon]
            y_values = freq_data[:, lat, lon]
    
            slope, intercept, r_value, p_value, std_err = linregress(x_values, y_values)
    
            result_slope[lat, lon]=slope
            result_r_value[lat, lon]=r_value
            result_p_value[lat, lon]=p_value


    return result_slope,result_r_value,result_p_value

def process_nc_file(year):
   
    dataset = nc.Dataset(str(current_directory)+"/ERA5_t2m_daily/ERA5_t2m_"+str(year)+"_daily.nc")
    tmp = dataset['t2m'][:]
    time_len = len(dataset.dimensions['time'])
    lat_len =len(dataset.dimensions['latitude'])
    lon_len =len(dataset.dimensions['longitude'])
    lat=dataset['latitude'][:]

#    data_area = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/ERA5_area.nc")
#    area=data_area['cell_area'][:]
#    area_weight=area/np.nanmean(area)

    tmp_change = np.ma.masked_array(np.zeros((time_len, lat_len, lon_len)))
    for time in range(0, time_len-1):
        tmp_change[time, :] = tmp[time + 1, :] - tmp[time, :]

    sudden_tmp_change_up_10 = np.where(tmp_change > 10, 1, 0)
    sudden_tmp_change_down_10 = np.where(tmp_change < -10, 1, 0)
    sudden_tmp_change_MAT=np.ma.masked_where(tmp[0,:].mask, np.nanmean(tmp,axis=0))
    
    print(str(year)+'finish')
    sys.stdout.flush()
    
    return (year,np.nanmean(sudden_tmp_change_up_10,axis=0),np.nanmean(sudden_tmp_change_down_10,axis=0),sudden_tmp_change_MAT)


if __name__ == "__main__":
    
    year = list(range(1970,2021))

    num_processes=2
    pool = multiprocessing.Pool(processes=num_processes)
    
    result=pool.map(process_nc_file, year)  

    pool.close()
    pool.join()

    dataset_ref = nc.Dataset("/data1/zxy/sudden_temp_change/ERA5_tmp/ERA5_t2m_daily/ERA5_t2m_2023_daily.nc")
    lat_len =len(dataset_ref.dimensions['latitude'])
    lon_len =len(dataset_ref.dimensions['longitude'])
    lat=dataset_ref['latitude'][:]
    ref_t2m=dataset_ref['t2m'][0,:]
     
    seamask=ref_t2m

    freq_up=np.array([item[1] for item in result])
    freq_down=np.array([item[2] for item in result])
    sudden_tmp_change_MAT=np.array([item[3] for item in result])

    
    T_change_up_freq_trend_slpoe,T_change_up_freq_trend_r_value,T_change_up_freq_trend_p_value=cal_trends(freq_up, sudden_tmp_change_MAT, lat_len,lon_len)
    print("T_change_up_freq_trend")

    T_change_down_freq_trend_slpoe,T_change_down_freq_trend_r_value,T_change_down_freq_trend_p_value=cal_trends(freq_down, sudden_tmp_change_MAT, lat_len,lon_len)
    print("T_change_down_freq_trend")   
    

    T_change_up_freq_trend_slpoe  [seamask.mask | (lat < -60)[:, None]]=np.nan
    T_change_up_freq_trend_r_value[seamask.mask | (lat < -60)[:, None]]=np.nan
    T_change_up_freq_trend_p_value[seamask.mask | (lat < -60)[:, None]]=np.nan
    T_change_down_freq_trend_slpoe[seamask.mask | (lat < -60)[:, None]]=np.nan
    T_change_down_freq_trend_r_value[seamask.mask | (lat < -60)[:, None]]=np.nan
    T_change_down_freq_trend_p_value[seamask.mask | (lat < -60)[:, None]]=np.nan


    #===============================write nc file===================================================#
    
    new = nc.Dataset(str(current_directory)+"/ERA5_sudden_T_change_freq_MAT_sensitivity_1970_2020.nc", 'w')

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

    new.variables['lat'][:] = dataset_ref['latitude'][:]
    new.variables['lon'][:] = dataset_ref['longitude'][:]
  
    new.createVariable("T_change_up_freq_trend_slpoe","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_up_freq_trend_slpoe"][:,:]=T_change_up_freq_trend_slpoe
    new.variables["T_change_up_freq_trend_slpoe"].__setattr__("standard_name","T_change_up_freq_trend_slpoe_1970_2020")
    
    new.createVariable("T_change_up_freq_trend_r_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_up_freq_trend_r_value"][:,:]=T_change_up_freq_trend_r_value
    new.variables["T_change_up_freq_trend_r_value"].__setattr__("standard_name","T_change_up_freq_trend_r_value_1970_2020")
    
    new.createVariable("T_change_up_freq_trend_p_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_up_freq_trend_p_value"][:,:]=T_change_up_freq_trend_p_value
    new.variables["T_change_up_freq_trend_p_value"].__setattr__("standard_name","T_change_up_freq_trend_p_value_1970_2020")
    
    new.createVariable("T_change_down_freq_trend_slpoe","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq_trend_slpoe"][:,:]=T_change_down_freq_trend_slpoe
    new.variables["T_change_down_freq_trend_slpoe"].__setattr__("standard_name","T_change_down_freq_trend_slpoe_1970_2020")
    
    new.createVariable("T_change_down_freq_trend_r_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq_trend_r_value"][:,:]=T_change_down_freq_trend_r_value
    new.variables["T_change_down_freq_trend_r_value"].__setattr__("standard_name","T_change_down_freq_trend_r_value_1970_2020")
    
    new.createVariable("T_change_down_freq_trend_p_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq_trend_p_value"][:,:]=T_change_down_freq_trend_p_value
    new.variables["T_change_down_freq_trend_p_value"].__setattr__("standard_name","T_change_down_freq_trend_p_value_1970_2020")




