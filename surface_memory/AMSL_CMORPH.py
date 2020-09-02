# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 10:15:40 2016

@author: cornkle
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib
import multiprocessing
import ipdb
import pandas as pd
from wavelet import util as wutil
from utils import u_arrays, constants as cnst, u_met
from scipy.stats import ttest_ind as ttest
from scipy.interpolate import griddata
import pickle as pkl
from utils import u_arrays as ua
import os
import collections
import warnings
import salem

matplotlib.rc('xtick', labelsize=10)
matplotlib.rc('ytick', labelsize=10)
matplotlib.rcParams['hatch.linewidth'] = 0.1


def run_hours():

    l = [15,16,17,18,19,20,21,22,23,0,1,2,3,4,5,6,7] #15,16,
    for ll in l:
        composite(ll)

def loopdays():

    for dk in ['day0', 'day+1', 'day+2', 'day+3', 'day+4', 'day+5']:
        composite(17,dk)

def composite(h, daykey):

    key = 'trackedDRY'

    month = 9
    # msgopen = pd.read_csv(cnst.network_data + 'figs/LSTA/corrected_LSTA/new/ERA5/core_txt/cores_gt15000km2_table_AMSRE_tracking_'+str(h)+'_init.csv', na_values=-999)

    # msgopen = pd.read_csv(
    #     cnst.network_data + 'figs/LSTA/corrected_LSTA/new/wavelet_coefficients/core_txt/PNAS_table_allCentre_2hOverlap/cores_gt15000km2_table_1640_580_' + str(
    #         h) + '_2hOverlap.csv', na_values=[-999, -99])
    #
    # hour = h
    # msg = pd.DataFrame.from_dict(msgopen)# &  &
    #
    # msg['refhour'] = h
    # msg['daykey'] = daykey
    #
    # msg['date'] = pd.to_datetime(msg[['year','month','day']])
    # print('Start core number ', len(msg))
    #
    # msgopen = msg
    #
    # #basic filter
    # month = 9
    # msgopen = msgopen[(msgopen['lat']>9.5) & (msgopen['lat']<20.5) & (msgopen['topo']<=450) & (msgopen['dtime']<=2) & (msgopen['month']==month)]

    ######################
    msgopen = pd.read_csv(
        cnst.network_data + 'figs/LSTA/corrected_LSTA/new/ERA5/core_txt/init_merged2/cores_gt15000km2_table_AMSRE_tracking2_' + str(
            h) + '_init.csv', na_values=[-999, -99])

    hour = h
    msg = pd.DataFrame.from_dict(msgopen)# &  &

    msg['refhour'] = h
    msg['daykey'] = daykey

    msg['date'] = pd.to_datetime(msg[['year','month','day']])
    print('Start core number ', len(msg))

    msgopen = msg

    #basic filter
    msgopen = msgopen[(msgopen['lat']>9.5) & (msgopen['lat']<20.5) & (msgopen['topo']<=450) & (msgopen['dtime']<=2)]
    #propagation filter
    msgopen = msgopen[(msgopen['xdiff']>=100) | ((msgopen['initTime'] <10 )&(msgopen['SMmean0'] >=-12) )]# | ((msgopen['initTime'] <11 )&(msgopen['initTime'] >2 ))]
    #msgopen = msgopen[(msgopen['xdiff'] >= 120) | ((msgopen['initTime'] < 10))]# & (msgopen['initTime'] > 2))]# & (msgopen['SMmean0'] >=0.1)  & (msgopen['SMmean-1'] >=0))]  # | ((msgopen['initTime'] <11 )&(msgopen['initTime'] >2 ))]

    #lsta filter
    #msgopen = msgopen[msgopen['LSTAslotfrac']>=0.05]
    #wetness_filter
    msgopen = msgopen[np.isfinite(msgopen['SMmean0'])]# & np.isfinite(msgopen['SMmean-1'])]
    #eraq_filter
    #msgopen = msgopen[(msgopen['ERAqmean'] >= 14)] #14
    # #dry_filter
    msgopen = msgopen[(msgopen['SMmean0']<=-1.8)]# -1.8 & (msgopen['SMmean-1']<=-0.5)]# & (msgopen['SMmean-1']<=-1)]#&(msgopen['SMmean0']<=-7.19)] #294 cases, with q 312
    # # #wet_filter

    ##########################
    msgin = msgopen
    print('Number of cores', len(msgin))
    msgin.sort_values(by='date')
    #ipdb.set_trace()
    msgy = msgin

    chunk, chunk_ind, chunk_count = np.unique(msgy.date, return_index=True, return_counts=True)

    chunks = [msgy.loc[msgy.index[ci:ci + cc]] for ci, cc in zip(chunk_ind, chunk_count)] # daily chunks

    # res = []
    # for m in chunks[::]:
    #     out = file_loop(m)
    #     res.append(out)
    #
    # return
    pool = multiprocessing.Pool(processes=5)

    res = pool.map(file_loop, chunks)
    pool.close()

    print('Returned from parallel')


    res = [x for x in res if x is not None]

    # lsta_list = []
    # lsta_cnt = []
    amsr_list = []
    amsr_cnt = []
    msg_list = []
    msg_cnt = []
    cmorph_list = []
    cmorph_cnt = []
    cores = 0
    for r in res:


        # lsta_list.append(r[0])
        # lsta_cnt.append(r[1])
        amsr_list.append(r[0])
        amsr_cnt.append(r[1])
        msg_list.append(r[2])
        msg_cnt.append(r[3])
        cmorph_list.append(r[4])
        cmorph_cnt.append(r[5])
        cores += r[6]

    dic = collections.OrderedDict([

                                   #('lsta' , [lsta_list, lsta_cnt]),
                                   ('amsr' , [amsr_list, amsr_cnt]),
                                   ('msg' , [msg_list, msg_cnt]),
                                   ('cmorph' , [cmorph_list, cmorph_cnt]),
                                   ('cores', cores)])

    keys = list(dic.keys())

    for l in keys:

        if l in ['cores','lsta']:  #'lsta'
            continue

        print(l)

        try:
            (dic[l])[0] = np.squeeze(np.vstack((dic[l])[0]))
        except TypeError:
            ipdb.set_trace()
        (dic[l])[1] = np.squeeze(np.vstack((dic[l])[1]))

    for l in keys:

        if l in ['cores','lsta']:  #, 'lsta'
            continue

        (dic[l])[0] = np.nansum((dic[l])[0], axis=0)
        (dic[l])[1] = np.nansum((dic[l])[1], axis=0)


    outpath = cnst.network_data + '/figs/CORE_MEMORY/tables/'
    pkl.dump(dic, open(outpath+"dominantCores_"+str(hour)+"UTC_15000_2dAMSL_ext_"+daykey+"_ALLS_minusMean_15-24LT_" +str(month).zfill(2)+'_'+ key + ".p", "wb"))
    print('Save file written!')




