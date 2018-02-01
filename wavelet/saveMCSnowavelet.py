# -*- coding: utf-8 -*-


import numpy as np
from wavelet import util
from eod import msg
import xarray as xr
import os
from utils import u_grid
from scipy.interpolate import griddata
from scipy import ndimage
from utils import u_arrays as ua
import multiprocessing
import datetime as dt
import matplotlib.pyplot as plt
import pdb


def run():
    #  (1174, 378)
    msg_folder = '/users/global/cornkle/data/OBS/meteosat_WA30'
    pool = multiprocessing.Pool(processes=7)

    m = msg.ReadMsg(msg_folder)
    files  = m.fpath

    files = files[4000:4100]
    mdic = m.read_data(files[0], llbox=[-6, 3, 11, 16])
    # make salem grid
    grid = u_grid.make(mdic['lon'].values, mdic['lat'].values, 5000) #m.lon, m.lat, 5000)

    files_str = []

    for f in files:
        files_str.append(f[0:-6])

    files_str = np.unique(files_str)

    passit = []
    for f in files_str:
        passit.append((grid,m, f))

    res = pool.map(file_loop, passit)


    #
    # for l in passit:
    #
    #     test = file_loop(l)

    pool.close()

    #return

    res = [x for x in res if x is not None]

    da = xr.concat(res, 'time')
    #da = da.sum(dim='time')

    savefile = '/users/global/cornkle/MCSfiles/mcs_map_30km_-40_JJAS_burkina.nc'

    try:
        os.remove(savefile)
    except OSError:
        pass
    da.to_netcdf(path=savefile, mode='w')
    #
    # das = da.sum(dim='time')
    #
    # das.to_netcdf('/users/global/cornkle/MCSfiles/blob_map_35km_-67_JJAS_sum_17-19UTC.nc')

    print('Saved ' + savefile)



def file_loop(passit):



    grid = passit[0]

    m = passit[1]
    files = passit[2]

    min_list = ['00'] #'15','30', '45']

    strr = files.split(os.sep)[-1]

    if ((np.int(strr[4:6]) > 9) | (np.int(strr[4:6])<6)):
        print('Skip month')
        return

    # if not ((np.int(strr[8:10]) >= 20)): #& (np.int(strr[8:10]) <= 19) ): #((np.int(strr[8:10]) > 3)): #not ((np.int(strr[8:10]) >= 16) & (np.int(strr[8:10]) <= 19) ): #& (np.int(strr[8:10]) < 18): #(np.int(strr[4:6]) != 6) & #(np.int(strr[8:10]) != 3) , (np.int(strr[8:10]) > 3)
    #     print('Skip hour')
    #     return

    lon, lat = grid.ll_coordinates

    ds = xr.Dataset()

    for min in min_list:

        file = files+min+'.gra'

        print('Doing file: ' + file)
        try:
            mdic = m.read_data(file, llbox=[-6,3,11,16])
        except FileNotFoundError:
            print('File not found')
            return

        if not mdic:
            print('File missing')
            return

        outt = u_grid.quick_regrid(mdic['lon'].values, mdic['lat'].values,mdic['t'].values.flatten(), grid)

        # hour = mdic['time.hour']
        # minute = mdic['time.minute']
        # day = mdic['time.day']
        # month = mdic['time.month']
        # year = mdic['time.year']
        #
        # date = dt.datetime(year, month, day, hour, minute)
        #
        # da = xr.DataArray(outt, coords={'time': date, 'lat': lat[:, 0], 'lon': lon[0, :]},
        #                   dims=['lat', 'lon'])  # [np.newaxis, :]
        #
        # da.to_netcdf('/users/global/cornkle/test.nc')
        # return

        out = np.zeros_like(outt, dtype=np.int)

        outt[outt >= -40] = np.nan
        outt[np.isnan(outt)] = -40


        hour = mdic['time.hour']
        minute = mdic['time.minute' ]
        day = mdic['time.day']
        month = mdic['time.month']
        year = mdic['time.year']

    date = dt.datetime(year, month, day, hour, minute)

    da = xr.DataArray(outt, coords={'time': date, 'lat': lat[:,0], 'lon':lon[0,:]}, dims=['lat', 'lon']) #[np.newaxis, :]

    #da.to_netcdf('/users/global/cornkle/MCSfiles/blob_maps_0-4UTC_-65/'+str(date)+'.nc')

    print('Did ', file)

    return (da)

