import netCDF4 as nc
import numpy as np
import os
import multiprocessing
import sys
from scipy.stats import linregress

current_directory = os.path.dirname(os.path.abspath(__file__))


#T_change_up_freq_years = np.ma.masked_array(np.zeros((120, 360, 720)))
#T_change_down_freq_years = np.ma.masked_array(np.zeros((120, 360, 720)))

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
    dataset = nc.Dataset("//data4/share/CRUJRA/v2.2/crujra.v2.2.5d.tmp."+str(year)+".365d.noc.nc")
    tmp = dataset['tmp'][:]

#    data_area = nc.Dataset("/data1/zxy/sudden_temp_change/CRU_JAR_tmp/CRUJRA_area.nc")
#    area=data_area['cell_area'][:]
#    area_weight=area/np.nanmean(area)
    
    tmp_change = np.ma.masked_array(np.zeros((1456, 360, 720), dtype=np.float16))
    for time in range(0, 1456):
        tmp_change[time, :] = tmp[time + 4, :] - tmp[time, :]

    sudden_tmp_change_up_10 = np.ma.masked_where(tmp_change.mask, np.where(tmp_change > 10, 1, 0))
    sudden_tmp_change_down_10 = np.ma.masked_where(tmp_change.mask, np.where(tmp_change < -10, 1, 0))
    sudden_tmp_change_MAT=np.ma.masked_where(tmp[0,:].mask, np.nanmean(tmp,axis=0))
    
#    print(sudden_tmp_change_MAT.shape)
#    print(np.nanmean(sudden_tmp_change_down_10,axis=0).shape)
#    print(str(year)+'finish')
#    sys.stdout.flush()
    
    year_index = year - 1901
    return (year_index,np.nanmean(sudden_tmp_change_up_10,axis=0),np.nanmean(sudden_tmp_change_down_10,axis=0),sudden_tmp_change_MAT)


if __name__ == "__main__":
    
    year = list(range(1970,2021))

    #num_processes = min(len(nc_files), multiprocessing.cpu_count()) 
    
    #Number of processes
    num_processes=10
    pool = multiprocessing.Pool(processes=num_processes)
    print("process star")
    sys.stdout.flush() 
    result=pool.map(process_nc_file, year)

    pool.close()
    pool.join()
       
    dataset_ref = nc.Dataset(f"/data4/share/CRUJRA/v2.2/crujra.v2.2.5d.tmp.2020.365d.noc.nc")
    tmp=dataset_ref['tmp'][0,:]
    print(tmp)
    freq_up=np.array([item[1] for item in result])
    freq_down=np.array([item[2] for item in result])
    sudden_tmp_change_MAT=np.array([item[3] for item in result])

    
    T_change_up_freq_trend_slpoe,T_change_up_freq_trend_r_value,T_change_up_freq_trend_p_value=cal_trends(freq_up, sudden_tmp_change_MAT, 360,720)
    print("T_change_up_freq_trend")

    T_change_down_freq_trend_slpoe,T_change_down_freq_trend_r_value,T_change_down_freq_trend_p_value=cal_trends(freq_down, sudden_tmp_change_MAT, 360,720)
    print("T_change_down_freq_trend")
    

    new = nc.Dataset(f"{current_directory}/CRUJRA_sudden_T_change_freq_MAT_sensitivity_1970_2020.nc", 'w')

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

    new.createVariable("T_change_up_freq_trend_slpoe","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_up_freq_trend_slpoe"][:,:]=T_change_up_freq_trend_slpoe
    new.variables["T_change_up_freq_trend_slpoe"].__setattr__("standard_name","T_change_up_freq_trend_slpoe")
    
    new.createVariable("T_change_up_freq_trend_r_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_up_freq_trend_r_value"][:,:]=T_change_up_freq_trend_r_value
    new.variables["T_change_up_freq_trend_r_value"].__setattr__("standard_name","T_change_up_freq_trend_r_value")
    
    new.createVariable("T_change_up_freq_trend_p_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_up_freq_trend_p_value"][:,:]=T_change_up_freq_trend_p_value
    new.variables["T_change_up_freq_trend_p_value"].__setattr__("standard_name","T_change_up_freq_trend_p_value")
    
    new.createVariable("T_change_down_freq_trend_slpoe","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq_trend_slpoe"][:,:]=T_change_down_freq_trend_slpoe
    new.variables["T_change_down_freq_trend_slpoe"].__setattr__("standard_name","T_change_down_freq_trend_slpoe")
    
    new.createVariable("T_change_down_freq_trend_r_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq_trend_r_value"][:,:]=T_change_down_freq_trend_r_value
    new.variables["T_change_down_freq_trend_r_value"].__setattr__("standard_name","T_change_down_freq_trend_r_value")
    
    new.createVariable("T_change_down_freq_trend_p_value","float32", (u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq_trend_p_value"][:,:]=T_change_down_freq_trend_p_value
    new.variables["T_change_down_freq_trend_p_value"].__setattr__("standard_name","T_change_down_freq_trend_p_value")