def cut_kernel_lsta(xpos, ypos, arr):

    dist = 200

    kernel = u_arrays.cut_kernel(arr,xpos, ypos,dist)

    kernel = kernel - np.nanmean(kernel)
    if kernel.shape != (2*dist+1, 2*dist+1):
        print('Kernel wrong shape')
        return

    # plt.figure()
    # plt.imshow(kernel, origin='lower')

    return kernel


def get_previous_hours_msg(storm_date, daykey):


    date = storm_date#.replace(hour=12)  # make 12 reference hour for MCS filter

    t1 = date +  pd.Timedelta('14 hours')
    t2 = date + pd.Timedelta('24 hours')

    # if daykey == 'day+2':
    #     t1 = date + pd.Timedelta('12 hours')
    #     t2 = date + pd.Timedelta('24 hours')
    #
    # if daykey == 'day+3':
    #     t1 = date + pd.Timedelta('12 hours')
    #     t2 = date + pd.Timedelta('24 hours')
    #
    # if daykey == 'day+4':
    #     t1 = date + pd.Timedelta('12 hours')
    #     t2 = date + pd.Timedelta('24 hours')
    #
    # if daykey == 'day+5':
    #     t1 = date + pd.Timedelta('12 hours')
    #     t2 = date + pd.Timedelta('24 hours')


    file = cnst.MCS_ALL# MCS_15K #_POINTS_DOM
    msg = xr.open_dataarray(file)
    try:
        msg = msg.sel(time=slice(t1.strftime("%Y-%m-%dT%H"), t2.strftime("%Y-%m-%dT%H")))
    except OverflowError:
        print('MSG date problem')
        return None

    #print(prev_time.strftime("%Y-%m-%dT%H"), date.strftime("%Y-%m-%dT%H"))
    pos = np.where((msg.values <= -65) ) #(msg.values >= 5) & (msg.values < 65)) # #

    out = np.zeros_like(msg.values)
    out[pos] = 1
    out[np.isnan(msg.values)] = np.nan
    out = np.nansum(out, axis=0)
    out[out>0]=1
    # if np.sum(out>1) != 0:
    #     'Stop!!!'
    #     pdb.set_trace()

    msg = msg.sum(axis=0)*0

    xout = msg.copy()
    del msg
    xout.name = 'probs'
    xout.values = out

    return xout



