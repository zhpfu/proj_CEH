import numpy as np
import xarray as xr
from utils import u_arrays as ua, u_darrays as uda
import matplotlib.pyplot as plt
import multiprocessing
import pickle as pkl
from collections import defaultdict
from utils import constants as cnst, u_met


import pdb
import glob
import ipdb
import pandas as pd

def dictionary():

    dic = {}
    vars = ['hour', 'month', 'year', 'area',
            'lon', 'lat', 'clon', 'clat',
            'tmin', 'tmean',
            'pmax', 'pmean',
            'q925', 'q650',
            'u925', 'u650',
            'v925', 'v650',
            'w925', 'w650',
            'rh925','rh650',
            't925', 't650',
            'div925','div650',
            'pv925', 'pv650',
            'shear',
            'pgt30', 'pgt01'
            'isvalid',
             't', 'p' ]

    for v in vars:
        dic[v] = []
    return dic

def perSys():

    pool = multiprocessing.Pool(processes=4)
    tthresh = '-50'
    files = glob.glob(cnst.network_data + 'MCSfiles/WA5000_4-20N_12W-12E_-50_afternoon_GPM/*.nc')
    #ipdb.set_trace()

    print('Nb files', len(files))
    mdic = dictionary() #defaultdict(list)
    res = pool.map(file_loop, files)
    pool.close()

    #
    # res = []
    # for f in files[0:100]:
    #     out = file_loop(f)
    #     res.append(out)
    #
    #res = [item for sublist in res for item in sublist]  # flatten list of lists

    keys = mdic.keys()
    for v in res:
        for k in keys:
            try:
                mdic[k].append(v[k])
            except TypeError:
                continue

        # if v[2]*25 > 1000000:
        #     tplt = v[9]
        #     tplt[np.where(tplt==np.nan)]=0
            # f = plt.figure()
            # ax = plt.axes(projection=ccrs.PlateCarree())
            # plt.contourf(v[10], v[11], tplt, transform=ccrs.PlateCarree())
            # ax.coastlines()
            # plt.colorbar()
            # ax.add_feature(cartopy.feature.BORDERS, linestyle='--')


    # f = plt.figure()
    # siz = 3
    #
    # ax = f.add_subplot(1, 1, 1)
    # plt.scatter(mdic['tmin'], mdic['pmax'])
    # plt.title('bulk', fontsize=9)

    #ipdb.set_trace()
    pkl.dump(mdic, open(cnst.network_data + 'data/CLOVER/saves/bulk_'+tthresh+'_5000km2_GPM_ERA5_5-20N_p15.p',
                           'wb'))


