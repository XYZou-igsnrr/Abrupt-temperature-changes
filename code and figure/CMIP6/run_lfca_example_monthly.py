#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 17:58:52 2018
%% LFCA  Truncated Low-Frequency Component Analysis
%     [LFCs,LFPs,WEIGHTS,R,PVAR,PCS,EOF,N,PVAR_SLOW,PVAR_LFC,R_EOFS,PVAR_SLOW_EOFS] = lfca(X,CUTOFF,TRUNCATION,SCALE,COVTOT)
%     performs low-frequency component analysis (LFCA) on the data in
%     matrix X based on a the ratio of low-pass filtered to unfiltered
%     variance, with a low-pass filter defined by CUTOFF (in # timesteps).
%     Another type of filter can be substituted for the Lanczos lowpass
%     filter in the code below.

%% INPUT
%     X is a 2D data matrix with time variantions along the first dimension
%     and spatial variations along the second dimension
%
%     CUTOFF is the lowpass cutoff for the LFCA in number of timesteps
%
%     TRUNCATION is the number of principal components / EOFs to include in
%     the LFCA
%
%     SCALE (optional) a scale vector, which for geospatial data should be
%     equal to the square root of grid cell area. The default value is one
%     for all grid points.
%
%     COVTOT (optional) the covariance matrix associated with the data in
%     X. If not specified, COVTOT will be computed from X.

%% OUTPUT

%     WEIGHTS is a matrix containing the canonical weight vectors as
%     columns. LFPs is a matrix containing the dual vectors of the
%     canonical weight vectors as rows. These are the so-called low-
%     frequency patterns (LFPs). R is a vector measuring the ratio of
%     low-pass filtered to total variance for each low-frequency component
%
%     PVAR is the percentage of total sample variation accounted for
%     by each of the EOFs. PCS is a matrix containing the principal
%     component time series as columns. EOF is a matrix containing the
%     EOFs, the principal component patterns, as rows. The scalar N
%     is the rank at which the PCA was truncated.
%
%     R is a vector containing the ratio of low-frequency to
%     total variance of each LFC.
%
%     PVAR_SLOW is a vector of the low-frequency variance associated with
%     each LFC as a fraction of the total low-frequency variance. Note that
%     the LFPs are not orthogonal, so these values need not add to the
%     total low-frequency variance in the first N principal components.
%
%     PVAR_LFC is a vector of the variance associated with
%     each LFC as a fraction of the total variance. Note that
%     the LFPs are not orthogonal, so these values need not add to the
%     total variance in the first N principal components.
%
%     R_EOFS, PVAR_SLOW_EOFS, and PVAR are equivalent to R, PVAR_SLOW,
%     and PVAR_LFC respectively, but for the original EOFs.
@author: Zhaoyi.Shen
"""

import sys
sys.path.append('/data1/zxy/sudden_temp_change/CRU_JAR_tmp/LFCA/')
from signal_processing import lfca
import numpy as np
import scipy as sp
from scipy import io
from matplotlib import pyplot as plt
import netCDF4 as nc
import os

dataset_ref = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/ACCESS-ESM1-5/ACCESS-ESM1-5_splityear_seamask.nc")
seamask=dataset_ref['topo'][:]
seamask_lat=dataset_ref['lat'][:]
seamask=np.transpose(seamask, (1, 0))

dataset = nc.Dataset("/data1/zxy/sudden_temp_change/CMIP6_daily_tas/ACCESS-ESM1-5/LFCA/ATC_monthly/T_change_freq_monthly_ACCESS-ESM1-5_1850-2014.nc")
ATCw=dataset["T_change_up_freq"][1476:,:] #1973-2014
ATCc=dataset["T_change_down_freq"][1476:,:] #1973-2014
print(ATCw.shape)
sys.stdout.flush()
ATCw = np.transpose(ATCw, (2, 1, 0))
ATCc = np.transpose(ATCc, (2, 1, 0))
print(ATCw.shape)
sys.stdout.flush()
lat_axis = dataset['lat'][:]
lon_axis = dataset['lon'][:]

nlon = ATCw.shape[0]
nlat = ATCw.shape[1]
ntime = ATCw.shape[2]


cutoff = 120 #10year time step
truncation = 30 #component 
#%%
ATCw_mean_seasonal_cycle = np.zeros((nlon,nlat,12))
ATCc_mean_seasonal_cycle = np.zeros((nlon,nlat,12))
ATCw_anomalies = np.zeros((nlon,nlat,ntime))
ATCc_anomalies = np.zeros((nlon,nlat,ntime))
for i in range(12):
    print(i)
    sys.stdout.flush()
    ATCw_mean_seasonal_cycle[...,i] = np.nanmean(ATCw[...,i:ntime:12],-1)
    ATCc_mean_seasonal_cycle[...,i] = np.nanmean(ATCc[...,i:ntime:12],-1)
    ATCw_anomalies[...,i:ntime:12] = ATCw[...,i:ntime:12] - ATCw_mean_seasonal_cycle[...,i][...,np.newaxis]
    ATCc_anomalies[...,i:ntime:12] = ATCc[...,i:ntime:12] - ATCc_mean_seasonal_cycle[...,i][...,np.newaxis]
#%%
s = ATCw_anomalies.shape
y, x = np.meshgrid(lat_axis,lon_axis)
area = np.cos(y*np.pi/180.)
area[np.where(np.isnan(np.mean(ATCw_anomalies,-1)))] = 0
area[seamask.mask] = 0
area[:,seamask_lat<-60]=0

order = 'C'
ATCw_x = np.transpose(np.reshape(ATCw_anomalies,(s[0]*s[1],s[2]),order=order))
ATCc_x = np.transpose(np.reshape(ATCc_anomalies,(s[0]*s[1],s[2]),order=order))
print(ATCw_x.shape)
print(ATCc_x.shape)
sys.stdout.flush()

#=============================land mask and area weights===========================#
area_weights = np.transpose(np.reshape(area,(s[0]*s[1],1),order=order))
print(area_weights.shape)
sys.stdout.flush()

icol_ret  = np.where(area_weights!=0)
icol_disc = np.where(area_weights==0)
ATCw_x = ATCw_x[:,icol_ret[1]]
ATCc_x = ATCc_x[:,icol_ret[1]]
print(ATCw_x.shape)
print(ATCc_x.shape)
sys.stdout.flush()
area_weights = area_weights[:,icol_ret[1]]
normvec = np.transpose(area_weights)/np.sum(area_weights)
scale = np.sqrt(normvec)

#======================================star lfcs=====================================#
#%%
print("star lfcs")
sys.stdout.flush()
ATCw_lfcs, ATCw_lfps, ATCw_weights, ATCw_r, ATCw_pvar, ATCw_pcs, ATCw_eofs, ATCw_ntr, ATCw_pvar_slow, ATCw_pvar_lfc, ATCw_r_eofs, ATCw_pvar_slow_eofs = lfca(ATCw_x, cutoff, truncation, scale)
ATCc_lfcs, ATCc_lfps, ATCc_weights, ATCc_r, ATCc_pvar, ATCc_pcs, ATCc_eofs, ATCc_ntr, ATCc_pvar_slow, ATCc_pvar_lfc, ATCc_r_eofs, ATCc_pvar_slow_eofs = lfca(ATCc_x, cutoff, truncation, scale)
#lfcs(time,comp)
#lfps(comp,land of latxlon)
#weights(land of latxlon, comp)
#r(comp,)
"""
print("lfcs:"+str(type(lfcs)))
try: print(lfcs.shape)
except Exception: print("error: lfcs.shape")
print("lfps:"+str(type(lfps)))
try: print(lfps.shape)
except Exception: print("error: lfps.shape")
print("weights:"+str(type(weights)))
try: print(weights.shape)
except Exception: print("error: weights.shape")
print("r:"+str(type(r)))
try: print(r.shape)
except Exception: print("error: r.shape")
print("pvar:"+str(type(pvar)))
try: print(pvar.shape)
except Exception: print("error: pvar.shape")
print("pcs:"+str(type(pcs)))
try: print(pcs.shape)
except Exception: print("error: pcs.shape")
print("eofs:"+str(type(eofs)))
try: print(eofs.shape)
except Exception: print("error: eofs.shape")
print("ntr:"+str(type(ntr)))
try: print(ntr)
except Exception: print("error: ntr.shape")
print("pvar_slow:"+str(type(pvar_slow)))
try: print(pvar_slow.shape)
except Exception: print("error: pvar_slow.shape")
print("pvar_lfc:"+str(type(pvar_lfc)))
try: print(pvar_lfc.shape)
except Exception: print("error: pvar_lfc.shape")
print("r_eofs:"+str(type(r_eofs)))
try: print(r_eofs.shape)
except Exception: print("error: r_eofs.shape")
print("pvar_slow_eofs:"+str(type(pvar_slow_eofs)))
try: print(pvar_slow_eofs.shape)
except Exception: print("error: pvar_slow_eofs.shape")
"""


#======================================reshape lfcs result=====================================#
nins = np.size(icol_disc[1])
nrows = ATCw_lfps.shape[0]
print(nrows)
print(ATCw_eofs.shape)
print(ATCc_eofs.shape)
print(ATCw_lfps.shape)
print(ATCc_lfps.shape)
ATCw_lfps_aug = np.zeros((nrows,ATCw_lfps.shape[1]+nins))
ATCc_lfps_aug = np.zeros((nrows,ATCc_lfps.shape[1]+nins))
ATCw_lfps_aug[:] = np.nan
ATCc_lfps_aug[:] = np.nan
ATCw_lfps_aug[:,icol_ret[1]] = ATCw_lfps
ATCc_lfps_aug[:,icol_ret[1]] = ATCc_lfps
nrows = ATCw_eofs.shape[0]
ATCw_eofs_aug = np.zeros((ATCw_eofs.shape[0],ATCw_eofs.shape[1]+nins))
ATCc_eofs_aug = np.zeros((ATCc_eofs.shape[0],ATCc_eofs.shape[1]+nins))
ATCw_eofs_aug[:] = np.nan
ATCc_eofs_aug[:] = np.nan
ATCw_eofs_aug[:,icol_ret[1]] = ATCw_eofs
ATCc_eofs_aug[:,icol_ret[1]] = ATCc_eofs
#%%
s1 = np.size(lon_axis)
s2 = np.size(lat_axis)
i = 0
#pattern = np.reshape(lfps_aug[i,...],(s1,s2),order=order)
ATCw_pattern = np.reshape(ATCw_lfps_aug,(ATCw_lfps.shape[0],s1,s2),order=order)
ATCc_pattern = np.reshape(ATCc_lfps_aug,(ATCc_lfps.shape[0],s1,s2),order=order)
ATCw_pattern[np.where(np.abs(ATCw_pattern)>1.e5)] = np.nan
ATCc_pattern[np.where(np.abs(ATCc_pattern)>1.e5)] = np.nan

ATCw_lfcs=ATCw_lfcs.transpose(1, 0)
ATCc_lfcs=ATCc_lfcs.transpose(1, 0)
ATCw_pattern=ATCw_pattern.transpose(0, 2, 1)
ATCc_pattern=ATCc_pattern.transpose(0, 2, 1)
#print(ATCw_pattern.shape)
#sys.stdout.flush()
#print(ATCw_lfps.shape)
#sys.stdout.flush()
#print(ATCw_lfcs.shape)
#sys.stdout.flush()

#=====================================write nc file====================================================#
current_directory = os.path.dirname(os.path.abspath(__file__))

new = nc.Dataset(str(current_directory)+"/LFCA_result_ACCESS-ESM1-5_1973_2014_monthly.nc", 'w')

new.createDimension("lat", nlat)
new.createDimension("lon", nlon)
new.createDimension("time", ntime)
new.createDimension("comp", truncation)

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

new.variables['lat'][:] = lat_axis
new.variables['lon'][:] = lon_axis

new.createVariable("lfps_up","float32", (u'comp',u'lat', u'lon'),fill_value=np.nan )
new.variables["lfps_up"][:]=ATCw_pattern[:]
new.variables["lfps_up"].__setattr__("standard_name","ATCw_lfps_30")

new.createVariable("lfps_down","float32", (u'comp',u'lat', u'lon'),fill_value=np.nan )
new.variables["lfps_down"][:]=ATCc_pattern[:]
new.variables["lfps_down"].__setattr__("standard_name","ATCc_lfps_30")

new.createVariable("lfcs_up","float32", (u'comp',u'time'),fill_value=np.nan )
new.variables["lfcs_up"][:]=ATCw_lfcs[:]
new.variables["lfcs_up"].__setattr__("standard_name","ATCw_lfcs_30")

new.createVariable("lfcs_down","float32", (u'comp',u'time'),fill_value=np.nan )
new.variables["lfcs_down"][:]=ATCc_lfcs[:]
new.variables["lfcs_down"].__setattr__("standard_name","ATCc_lfcs_30")

#=====================================plot result====================================================#

#print("star plot")
#sys.stdout.flush()
#plt.figure()
#plt.contourf(np.squeeze(lon_axis),np.squeeze(lat_axis),np.transpose(pattern),np.arange(-1,1.1,0.1),cmap=plt.cm.RdYlBu_r)
#plt.savefig(str(current_directory)+"/contourf_plot.png", dpi=100, bbox_inches='tight')
#plt.figure()
#plt.plot(lfcs[:,i])
#plt.savefig(str(current_directory)+"/plot_LFCA_ATCw.png",dpi=100)