def get_previous_hours_CMORPH(date, daykey):


    # t1 = date -  pd.Timedelta('7 hours')
    # t2 = date + pd.Timedelta('17 hours')

    t1 = date +  pd.Timedelta('14 hours')
    t2 = date + pd.Timedelta('24 hours')


    # if daykey == 'day+2':
    #     t1 = date + pd.Timedelta('12 hours')
    #     t2 = date + pd.Timedelta('24 hours')
    #
    # if daykey == 'day+3':
    #     t1 = date + pd.Timedelta('12 hours')
    #     t2 = date + pd.Timedelta('24 hours')
    #
    # if daykey == 'day+4':
    #     t1 = date + pd.Timedelta('12 hours')
    #     t2 = date + pd.Timedelta('24 hours')
    #
    # if daykey == 'day+5':
    #     t1 = date + pd.Timedelta('12 hours')
    #     t2 = date + pd.Timedelta('24 hours')
    # before2 = pd.Timedelta('15 minutes')
    #
    # t1 = date #- before
    # t2 = date + before2

    file = cnst.CMORPH

    try:
        cmm = xr.open_dataarray(file + 'CMORPH_WA_' + str(date.year) + '.nc')
    except:
        return None
    cmm = cmm.sel( time=slice(t1, t2)).sum(dim='time')
    # cmm = cmm.sel(lat=slice(10.9, 19), lon=slice(-9.8, 9.8))

    cm = cmm
    pos = np.where(cm.values >= 8)

    out = np.zeros_like(cm)
    out[pos] = 1

    xout = cm.copy()
    xout.name = 'probs'
    xout.values = out

    return xout



