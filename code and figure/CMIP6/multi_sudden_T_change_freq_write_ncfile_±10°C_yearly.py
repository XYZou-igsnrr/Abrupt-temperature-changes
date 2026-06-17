import netCDF4 as nc
import numpy as np
import os
import multiprocessing
import sys
from scipy.stats import linregress

current_directory = os.path.dirname(os.path.abspath(__file__))
model='ACCESS-ESM1-5'

def process_nc_file(year):
    print(str(year)+'star')
    sys.stdout.flush()
    dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_ssp585/"+str(model)+"/"+str(model)+"_splityear_"+str(year)+".nc")
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
    
    year = list(range(1970,2100))

    #num_processes = min(len(nc_files), multiprocessing.cpu_count()) 
    
    #Number of processes
    num_processes=15
    pool = multiprocessing.Pool(processes=num_processes)
    print("process star")
    sys.stdout.flush() 
    result=pool.map(process_nc_file, year)

    pool.close()
    pool.join()
       
    dataset_ref = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_ssp585/"+str(model)+"/"+str(model)+"_splityear_1850.nc")
    tmp=dataset_ref['tas'][0,:]
    tmp_mask=tmp.mask
    lon_dim = dataset_ref.dimensions['lon'].size
    lat_dim = dataset_ref.dimensions['lat'].size

    year_index=[item[0] for item in result]

    T_change_up_freq_dataset=np.stack([item[1] for item in result])
    T_change_down_freq_dataset=np.stack([item[2] for item in result])
    tmp_mask = np.broadcast_to(tmp_mask, T_change_up_freq_dataset.shape)
    T_change_up_freq_dataset=np.ma.masked_where(tmp_mask,T_change_up_freq_dataset)
    T_change_down_freq_dataset=np.ma.masked_where(tmp_mask,T_change_down_freq_dataset)
    
    new = nc.Dataset(str(current_directory)+"/T_change_freq_"+str(model)+"_yearly_1970-2100.nc", 'w')

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
    new.variables["T_change_up_freq"][:,:]=T_change_up_freq_dataset
    new.variables["T_change_up_freq"].__setattr__("standard_name","T_change_up_freq")
    
    new.createVariable("T_change_down_freq","float32", (u'time', u'lat', u'lon'),fill_value=np.nan )
    new.variables["T_change_down_freq"][:,:]=T_change_down_freq_dataset
    new.variables["T_change_down_freq"].__setattr__("standard_name","T_change_down_freq")
    