def file_loop(f):
    print('Doing file: ' + f)

    dic = xr.open_dataset(f)
    edate = pd.Timestamp(dic.time.values)

    if edate.hour < 17:
        return

    try:
        era_pl = xr.open_dataset(cnst.ERA5_HOURLY_PL+'ERA5_'+str(dic['time.year'].values)+'_'+str(dic['time.month'].values).zfill(2)+'_pl.nc')
    except:
        print('ERA5 missing')
        return
    #era_srfc = xr.open_dataset(cnst.ERA5_HOURLY_SRFC+'ERA5_'+str(dic['time.year'].values)+'_'+str(dic['time.month'].values).zfill(2)+'_srfc.nc')
    era_pl = uda.flip_lat(era_pl)
    #era_srfc = uda.flip_lat(era_srfc)

    edate = edate.replace(hour=12, minute=0)

    era_pl_day = era_pl.sel(time=edate, longitude=slice(-13,13), latitude=slice(4,22))
    #era_srfc_day = era_srfc.sel(time=edate, longitude=slice(-13, 13), latitude=slice(4, 22))

    #ipdb.set_trace()
     # try:
    #     era_day = era.isel(time=int(getera[0]))
    # except TypeError:
    #     print('Era missing')
    #     return

    out = dictionary()
    res = []
    outt = dic['tc_lag0'].values
    outp = dic['p'].values


    tminpos = np.where(dic['tc_lag0'].values == np.nanmin(dic['tc_lag0'].values)) # era position close to min temp
    if len(tminpos[0])>1:
        ptmax = np.nanmax((dic['p'].values)[tminpos])
        if ptmax > 0:
            prpos = np.where((dic['p'].values)[tminpos] == ptmax)
            tminpos = ((tminpos[0])[prpos], (tminpos[1])[prpos] )
        else:
            tminpos = ((tminpos[0])[0], (tminpos[1])[0])

    elon = dic['lon'].values[tminpos]
    elat = dic['lat'].values[tminpos]

    era_day = era_pl_day.sel(latitude=elat, longitude=elon , method='nearest')

    del era_pl_day

    e925 = era_day.sel(level=925).mean()
    elow = era_day.sel(level=slice(925,850)).mean('level').mean()
    e650 = era_day.sel(level=650).mean()
    emid = era_day.sel(level=slice(600,700)).mean('level').mean()


    out['lon'] = dic['lon'].values
    out['lat'] = dic['lat'].values
    out['hour'] = dic['time.hour'].item()
    out['month'] = dic['time.month'].item()
    out['year'] = dic['time.year'].item()
    out['date'] = dic['time'].values

    t_thresh = -50  # -40C ~ 167 W m-2
    mask = np.isfinite(outp) & (outt<=t_thresh) & np.isfinite(outt)
    mask_area = (outt<=t_thresh) & np.isfinite(outt)
    mask70 = (outt<=-70) & np.isfinite(outt)

    if np.sum(mask) < 3:
        return

    out['clat'] = np.min(out['lat'])+((np.max(out['lat'])-np.min(out['lat']))*0.5)
    out['clon'] = np.min(out['lon']) + ((np.max(out['lon']) - np.min(out['lon'])) * 0.5)

    print(np.nanmax(outt[mask]))   # can be bigger than cutout threshold because of interpolation to 5km grid after cutout

    out['area'] = np.sum(mask_area)
    out['area70'] = np.sum(mask70)

    out['clat'] = np.min(out['lat'])+((np.max(out['lat'])-np.min(out['lat']))*0.5)
    out['clon'] = np.min(out['lon']) + ((np.max(out['lon']) - np.min(out['lon'])) * 0.5)

    out['tmin'] = np.min(outt[mask])
    out['tmean'] = np.mean(outt[mask])

    maxpos = np.unravel_index(np.nanargmax(outp), outp.shape)
    out['pmax'] = np.nanmean(ua.cut_kernel(outp,maxpos[1], maxpos[0],1)) #np.max(outp[mask])
    out['pmean'] = np.mean(outp[mask])
    try:
        out['q925'] =float(e925['q'])
    except TypeError:
        return

    out['q650'] = float(e650['q'])
    out['v925'] = float(e925['v'])
    out['v650'] = float(e925['v'])
    out['u925'] = float(e925['u'])
    out['u650'] = float(e650['u'])
    out['w925'] = float(e925['w'])
    out['w650'] = float(e650['w'])
    out['rh925'] = float(e925['r'])
    out['rh650'] = float(e650['r'])
    out['t925'] = float(e925['t'])
    out['t650'] = float(e650['t'])
    out['pv925'] = float(e925['pv'])
    out['pv650'] = float(e650['pv'])
    out['div925'] = float(e925['d'])
    out['div650'] = float(e650['d'])
    out['q_low'] = float(elow['q'])
    out['q_mid'] = float(emid['q'])

    out['shear'] = float(e650['u']-e925['u'])

    theta_down = u_met.theta_e(925,e925['t']-273.15, e925['q'])
    theta_up = u_met.theta_e(650,e650['t']-273.15, e650['q'])

    out['dtheta'] =  theta_down-theta_up
    out['thetaup'] = theta_up
    out['thetadown'] = theta_down

    out['pgt30'] = np.sum(outp[mask]>=30)
    out['isvalid'] = np.sum(mask)
    out['pgt01'] = np.sum(outp[mask]>=0.1)
    #
    out['p'] = outp[mask]
    out['t'] = outt[mask]
    #ipdb.set_trace()
    dic.close()

    return out
