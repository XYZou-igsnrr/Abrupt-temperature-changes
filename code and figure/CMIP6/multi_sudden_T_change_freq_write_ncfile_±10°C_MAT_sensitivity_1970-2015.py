import netCDF4 as nc
import numpy as np
import os
import multiprocessing
import sys
from scipy.stats import linregress
import pymannkendall as mk

current_directory = os.path.dirname(os.path.abspath(__file__))
model='ACCESS-ESM1-5'

data_area = nc.Dataset(str(current_directory)+"/"+str(model)+"_area.nc")
area=data_area['cell_area'][:]
area_weight=area/np.nanmean(area)

def cal_trends(freq_data,MAT_data,lat_len,lon_len):

    result_slope=np.zeros((lat_len, lon_len))
    result_r_value=np.zeros((lat_len, lon_len))
    result_p_value=np.zeros((lat_len, lon_len))
    for lat in range(lat_len):
#        print(lat)
        for lon in range(lon_len):
            x_values = MAT_data[:, lat, lon]
            y_values = freq_data[:, lat, lon]
    
            slope, intercept, r_value, p_value, std_err = linregress(x_values, y_values)
    
            result_slope[lat, lon]=slope
            result_r_value[lat, lon]=r_value
            result_p_value[lat, lon]=p_value


    return result_slope,result_r_value,result_p_value   



def process_nc_file(year):
    print(str(year)+'star')
    sys.stdout.flush()
    dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/"+str(model)+"_splityear_"+str(year)+".nc")
    tmp = dataset['tas'][:]
    lon_dim = dataset.dimensions['lon'].size
    lat_dim = dataset.dimensions['lat'].size
    
    tmp_change = np.ma.masked_array(np.zeros((363, lat_dim, lon_dim), dtype=np.float16))
    for time in range(0, 363):
        tmp_change[time, :] = tmp[time + 1, :] - tmp[time, :]

    sudden_tmp_change_up_10 = np.where(tmp_change > 10, 1, 0)
    sudden_tmp_change_down_10 = np.where(tmp_change < -10, 1, 0)
    sudden_tmp_change_MAT=np.ma.masked_where(tmp[0,:].mask, np.nanmean(tmp,axis=0))
    
#    print(str(year)+'finish')
#    sys.stdout.flush()
    
    year_index = year
    return (year_index,np.nanmean(sudden_tmp_change_up_10,axis=0)*area_weight,np.nanmean(sudden_tmp_change_down_10,axis=0)*area_weight,sudden_tmp_change_MAT)


if __name__ == "__main__":
    
    year = list(range(1970,2015))

    #num_processes = min(len(nc_files), multiprocessing.cpu_count()) 
    
    #Number of processes
    num_processes=15
    pool = multiprocessing.Pool(processes=num_processes)
    print("process star")
    sys.stdout.flush() 
    result=pool.map(process_nc_file, year)

    pool.close()
    pool.join()
       
    dataset_ref = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/"+str(model)+"/"+str(model)+"_splityear_seamask.nc")
    tmp=dataset_ref['topo'][:]
    tmp_mask=tmp.mask
    lon_dim = dataset_ref.dimensions['lon'].size
    lat_dim = dataset_ref.dimensions['lat'].size
    lat_len =len(dataset_ref.dimensions['lat'])
    lon_len =len(dataset_ref.dimensions['lon'])
    lat=dataset_ref['lat'][:]

    freq_up=np.array([item[1] for item in result])
    freq_down=np.array([item[2] for item in result])
    sudden_tmp_change_MAT=np.array([item[3] for item in result])

    T_change_up_freq_trend_slpoe,T_change_up_freq_trend_r_value,T_change_up_freq_trend_p_value=cal_trends(freq_up, sudden_tmp_change_MAT, lat_len,lon_len)
    print("T_change_up_freq_trend")

    T_change_down_freq_trend_slpoe,T_change_down_freq_trend_r_value,T_change_down_freq_trend_p_value=cal_trends(freq_down, sudden_tmp_change_MAT, lat_len,lon_len)
    print("T_change_down_freq_trend") 

    T_change_up_freq_trend_slpoe[tmp.mask | (lat < -60)[:, None]]=np.nan
    T_change_up_freq_trend_r_value[tmp.mask | (lat < -60)[:, None]]=np.nan
    T_change_up_freq_trend_p_value[tmp.mask | (lat < -60)[:, None]]=np.nan
    T_change_down_freq_trend_slpoe[tmp.mask | (lat < -60)[:, None]]=np.nan
    T_change_down_freq_trend_r_value[tmp.mask | (lat < -60)[:, None]]=np.nan
    T_change_down_freq_trend_p_value[tmp.mask | (lat < -60)[:, None]]=np.nan
  
    
    new = nc.Dataset(str(current_directory)+"/T_change_freq_"+str(model)+"_MAT_sensitivity_1970-2015.nc", 'w')

    new.createDimension("lat", lat_dim)
    new.createDimension("lon", lon_dim)

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
    
    new.createVariable("T_change_up_freq_trend_slpoe","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_up_freq_trend_slpoe"][:,:]=T_change_up_freq_trend_slpoe
    new.variables["T_change_up_freq_trend_slpoe"].__setattr__("standard_name","T_change_up_freq_trend_slpoe_1970-2020")
    
    new.createVariable("T_change_up_freq_trend_r_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_up_freq_trend_r_value"][:,:]=T_change_up_freq_trend_r_value
    new.variables["T_change_up_freq_trend_r_value"].__setattr__("standard_name","T_change_up_freq_trend_r_value_1970-2020")
    
    new.createVariable("T_change_up_freq_trend_p_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_up_freq_trend_p_value"][:,:]=T_change_up_freq_trend_p_value
    new.variables["T_change_up_freq_trend_p_value"].__setattr__("standard_name","T_change_up_freq_trend_p_value_1970-2020")
    
    new.createVariable("T_change_down_freq_trend_slpoe","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq_trend_slpoe"][:,:]=T_change_down_freq_trend_slpoe
    new.variables["T_change_down_freq_trend_slpoe"].__setattr__("standard_name","T_change_down_freq_trend_slpoe_1970-2020")
    
    new.createVariable("T_change_down_freq_trend_r_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq_trend_r_value"][:,:]=T_change_down_freq_trend_r_value
    new.variables["T_change_down_freq_trend_r_value"].__setattr__("standard_name","T_change_down_freq_trend_r_value_1970-2020")
    
    new.createVariable("T_change_down_freq_trend_p_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq_trend_p_value"][:,:]=T_change_down_freq_trend_p_value
    new.variables["T_change_down_freq_trend_p_value"].__setattr__("standard_name","T_change_down_freq_trend_p_value_1970-2020") 