def file_loop(df):

    date = df['date'].iloc[0]
    hour = df['hour'].iloc[0]
    print('Doing day: ', date)

    daykey = df['daykey'].iloc[0]

    storm_date = date

    dayd = pd.Timedelta('1 days')

    prev_day = storm_date - dayd
    next_day = storm_date + dayd
    next2_day = storm_date + pd.Timedelta('2 days')
    next3_day = storm_date + pd.Timedelta('3 days')
    next4_day = storm_date + pd.Timedelta('4 days')
    next5_day = storm_date + pd.Timedelta('5 days')

    ctimes = {'day0' : [storm_date, cnst.AMSRE_ANO_DAY],
              'night0': [storm_date, cnst.AMSRE_ANO_NIGHT],
              'day-1' : [prev_day, cnst.AMSRE_ANO_DAY],
              'night-1': [prev_day, cnst.AMSRE_ANO_NIGHT],
              'night+1': [next_day, cnst.AMSRE_ANO_NIGHT],
              'day+1' : [next_day, cnst.AMSRE_ANO_DAY],
              'night+2': [next2_day, cnst.AMSRE_ANO_NIGHT],
              'day+2': [next2_day, cnst.AMSRE_ANO_DAY],
              'night+3': [next3_day, cnst.AMSRE_ANO_NIGHT],
              'day+3': [next3_day, cnst.AMSRE_ANO_DAY],
              'night+4': [next4_day, cnst.AMSRE_ANO_NIGHT],
              'day+4': [next4_day, cnst.AMSRE_ANO_DAY],
              'night+5': [next5_day, cnst.AMSRE_ANO_NIGHT],
              'day+5': [next5_day, cnst.AMSRE_ANO_DAY]
              }

    tag = daykey

    outime = (ctimes[tag])[0]

    fdate = str(outime.year) + str(outime.month).zfill(2) + str(outime.day).zfill(2)


    #topo = xr.open_dataset(cnst.LSTA_TOPO)
    topo = xr.open_dataset(cnst.WA_TOPO_3KM)
    topo = topo.sel(lat=slice(6.5,26.5), lon=slice(-14.5,14.5))

    ttopo = topo['h']
    grad = np.gradient(ttopo.values)
    gradsum = abs(grad[0]) + abs(grad[1])

    amsre = xr.open_dataset((ctimes[tag])[1] + 'sma_' + fdate + '.nc')
    amsre = amsre.sel(time=str(outime.year)+'-'+str(outime.month)+'-'+str(outime.day))
    amsre = amsre.sel(lon=slice(-15, 15), lat=slice(6, 27))
    print('Doing '+ 'AMSR_' + str(outime.year) + str(outime.month).zfill(2) + str(
        outime.day).zfill(2) + '.nc')

    amsr_da = amsre['SM'].squeeze()


    # try:
    #     lstal = xr.open_dataset(cnst.LSTA_1330 + 'lsta_daily_' + fdate + '.nc')
    # except OSError:
    #     return None
    # print('Doing ' + 'lsta_daily_' + fdate + '.nc')
    #
    # lsta_da = lstal['LSTA'].squeeze()
    # slot_da = lstal['NbSlot'].squeeze().values

    # if (np.sum(np.isfinite(lsta_da)) / lsta_da.size) < 0.01:
    #     print('Not enough valid')
    #     return None



    # if (np.sum(np.isfinite(amsr_da)) / amsr_da.size) < 0.01:
    #     print('Not enough valid')
    #     return None

    try:
        amsr_da = topo.salem.transform(amsr_da, interp='nearest')
    except RuntimeError:
        print('amsr_da on LSTA interpolation problem')
        return None


    # try:
    #     lsta_da = topo.salem.transform(lsta_da, interp='nearest')
    # except RuntimeError:
    #     print('lsta_da on LSTA interpolation problem')
    #     return None


    probs_msg = get_previous_hours_msg(outime, daykey)
    probsm_on_lsta = topo.salem.transform(probs_msg, interp='nearest')
    del probs_msg

    probs_cm = get_previous_hours_CMORPH(outime, daykey)   # get previous rain to storm
    try:
        probscm_on_lsta = topo.salem.transform(probs_cm, interp='nearest')
    except RuntimeError:
        return None

    # lsta_da.values[ttopo.values >= 450] = np.nan
    # lsta_da.values[gradsum > 30] = np.nan

    amsr_da.values[ttopo.values >= 450] = np.nan
    amsr_da.values[gradsum > 30] = np.nan

    del topo

    # lsta = []
    amsr = []
    msg = []
    cmorph = []


    ###############################Blob loop
    cores = 0
    ERAq = 0

    for dids, dit in df.iterrows():

        lat = dit.lat
        lon = dit.lon

        try:
            point = amsr_da.sel(lat=lat, lon=lon, method='nearest', tolerance=0.04)
        except KeyError:
            print('Nearest point finding error')
            continue

        plat = point['lat'].values
        plon = point['lon'].values

        xpos = np.where(amsr_da['lon'].values == plon)
        xpos = int(xpos[0])
        ypos = np.where(amsr_da['lat'].values == plat)
        ypos = int(ypos[0])

        # try:
        #     lsta_kernel = cut_kernel_lsta(xpos, ypos, lsta_da.values)
        # except TypeError:
        #     print('LSTA kernel error')
        #     continue

        try:
            amsre_kernel = cut_kernel_lsta(xpos, ypos, amsr_da.values)
        except TypeError:
            print('AMSR kernel error')
            continue

        try:
            msg_kernel = cut_kernel_lsta(xpos, ypos, probsm_on_lsta.values)
        except TypeError:
            print('AMSR kernel error')
            continue

        try:
            cmorph_kernel = cut_kernel_lsta(xpos, ypos, probscm_on_lsta.values)
        except TypeError:
            print('AMSR kernel error')
            continue

        # lsta.append(lsta_kernel)
        amsr.append(amsre_kernel)
        msg.append(msg_kernel)
        cmorph.append(cmorph_kernel)
        cores += 1


    # del lsta_da
    del amsr_da
    del probsm_on_lsta
    del probscm_on_lsta

    if (np.array(amsr).ndim == 1):
        return None


    #try:
    if  (len(amsr) <= 1) | (np.array(amsr).ndim < 3) |  (np.nansum(amsr)==0):
        print('NorthSouth 1')
        return None
    else:
        # try:
        #     lsta_sum = np.nansum(np.stack(lsta, axis=0), axis=0)[np.newaxis,...]
        #     lsta_cnt = np.nansum(np.isfinite(np.stack(lsta, axis=0)), axis=0)[np.newaxis,...]
        # except:
        #     lsta_sum = 0
        #     lsta_cnt = 0
        try:
            amsr_sum = np.nansum(np.stack(amsr, axis=0), axis=0)[np.newaxis,...]
        except ValueError:
            ipdb.set_trace()
        amsr_cnt = np.nansum(np.isfinite(np.stack(amsr, axis=0)), axis=0)[np.newaxis,...]

        msg_sum = np.nansum(np.stack(msg, axis=0), axis=0)[np.newaxis,...]
        msg_cnt = np.nansum(np.isfinite(np.stack(msg, axis=0)), axis=0)[np.newaxis,...]

        cmorph_sum = np.nansum(np.stack(cmorph, axis=0), axis=0)[np.newaxis,...]
        cmorph_cnt = np.nansum(np.isfinite(np.stack(cmorph, axis=0)), axis=0)[np.newaxis,...]


    print('Returning with kernel, success!!')

    return (amsr_sum, amsr_cnt, msg_sum, msg_cnt, cmorph_sum, cmorph_cnt, cores) #lsta_sum, lsta_cnt,

if __name__ == "__main__":
    run_hours()
