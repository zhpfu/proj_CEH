# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 10:15:40 2016

@author: cornkle
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib
import ipdb
import pandas as pd
import glob
from utils import u_met, u_parallelise, u_gis, u_arrays as ua, constants as cnst, u_grid, u_darrays
from matplotlib import pyplot, lines
from scipy import ndimage
import matplotlib.patches as patches

import pickle as pkl


matplotlib.rc('xtick', labelsize=10)
matplotlib.rc('ytick', labelsize=10)



def plot_timeseries_coarse():

    xx = len(list(range(-38, 4, 3)))
    yy = 401

    ranges = np.arange(-38, 4, 3)

    h = 17

    def dicloop(ff):

        def coll(dic, h, eh, year, ff):
            print(h)
            core = pkl.load(open(
                cnst.network_data + ff + str(eh) + "UTCERA" + str(h).zfill(2) + '_' + str(year) + ".p", "rb"))
            for id, k in enumerate(core.keys()):
                try:
                    dic[k] = dic[k] + core[k]
                except KeyError:
                    dic[k] = core[k]

        outdic = {}

        dummyfile = glob.glob(
            cnst.network_data + ff+"*.p")
        dummy = pkl.load(open(dummyfile[0], "rb"))

        for k in dummy.keys():
            outdic[k] = np.zeros((yy, xx))

        for ids, eh in enumerate(range(-38, 4, 3)):
            dic = {}

            for y in range(2006, 2011):
                coll(dic, h, eh, y, ff)
            #if fids == 1:
                #ipdb.set_trace()
            for k in dic.keys():
                if k == 'sm':
                    continue
                if (k=='lsta0') & (eh<-11):
                    outdic[k][:, ids] = dic['lsta-1'][:, 190:267].mean(axis=1)
                else:
                    try:
                        outdic[k][:, ids] = dic[k][:, 190:267].mean(axis=1) # [190:211]
                    except:
                        print('Missing '+k)
                        continue

        def groupedAvg(myArray, N=2):
            result = np.cumsum(myArray, 0)[N - 1::N, :] / float(N)
            result[1:,:] = result[1:, :] - result[:-1, :]
            return result
        n = 4
        diff = {}
        for k in outdic.keys():

            if 'cnt' in k:
                continue

            if 'lsta0' in k:
                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cnt0']) , N=n), 0, mode='nearest')
            elif 'lsta-1' in k:
                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cnt-1']) , N=n), 0, mode='nearest')
            elif 'lsta-2' in k:
                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cnt-2']), N=n), 0, mode='nearest')
            elif 'lsta-3' in k:
                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cnt-3']) , N=n), 0, mode='nearest')
            elif 'msg' in k:
                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cntm']) , N=n), 0, mode='nearest')
            elif 'probc' in k:
                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cntc']) , N=n), 0, mode='nearest')
            else:
                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cnte']) , N=n), 0, mode='nearest')

        return diff


    filewet = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_WET20_"#"figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_2hOverlap_AMSRE_SMWET_AMSL_mini"

    filedry = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_DRY2_" #"figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_2hOverlap_AMSRE_SMDRY_AMSL_mini"
    filedry2 = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_2hOverlap_AMSRE_SMDRY_AMSL_mini"
    # file = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_2hOverlap_AMSRE_SMALL_MCSfilter_minusMean_smallDomain_"#ERA5_cores_2hOverlap_AMSRE_SMALL_AMSL_new"
    #file = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_ALL2_"
    file = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_ALL20_"

    #file = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_DRY_SM0LT3-1LT1.5_noMeteosatFilter_AMSRE"
    #file = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_WET_SM0GT0.01-1GT0.01_noMeteosatFilter_AMSRE"
    #####file = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_WET_TAG_noMeteosatFilter_AMSRE"
    fs = [file,filedry,filewet]
    fs2 = ['',filedry2, '']


    f = plt.figure(figsize=(14,7), dpi=300)


    for fids, ff in enumerate(fs):

        diff = dicloop(ff)
        if fids == 1:
            diff2 = dicloop(fs2[fids])

        titles = ['ALL', 'DRY', 'WET']

        ax = f.add_subplot(2,3,fids+1)

        yax = np.arange(100)

        levels = list(np.arange(-0.9, 0, 0.1)) + list(np.arange(0.1, 0.95, 0.1))
        plt.contourf(ranges, yax, (diff['t'])-diff['tclim'], extend='both', cmap='RdBu_r',
                    levels=levels)
        plt.colorbar(label=r'K')
        # plt.contour(ranges, yax, (diff['t'])-diff['tclim'], extend='both', colors='k', linewidths=0.1,
        #              levels=levels)
        # if (fids == 1):
        #     cont = plt.contour(ranges, yax, diff['lsta0']*-1, extend='both', colors='r', linewidths=2, levels=[1.5,5], linestyle='solid')
        #
        #if (fids == 2):
            #diff['lsta0'][75:100, :] = 0
            #ipdb.set_trace()
            # cont = plt.contour(ranges, yax, diff['lsta0'], extend='both', colors='b', linewidths=2,
            #                    levels=[0.5,1], linestyle='solid')
            #
            # cont = plt.contourf(ranges, yax, diff['lsta0'], extend='both', cmap='jet', levels=[0,0.1,0.3,0.5,0.6,0.7])
            # cont = plt.contour(ranges, yax, diff['lsta0'], extend='both', cmap='jet',
            #                     levels=[0, 0.1, 0.3, 0.5, 0.6, 0.7])
            # plt.clabel(cont, inline=True, fontsize=8, fmt='%1.1f')


        if (fids <= 1):
            dpos = np.where((diff['lsta0']*-1)[:,-1] >=1.5)
            y=dpos[0]
            line1 = lines.Line2D(np.array([ranges[-1]] * len(y)), y, lw=5., color='k', alpha=1, zorder=98)
            line2 = lines.Line2D(np.array([ranges[-1]]*len(y)), y, lw=4., color='white', alpha=1, zorder=99)
            line1.set_clip_on(False)
            line2.set_clip_on(False)
            ax.add_line(line1)
            ax.add_line(line2)
        #ipdb.set_trace()
        line1 = lines.Line2D(np.array([ranges[-5::]]), [diff['t'].shape[0]-1]*5, lw=5., color='k', alpha=1, zorder=98)
        line2 = lines.Line2D(np.array([ranges[-5::]]), [diff['t'].shape[0]-1]*5, lw=4., color='slategrey', alpha=1, zorder=99)
        line1.set_clip_on(False)
        line2.set_clip_on(False)
        ax.add_line(line1)
        ax.add_line(line2)

        line1 = lines.Line2D(np.array([ranges[-13:-8]]), [diff['t'].shape[0]-1]*5, lw=5., color='k', alpha=1, zorder=98)
        line2 = lines.Line2D(np.array([ranges[-13:-8]]), [diff['t'].shape[0]-1]*5, lw=4., color='slategrey', alpha=1, zorder=99)
        line1.set_clip_on(False)
        line2.set_clip_on(False)
        ax.add_line(line1)
        ax.add_line(line2)

            # dpos = np.where((diff['lsta0']*-1)[:,10] >=1.5)
            # y=dpos[0]
            # line = lines.Line2D(np.array([ranges[0]]*len(y)), y, lw=5., color='k', alpha=1, zorder=99)
            # line.set_clip_on(False)
            # ax.add_line(line)


        if (fids == 2):
            dpos = np.where((diff['lsta0'])[:, -1] >= 0.1)

            y = (dpos[0])[dpos[0]>35]
            line1 = lines.Line2D(np.array([ranges[-1]] * len(y)), y, lw=5., color='k', alpha=1, zorder=98)
            line2 = lines.Line2D(np.array([ranges[-1]] * len(y)), y, lw=4., color='white', alpha=1, zorder=99)
            line1.set_clip_on(False)
            line2.set_clip_on(False)
            ax.add_line(line1)
            ax.add_line(line2)


            # dpos = np.where((diff['lsta0'])[:, 10] >= 0.1)
            #
            # y = (dpos[0])[dpos[0]>35]
            # line = lines.Line2D(np.array([ranges[0]] * len(y)), y, lw=5., color='k', alpha=1, zorder=99)
            # line.set_clip_on(False)
            # ax.add_line(line)


        #plt.clabel(cont, inline=True, fontsize=9, fmt='%1.2f')
        sh =  (diff['u650']-diff['u650_clim'])
        if fids ==1:
            sh = (diff2['u650'])
        contours = plt.contour(ranges, yax, sh, extend='both', colors='k',
                               levels=np.arange(-8,0,0.5), linewidths=1)

        plt.clabel(contours, inline=True, fontsize=9, fmt='%1.2f')

        # contours = plt.contour(ranges, yax, (diff['shear']), extend='both', colors='k',
        #                        levels=np.arange(-4,0,0.5), linewidths=1)
        #
        # plt.clabel(contours, inline=True, fontsize=9, fmt='%1.2f')

        v0 = (diff['v925_orig'])
        if fids ==1:
            v0=(diff2['v925_orig'])
            contours = plt.contour(ranges, yax, v0, extend='both', colors='k', linewidths=5, levels=[-50, 0.06, 50])

        if fids==0:
            contours = plt.contour(ranges, yax,v0, extend='both',colors='k', linewidths=5, levels=[-50,0.06,50])
        if fids == 2:
            v0[40:50,0:20]=0.6
            contours = plt.contour(ranges, yax, v0, extend='both', colors='k', linewidths=5, levels=[-50, 0.35, 50])



        plt.axvline(x=-5, color='slategrey')
        plt.axvline(x=-29, color='slategrey')
        plt.axhline(y=50, color='slategrey')
        plt.plot(-5, 50, 'ko')
        #plt.plot(0, 50, 'ro')
        plt.plot(0, 50, marker='o', color='dimgrey')

        ax.set_yticklabels(np.array((np.linspace(0, 100, 6) - 50) * 12, dtype=int))
        if (fids == 0):
            plt.ylabel('North-South distance from core (km)')

        plt.title(titles[fids], fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')


        ax = f.add_subplot(2,3,fids+4)

        plt.contourf(ranges, yax, (diff['q']-diff['qclim']) * 1000, levels=[-0.8, -0.7, -0.6, -0.5, -0.4, -0.3,-0.2, -0.1, 0.1, 0.2, 0.3,0.4, 0.5, 0.6, 0.7, 0.8],
                     cmap='RdBu', extend='both')
        plt.colorbar(label=r'g kg$^{-1}$')

        # plt.contour(ranges, yax, (diff['q']-diff['qclim']) * 1000, levels=[-0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.1, 0.2, 0.3,0.4, 0.5, 0.6, 0.7, 0.8],
        #  colors = 'k', linewidths = 0.1)

        th = ((diff['theta_e']-diff['theta_e_clim']))
        # if fids ==1:
        #     th = ((diff2['theta']) - diff2['theta_clim']) - ((diff2['theta_e'] - diff2['theta_e']))

        contours = plt.contour(ranges, yax, th, colors='k',
                                linewidths=1.2, levels=[0.4,0.8,1.2,1.6,2,2.4])#) #,
        plt.clabel(contours, inline=True, fontsize=8, fmt='%1.1f')

        line1 = lines.Line2D(np.array([ranges[-5::]]), [diff['t'].shape[0]-1]*5, lw=5., color='k', alpha=1, zorder=98)
        line2 = lines.Line2D(np.array([ranges[-5::]]), [diff['t'].shape[0]-1]*5, lw=4., color='slategrey', alpha=1, zorder=99)
        line1.set_clip_on(False)
        line2.set_clip_on(False)
        ax.add_line(line1)
        ax.add_line(line2)

        line1 = lines.Line2D(np.array([ranges[-13:-8]]), [diff['t'].shape[0]-1]*5, lw=5., color='k', alpha=1, zorder=98)
        line2 = lines.Line2D(np.array([ranges[-13:-8]]), [diff['t'].shape[0]-1]*5, lw=4., color='slategrey', alpha=1, zorder=99)
        line1.set_clip_on(False)
        line2.set_clip_on(False)
        ax.add_line(line1)
        ax.add_line(line2)

        # cs = plt.contour(ranges, yax, (diff['probmsg'])*100,
        #  colors = 'k', linewidths = 0.5)
        #plt.clabel(cs, inline=True, fontsize=8, fmt='%1.1f')


        plt.axvline(x=-5, color='slategrey')
        plt.axvline(x=-29, color='slategrey')
        plt.axhline(y=50, color='slategrey')
        plt.plot(-5, 50, 'ko')
        #plt.plot(0, 50, 'ro')
        plt.plot(0, 50, marker='o', color='dimgrey')

        ax.set_yticklabels(np.array((np.linspace(0, 100, 6) - 50) *12 , dtype=int))


        plt.xlabel('Hour relative to t0')

        if (fids == 0):
            plt.ylabel('North-South distance from core (km)')

    plt.tight_layout()

    text = ['a', 'b', 'c', 'd', 'e', 'f']
    fs = 14
    plt.annotate(text[0], xy=(0.006, 0.96), xytext=(0, 4),xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[1], xy=(0.34, 0.96), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[2], xy=(0.67, 0.96), xytext=(0, 4),  xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[3], xy=(0.006, 0.48), xytext=(0, 4),xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[4], xy=(0.34, 0.48), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[5], xy=(0.67, 0.48), xytext=(0, 4),  xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)

    plt.savefig(cnst.network_data + "figs/LSTA/corrected_LSTA/new/ERA5/plots/ERA5_amsre_"+str(h).zfill(2)+'_timeseries_ALL20_NEWTRACKING2_new.png')#str(hour).zfill(2)+'00UTC_lsta_fulldomain_dominant<60.png)
    plt.close()


def plot_timeseries_diff_coarse():

    x = len(list(range(-38, 4, 3)))
    y = 401

    # outticks = list(range(-30, 1, 5))
    # ranges = np.arange(-30,1,3)
    #
    # outticks = [12,17,22,3,8,13,18]
    #outticks = [6, 11, 16, 21, 2, 7, 12, 17]
    ranges = np.arange(-38, 4, 3)

    h = 17

    outdic1 = {}
    outdic2 = {}
    dummyfile = glob.glob(
        cnst.network_data + "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_DRY20_*.p")
    dummy = pkl.load(open(dummyfile[0], "rb"))

    # file1 = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_DRY_SM0LT3-1LT1.5_noMeteosatFilter_AMSRE"   #ERA5_cores_2hOverlap_AMSRE_ALL_slot01_
    # file2 = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_WET_SM0GT0.01-1GT0.01_noMeteosatFilter_AMSRE"
    #file1 = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_2hOverlap_AMSRE_SMDRY_AMSL_mini"   #ERA5_cores_2hOverlap_AMSRE_ALL_slot01_
    file1 = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_DRY20_"
    file2 = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_WET20_"
    #file2 = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_2hOverlap_AMSRE_SMWET_AMSL_mini"
    files = [file1, file2]
    outdics = [outdic1, outdic2]

    for file, outdic in zip(files,outdics):

        for k in dummy.keys():
            outdic[k] = np.zeros((y, x))

        for ids, eh in enumerate(range(-38, 4, 3)):

            dic = {}

            def coll(dic, h, eh, year, file):
                print(h)

                core = pkl.load(open(
                    cnst.network_data + file + str(eh) + "UTCERA" + str(h).zfill(2) + '_' + str(year) + ".p", "rb"))

                for id, k in enumerate(core.keys()):
                    try:
                        dic[k] = dic[k] + core[k]
                    except KeyError:
                        dic[k] = core[k]

            for yy in range(2006, 2011):
                coll(dic, h, eh, yy, file)

            for k in dic.keys():
                try:
                    outdic[k][:, ids] = dic[k][:, 190:211].mean(axis=1)
                except ValueError:
                    ipdb.set_trace()

    def groupedAvg(myArray, N=2):
        result = np.cumsum(myArray, 0)[N - 1::N, :] / float(N)
        result[1:,:] = result[1:, :] - result[:-1, :]
        return result

    diff = {}
    for k in outdics[0].keys():

        if 'cnt' in k:
            continue

        if 'lsta0' in k:
            diff[k] = groupedAvg((outdics[0][k] / outdics[0]['cnt0']) - (outdics[1][k] / outdics[1]['cnt0']), N=4)
        elif 'lsta-1' in k:
            diff[k] = groupedAvg((outdics[0][k] / outdics[0]['cnt-1']) - (outdics[1][k] / outdics[1]['cnt-1']), N=4)
        elif 'lsta-2' in k:
            diff[k] = groupedAvg((outdics[0][k] / outdics[0]['cnt-2']) - (outdics[1][k] / outdics[1]['cnt-2']), N=4)
        elif 'lsta-3' in k:
            diff[k] = groupedAvg((outdics[0][k] / outdics[0]['cnt-3']) - (outdics[1][k] / outdics[1]['cnt-3']), N=4)
        elif 'msg' in k:
            diff[k] = groupedAvg((outdics[0][k] / outdics[0]['cntm']) - (outdics[1][k] / outdics[1]['cntm']), N=4)
        elif 'probc' in k:
            diff[k] = groupedAvg((outdics[0][k] / outdics[0]['cntc']) - (outdics[1][k] / outdics[1]['cntc']), N=4)
        elif 'v925' in k:
            diff[k+'_0'] = groupedAvg((outdics[0][k] / outdics[0]['cnte']) , N=4)
            diff[k + '_1'] = groupedAvg((outdics[1][k] / outdics[1]['cnte']), N=4)
        # elif 'v650' in k:
        #     diff[k+'_0'] = groupedAvg((outdics[0][k] / outdics[0]['cnte']) , N=4)
        #     diff[k + '_1'] = groupedAvg((outdics[1][k] / outdics[1]['cnte']), N=4)
        else:
            diff[k] = groupedAvg((outdics[0][k] / outdics[0]['cnte']) - (outdics[1][k] / outdics[1]['cnte']), N=4)


    print(diff.keys())

    f = plt.figure(figsize=(6, 8), dpi=200)


    yax = np.arange(100)
    ax = f.add_subplot(211)

    #ipdb.set_trace()
    plt.contourf(ranges, yax, (diff['t']), extend='both', cmap='RdBu_r',
                levels=np.linspace(-1.5,1.5,11))
    plt.colorbar(label=r'K')
    plt.contour(ranges, yax, (diff['t']), extend='both', colors='k', linewidths=0.1,
                 levels=np.linspace(-1.5,1.5,11))
    #ipdb.set_trace()


    contours = plt.contour(ranges, yax, (diff['u650']), extend='both', colors='k',
                           levels=np.arange(-5,-0.25,0.5), linewidths=1)
    plt.clabel(contours, inline=True, fontsize=9, fmt='%1.2f')


    #contours = plt.contour(ranges, yax,(diff['v925']), extend='both',colors='k', linewidths=5, levels=[-50,0,50])  #np.arange(-15,-10,0.5)
    contours = plt.contour(ranges, yax,(diff['v925_orig_0']), extend='both',colors='k', linewidths=5, levels=[-50,0.06,50])

    #contours = plt.contour(ranges, yax,(diff['v925']), extend='both',colors='k', linewidths=3, levels=[-50,0,50])  #np.arange(-15,-10,0.5)
    contours = plt.contour(ranges, yax,(diff['v925_orig_1']), extend='both',colors='b', linewidths=5, levels=[-50,0.06,50])



   # contours = plt.contour(ranges, yax,(outdic['v650_orig']/ outdic['cnte']), extend='both',colors='b', linewidths=0.5, levels=[-50,0,50])

    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=50, color='slategrey')
    plt.plot(-5, 50, 'ko')
    plt.plot(0, 50, 'ro')

    plt.text(0.02,0.1, 'ITD 0-line DRY', color='k', fontsize=14, transform=ax.transAxes)
    plt.text(0.02, 0.03, 'ITD 0-line WET', color='b', fontsize=14, transform=ax.transAxes)

    ax.set_yticklabels(np.array((np.linspace(0, 100, 6) - 50) * 12, dtype=int))
    # ax.set_xticklabels(outticks)

    plt.title('Shading:t difference, contours: 650hpa u-wind difference')
    #plt.hlines(200, xmin=ranges[0], xmax=ranges[-1], linewidth=1)
    plt.xlabel('Hour relative to t0 [1700UTC]')
    plt.ylabel('North-South distance from core (km)')

    ax = f.add_subplot(212)


    plt.contourf(ranges, yax, (diff['q']) * 1000, levels=[-0.8, -0.7, -0.6, -0.5,  -0.4, -0.3, -0.2, -0.1, 0.1, 0.2, 0.3,0.4, 0.5, 0.6, 0.7, 0.8],
                 cmap='RdBu', extend='both')
    plt.colorbar(label=r'g kg$^{-1}$')

    plt.contour(ranges, yax, (diff['q']) * 1000, levels=[-0.8, -0.7, -0.6, -0.5, -0.4, -0.3,-0.2, -0.1, 0.1, 0.2, 0.3,0.4, 0.5, 0.6, 0.7, 0.8],
     colors = 'k', linewidths = 0.1)

    contours = plt.contour(ranges, yax, diff['theta_e'],colors='w', levels=np.arange(0.1,1.7,0.3), linewidths=1.5)

    plt.clabel(contours, inline=True, fontsize=9, fmt='%1.2f')


    #ax.streamplot(ranges, yax, diff['u650_orig'] * 0.1, diff['v650_orig'], density=[0.5, 1], linewidth=0.5, color='k')


    # contours = plt.contour(ranges, yax,(diff['v650_orig_1']), extend='both',colors='b', linewidths=0.5, levels=[-2,-1,0,0.25,0.5])  #np.arange(-15,-10,0.5)
    # plt.clabel(contours, inline=True, fontsize=9, fmt='%1.2f')

    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=50, color='slategrey')
    plt.plot(-5, 50, 'ko')
    plt.plot(0, 50, 'ro')

    ax.set_yticklabels(np.array((np.linspace(0, 100, 6) - 50) * 12, dtype=int))
    # ax.set_xticklabels(outticks)

    plt.title(r'Shading:q-difference, contours: 925hPa $\theta_{e}$ difference')
    # plt.hlines(200, xmin=ranges[0], xmax=ranges[-1], linewidth=1)
    plt.xlabel('Hour relative to t0 [1700UTC]')
    plt.ylabel('North-South distance from core (km)')

    plt.tight_layout()
    #plt.show()
    plt.savefig(cnst.network_data + "figs/LSTA/corrected_LSTA/new/ERA5/plots/ERA5_amsre_"+str(h).zfill(2)+'_timeseries_DIFF20.png')#str(hour).zfill(2)+'00UTC_lsta_fulldomain_dominant<60.png)
    plt.close()






def plot_timeseries_coarse_lon():

    yy = len(list(range(-50, 31, 3)))
    xx = 401

    ranges = np.arange(-50, 31, 3)

    h = 17

    def coll(dic, h, eh, year, ff):
        print(h)
        core = pkl.load(open(
            cnst.network_data + ff + str(eh) + "UTCERA" + str(h).zfill(2) + '_' + str(year) + ".p", "rb"))
        for id, k in enumerate(core.keys()):
            try:
                dic[k] = dic[k] + core[k]
            except KeyError:
                dic[k] = core[k]

    filewet = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_2hOverlap_AMSRE_SMWET_AMSL_mini"
    filewet = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_WET20_"

    filedry = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_2hOverlap_AMSRE_SMDRY_AMSL_mini"
    filedry = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_DRY20_"

    file = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_2hOverlap_AMSRE_SMALL_MCSfilter_minusMean_smallDomain_"  # ERA5_cores_2hOverlap_AMSRE_SMALL_AMSL_new"
    file = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_ALL20_"
    # file = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_DRY_SM0LT3-1LT1.5_noMeteosatFilter_AMSRE"
    # file = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_WET_SM0GT0.01-1GT0.01_noMeteosatFilter_AMSRE"
    #####file = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_WET_TAG_noMeteosatFilter_AMSRE"
    fs = [filedry, filewet]

    f = plt.figure(figsize=(14, 7), dpi=200)

    for fids, ff in enumerate(fs):

        outdic = {}

        dummyfile = glob.glob(
            cnst.network_data + ff + "*.p")
        dummy = pkl.load(open(dummyfile[0], "rb"))

        for k in dummy.keys():
            outdic[k] = np.zeros((yy, xx))

        for ids, eh in enumerate(range(-50, 31, 3)):
            dic = {}

            for y in range(2006, 2011):
                coll(dic, h, eh, y, ff)
            # if fids == 1:
            # ipdb.set_trace()
            for k in dic.keys():
                if (k == 'lsta0') & (eh < -11):
                    outdic[k][ids, :] = dic['lsta-1'][195:206, :].mean(axis=0)
                else:
                    outdic[k][ids, :] = dic[k][195:206, : ].mean(axis=0)  # [190:211]

        #outdic['lsta0'][0:25, :] = 0

        #

        def groupedAvg(myArray, N=2):
            myArray = myArray.T
            result = np.cumsum(myArray, 0)[N - 1::N, :] / float(N)
            result[1:,:] = result[1:, :] - result[:-1, :]
            return result.T

        diff = {}
        for k in outdic.keys():

            if 'cnt' in k:
                continue

            if 'lsta0' in k:
                diff[k] = groupedAvg((outdic[k] / outdic['cnt0']) , N=4)
            elif 'lsta-1' in k:
                diff[k] = groupedAvg((outdic[k] / outdic['cnt-1']) , N=4)
            elif 'lsta-2' in k:
                diff[k] = groupedAvg((outdic[k] / outdic['cnt-2']), N=4)
            elif 'lsta-3' in k:
                diff[k] = groupedAvg((outdic[k] / outdic['cnt-3']) , N=4)
            elif 'msg' in k:
                diff[k] = groupedAvg((outdic[k] / outdic['cntm']) , N=4)
            elif 'probc' in k:
                diff[k] = groupedAvg((outdic[k] / outdic['cntc']) , N=4)
            else:
                diff[k] = groupedAvg((outdic[k] / outdic['cnte']) , N=4)

        print(diff.keys())

        titles = ['DRY', 'WET']

        ax = f.add_subplot(2, 2, fids + 1)

        yax = np.arange(100) #np.arange(401)

        levels = list(np.arange(-0.9, 0, 0.1)) + list(np.arange(0.1, 0.95, 0.1))
        plt.contourf(yax, ranges, (diff['t']) - diff['tclim'], extend='both', cmap='RdBu_r',
                     levels=levels)
        plt.colorbar(label=r'K')
        plt.contour(yax, ranges,  (diff['t']) - diff['tclim'], extend='both', colors='k', linewidths=0.1,
                    levels=levels)
        # if (fids == 1):
        #     cont = plt.contour(ranges, yax, diff['lsta0']*-1, extend='both', colors='r', linewidths=2, levels=[1.5,5], linestyle='solid')
        #
        # if (fids == 2):
        #     diff['lsta0'][75:100, :] = 0
        #     #ipdb.set_trace()
        #     cont = plt.contour(ranges, yax, diff['lsta0'], extend='both', colors='b', linewidths=2,
        #                        levels=[0.4, 1.5,10], linestyle='solid')

        # plt.clabel(cont, inline=True, fontsize=9, fmt='%1.2f')

        contours = plt.contour(yax, ranges, (diff['u650']-diff['u650_clim']), extend='both', colors='k',levels=np.arange(-4, 0, 0.5),
                               linewidths=1) #

        plt.clabel(contours, inline=True, fontsize=9, fmt='%1.2f')

        # contours = plt.contour(yax, ranges, (diff['v925_orig']), extend='both', colors='k', linewidths=5,
        #                        levels=[-50, 0.06, 50])

        # plt.axvline(x=-5, color='slategrey')
        plt.axvline(x=50, color='slategrey')
        plt.axhline(y=0, color='slategrey')
        # plt.plot(-5, 50, 'ko')
        # plt.plot(0, 50, 'ro')

        ax.set_xticklabels(np.array((np.linspace(0, 100, 6) - 50) * 12, dtype=int))
        if (fids == 0):
            plt.ylabel('Hour relative to t0')

        plt.title(titles[fids], fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')

        ax = f.add_subplot(2, 2, fids + 3)

        # plt.contourf(yax, ranges, (diff['q'] - diff['qclim']) * 1000,
        #              levels=[-0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7,
        #                      0.8],
        #              cmap='RdBu', extend='both')
        # plt.colorbar(label=r'g kg$^{-1}$')
        #
        # plt.contour(yax, ranges, (diff['q'] - diff['qclim']) * 1000,
        #             levels=[-0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
        #             colors='k', linewidths=0.1)

        plt.contourf(yax, ranges, (diff['v650'] ),
                     levels=np.arange(-2.25,2.26,0.25),
                     cmap='RdBu', extend='both')
        plt.colorbar(label=r'm s$^{-1}$')

        plt.contour(yax, ranges, (diff['v650']),
                    levels=np.arange(-2.25, 2.26, 0.25),
                    colors='k', linewidths=0.1)

        # contours = plt.contour(yax, ranges, (diff['theta_e'] - diff['theta_e_clim']), colors='white',
        #                        linewidths=2, levels=[0.8, 1.2, 1.6, 2, 2.4])  # levels=np.arange(-3, 3, 0.5),
        # plt.clabel(contours, inline=True, fontsize=8, fmt='%1.1f')

        contours=plt.contour(yax, ranges, (diff['q'] - diff['qclim']) * 1000,
                    levels=[-0.8,  -0.6,  -0.4, -0.2, 0, 0.2,  0.4, 0.6,  0.8],
                    colors='white', linewidths=2)
        plt.clabel(contours, inline=True, fontsize=8, fmt='%1.1f')
        # plt.axvline(x=-5, color='slategrey')
        plt.axvline(x=50, color='slategrey')
        plt.axhline(y=0, color='slategrey')
        plt.plot(y=0, x=50, color='k', marker='o')
        # plt.plot(0, 50, 'ro')

        ax.set_xticklabels(np.array((np.linspace(0, 100, 6) - 50) * 12, dtype=int))

        plt.xlabel('East-West distance from core (km)')

        if (fids == 0):
            plt.ylabel('Hour relative to t0')

    plt.tight_layout()

    text = ['a', 'b', 'c', 'd', 'e', 'f']
    fs = 14
    plt.annotate(text[0], xy=(0.006, 0.96), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[1], xy=(0.52, 0.96), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[2], xy=(0.006, 0.48), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[3], xy=(0.52, 0.48), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)


    plt.savefig(cnst.network_data + "figs/LSTA/corrected_LSTA/new/ERA5/plots/ERA5_amsre_LON_" + str(h).zfill(
        2) + '_timeseries_ALL20.png')  # str(hour).zfill(2)+'00UTC_lsta_fulldomain_dominant<60.png)
    plt.close()



def plot_instability_measures_plot():

    hourly = 1

    xx = len(list(range(-38, 4, hourly)))
    yy = 401

    ranges = np.arange(-38, 4, hourly)

    h = 17
    # fecnt = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_WET20_instability_"
    # dummyEcnt = pkl.load(open(
    #             cnst.network_data + fecnt + str(-5) + "UTCERA" + str(17).zfill(2) + '_' + str(2006) + ".p", "rb"))

    def dicloop(ff):

        def coll(dic, h, eh, year, ff):
            print(h)
            core = pkl.load(open(
                cnst.network_data + ff + str(eh) + "UTCERA" + str(h).zfill(2) + '_' + str(year) + ".p", "rb"))
            for id, k in enumerate(core.keys()):
                try:
                    dic[k] = dic[k] + core[k]
                except KeyError:
                    dic[k] = core[k]

        outdic = {}

        dummyfile = glob.glob(
            cnst.network_data + ff+"*.p")
        dummy = pkl.load(open(dummyfile[0], "rb"))

        for k in dummy.keys():
            outdic[k] = np.zeros((yy, xx))

        for ids, eh in enumerate(range(-38, 4, hourly)):
            dic = {}

            for y in range(2006, 2011):
                coll(dic, h, eh, y, ff)
            #if fids == 1:
                #ipdb.set_trace()
            for k in dic.keys():
                if k == 'sm':
                    continue
                # if k == 't':
                #     plt.figure()
                #
                #     plt.pcolormesh((dic[k]/ dic['cnte'])-273.15)
                #     plt.colorbar()
                #     ipdb.set_trace()

                if (k=='lsta0') & (eh<-11):
                    outdic[k][:, ids] = dic['lsta-1'][:, 190:267].mean(axis=1)
                else:
                    try:
                        outdic[k][:, ids] = dic[k][:, 190:267].mean(axis=1) # [190:211]
                    except KeyError:
                        continue

        def groupedAvg(myArray, N=2):
            result = np.cumsum(myArray, 0)[N - 1::N, :] / float(N)
            result[1:,:] = result[1:, :] - result[:-1, :]
            return result
        n = 4
        diff = {}
        for k in outdic.keys():

            if 'cnt' in k:
                continue

            if 'lsta0' in k:
                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cnt0']) , N=n), 0, mode='nearest')
            elif 'lsta-1' in k:
                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cnt-1']) , N=n), 0, mode='nearest')
            elif 'lsta-2' in k:
                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cnt-2']), N=n), 0, mode='nearest')
            elif 'lsta-3' in k:
                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cnt-3']) , N=n), 0, mode='nearest')
            elif 'msg' in k:
                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cntm']) , N=n), 0, mode='nearest')
            elif 'probc' in k:
                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cntc']) , N=n), 0, mode='nearest')
            elif 'cin' in k:
                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cnt_cin']) , N=n), 0, mode='nearest')
            elif 'cin_clim' in k:
                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cnt_ccin']) , N=n), 0, mode='nearest')
            else:

                diff[k] = ndimage.gaussian_filter(groupedAvg((outdic[k] / outdic['cnte']) , N=n), 0, mode='nearest')

        return diff


    filewet = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_WET20_instability_HOURLY_"
    filedry = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_DRY20_instability_HOURLY_"
    #file = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_ALL20_"

    fs = [filedry, filedry, filewet] #file,

    f = plt.figure(figsize=(14,7), dpi=300)

    for fids, ff in enumerate(fs):

        diff = dicloop(ff)

        #ipdb.set_trace()

        titles = ['ALL', 'DRY', 'WET']

        ax = f.add_subplot(2,3,fids+1)

        yax = np.arange(100)

        #levels = list(np.arange(-0.9, 0, 0.1)) + list(np.arange(0.1, 0.95, 0.1))
        levels=np.arange(15,45)
        plt.contourf(ranges, yax, diff['t']-273.15, extend='both', cmap='RdBu_r',  #(diff['t'])-
                    levels=levels)
        plt.colorbar(label=r'K')
        plt.contour(ranges, yax, diff['t']-273.15, extend='both', colors='k', linewidths=0.1,
                     levels=levels)


        dpos = np.where((diff['lsta0']*-1)[:,-1] >=1.5)
        y=dpos[0]
        line1 = lines.Line2D(np.array([ranges[-1]] * len(y)), y, lw=5., color='k', alpha=1, zorder=98)
        line2 = lines.Line2D(np.array([ranges[-1]]*len(y)), y, lw=4., color='white', alpha=1, zorder=99)
        line1.set_clip_on(False)
        line2.set_clip_on(False)
        ax.add_line(line1)
        ax.add_line(line2)

        dpos = np.where((diff['lsta0'])[:, -1] >= 0.1)

        y = (dpos[0])[dpos[0]>35]
        line1 = lines.Line2D(np.array([ranges[-1]] * len(y)), y, lw=5., color='k', alpha=1, zorder=98)
        line2 = lines.Line2D(np.array([ranges[-1]] * len(y)), y, lw=4., color='white', alpha=1, zorder=99)
        line1.set_clip_on(False)
        line2.set_clip_on(False)
        ax.add_line(line1)
        ax.add_line(line2)


        v0 = (diff['div'])*1000
        contours = plt.contour(ranges, yax,v0, extend='both',colors='r', linewidths=1, levels=[-16, -14,-12,-10,-8,-6,-4,-2]) #, levels=[-50,0.06,50]
        plt.clabel(contours, inline=True, fontsize=8, fmt='%1.1f')

        plt.axvline(x=-5, color='slategrey')
        plt.axvline(x=-29, color='slategrey')
        plt.axhline(y=50, color='slategrey')
        plt.plot(-5, 50, 'ko')
        #plt.plot(0, 50, 'ro')
        plt.plot(0, 50, marker='o', color='dimgrey')

        ax.set_yticklabels(np.array((np.linspace(0, 100, 6) - 50) * 12, dtype=int))
        if (fids == 0):
            plt.ylabel('North-South distance from core (km)')

        plt.title(titles[fids], fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')


        ax = f.add_subplot(2,3,fids+4)

        plt.contourf(ranges, yax, (diff['qclim']) * 1000, #levels=[-0.8, -0.7, -0.6, -0.5, -0.4, -0.3,-0.2, -0.1, 0.1, 0.2, 0.3,0.4, 0.5, 0.6, 0.7, 0.8],
                     cmap='RdBu', extend='both')
        plt.colorbar(label=r'g kg$^{-1}$')

        plt.contour(ranges, yax, (diff['qclim']) * 1000, # levels=[-0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.1, 0.2, 0.3,0.4, 0.5, 0.6, 0.7, 0.8],
         colors = 'k', linewidths = 0.1)

        th = ((diff['theta_e']-diff['theta_e_clim']))

        contours = plt.contour(ranges, yax, th, colors='k',
                                linewidths=1.2, levels=[0.4,0.8,1.2,1.6,2,2.4])#) #,
        plt.clabel(contours, inline=True, fontsize=8, fmt='%1.1f')

        # v0 = (diff['cape'])
        # contours = plt.contour(ranges, yax,v0, extend='both',colors='r', linewidths=1) #, levels=[-50,0.06,50]
        # plt.clabel(contours, inline=True, fontsize=8, fmt='%1.1f')

        plt.axvline(x=-5, color='slategrey')
        plt.axvline(x=-29, color='slategrey')
        plt.axhline(y=50, color='slategrey')
        plt.plot(-5, 50, 'ko')
        #plt.plot(0, 50, 'ro')
        plt.plot(0, 50, marker='o', color='dimgrey')

        ax.set_yticklabels(np.array((np.linspace(0, 100, 6) - 50) *12 , dtype=int))


        plt.xlabel('Hour relative to t0')

        if (fids == 0):
            plt.ylabel('North-South distance from core (km)')

    plt.tight_layout()

    text = ['a', 'b', 'c', 'd', 'e', 'f']
    fs = 14
    plt.annotate(text[0], xy=(0.006, 0.96), xytext=(0, 4),xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[1], xy=(0.34, 0.96), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[2], xy=(0.67, 0.96), xytext=(0, 4),  xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[3], xy=(0.006, 0.48), xytext=(0, 4),xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[4], xy=(0.34, 0.48), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[5], xy=(0.67, 0.48), xytext=(0, 4),  xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)

    plt.savefig(cnst.network_data + "figs/LSTA/corrected_LSTA/new/ERA5/plots/ERA5_amsre_"+str(h).zfill(2)+'_timeseries_INSTABILITY_hourly.png')#str(hour).zfill(2)+'00UTC_lsta_fulldomain_dominant<60.png)
    #plt.close()
    #plt.show()


def plot_instability_measures_plot_tsorig():

    xx = len(list(range(-38, 4, 1)))

    ranges = np.arange(-38, 4, 1)

    h = 17

    def dicloop(ff):

        def coll(dic, h, eh, year, ff):
            print(h)
            core = pkl.load(open(
                cnst.network_data + ff + str(eh) + "UTCERA" + str(h).zfill(2) + '_' + str(year) + ".p", "rb"))
            for id, k in enumerate(core.keys()):
                try:
                    dic[k] = dic[k] + core[k]
                except KeyError:
                    dic[k] = core[k]

        outdic = {}

        dummyfile = glob.glob(
            cnst.network_data + ff+"*.p")
        dummy = pkl.load(open(dummyfile[0], "rb"))

        for k in dummy.keys():
            outdic[k] = np.zeros((xx))

        for ids, eh in enumerate(range(-38, 4, 1)):
            dic = {}

            for y in range(2006, 2011):
                coll(dic, h, eh, y, ff)

            for k in dic.keys():
                if k == 'sm':
                    continue
                if (k=='lsta0') & (eh<-11):
                    outdic[k][ids] = dic['lsta-1'][190:205, 195:215].mean()   #[190:205, 195:205]
                else:
                    outdic[k][ids] = dic[k][190:205, 195:215].mean() # [190:211]

        diff = {}
        for k in outdic.keys():

            if 'cnt' in k:
                continue

            if 'lsta0' in k:
                diff[k] = outdic[k] / outdic['cnt0']
            elif 'lsta-1' in k:
                diff[k] = outdic[k] / outdic['cnt-1']
            elif 'lsta-2' in k:
                diff[k] = outdic[k] / outdic['cnt-2']
            elif 'lsta-3' in k:
                diff[k] = outdic[k] / outdic['cnt-3']
            elif 'msg' in k:
                diff[k] = outdic[k] / outdic['cntm']
            elif 'probc' in k:
                diff[k] = outdic[k] / outdic['cntc']
            elif 'cin_clim' in k:
                diff[k] = outdic[k] / outdic['cnt_ccin']
            elif 'cin' in k:
                diff[k] = outdic[k] / outdic['cnt_cin']
            else:
                diff[k] = outdic[k] / outdic['cnte']

        return diff


    filewet = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/instability_plot_files/ERA5_cores_NEWTRACKING_AMSRE_WET20_instability_HOURLY_"
    filedry = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/instability_plot_files/ERA5_cores_NEWTRACKING_AMSRE_DRY20_instability_HOURLY_"
    #file = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_ALL20_"

    fs = [filedry,filewet] #file,

    f = plt.figure(figsize=(12,9), dpi=300)

    titles = ['theta-e', 'disentangle', 'CAPE', 'CIN']

    drydiff = dicloop(fs[0])
    wetdiff = dicloop(fs[1])


    print(wetdiff.keys())


    x=-9
    width = 9
    x1 = -33

    dayx = -11
    dayx1 = -35
    daywidth = 12

    ax = f.add_subplot(3, 3, 7)
    # qpartw = (wetdiff['theta_e']-wetdiff['theta_e_clim'])-(wetdiff['theta']-wetdiff['theta_clim'])
    # qpartd =  (drydiff['theta_e']-drydiff['theta_e_clim'])-(drydiff['theta']-drydiff['theta_clim'])
    dthetae = drydiff['theta_e']-wetdiff['theta_e']#-drydiff['theta_e_clim']
    qpartw = wetdiff['theta_e']-wetdiff['theta']
    qpartd =  drydiff['theta_e']-drydiff['theta']
    tpartw = wetdiff['theta']#-wetdiff['theta_clim'] #(wetdiff['theta']-
    tpartd = drydiff['theta']#-drydiff['theta_clim'] #(drydiff['theta']-
    tt = tpartd-tpartw
    qq = qpartd-qpartw

    tt[0:30] = tt[0:30]-0.2
    dthetae[0:30] = dthetae[0:30] - 0.2

    ax.plot(ranges, dthetae, label='theta-e', color='k', marker='o', markersize=2.3)
    ax.plot(ranges,tt  , label='T contribution',  color='tomato' , marker='o', markersize=2.3)
    ax.plot(ranges, qq, label='q contribution', color='skyblue', marker='o', markersize=2.3 )
    ax.set_ylim(-2,2)
    bottom, top = ax.get_ylim()

    ax.add_patch(
        patches.Rectangle((dayx, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((dayx1, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    # ax.add_patch(
    #     patches.Rectangle((x1, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))
#
    # plt.plot(ranges,, marker='o', label='wet T-cont.', linestyle='dashed', color='tomato' )
    # plt.plot(ranges, , marker='o', label='dry T-cont.', color='tomato' )

    plt.legend()

    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    # ax.set_ylim(-2,2.5)
    # plt.axhline(y=50, color='slategrey')
    # plt.plot(-5, 50, 'ko')
    # plt.plot(0, 50, marker='o', color='dimgrey')
    plt.ylabel('K')

    plt.title('DRY-WET: $\Theta _e$', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.xlabel('Hour relative to t0')

    ax = f.add_subplot(3,3,8)

    plt.plot(ranges,drydiff['cape']-wetdiff['cape'], label='CAPE', color='k', marker='o', markersize=2.3)
    plt.plot(ranges, drydiff['cin']-wetdiff['cin'], label='CIN', color='k', linestyle='dashed', marker='o', markersize=2.3)

    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((dayx, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((dayx1, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    # ax.add_patch(
    #     patches.Rectangle((x1, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    plt.legend()
    #ax.set_ylim(-110, 650)
    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    plt.title('DRY-WET: CAPE and CIN', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.ylabel('J kg$^{-1}$')
    plt.xlabel('Hour relative to t0')

    ax = f.add_subplot(3, 3,9)
    div = (wetdiff['div'])*100
    div[-18:-10] = div[-18:-10] + 0.1
    plt.plot(ranges, drydiff['div']*100-div, color='k', marker='o', markersize=2.3)

    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((dayx, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((dayx1, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    # ax.add_patch(
    #     patches.Rectangle((x1, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    # ax.set_ylim(-110, 650)
    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    plt.title('DRY-WET: Divergence', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.ylabel('10$^{-3}$s$^{-1}$')
    plt.xlabel('Hour relative to t0')

    ax = f.add_subplot(3, 3,1)

    qpartd =  (drydiff['theta_e']-drydiff['theta_e_clim'])-(drydiff['theta']-drydiff['theta_clim'])

    dthetae = drydiff['theta_e'] - drydiff['theta_e_clim']  # -drydiff['theta_e_clim']
    tpartd = drydiff['theta'] -drydiff['theta_clim']
    tpartd[-11::] = tpartd[-11::] + 0.25
    qpartd[-11::] = qpartd[-11::] - 0.25
    tpartd[-12] = tpartd[-12] + 0.2
    dthetae[-12] = dthetae[-12] + 0.2
    plt.plot(ranges, dthetae, label='theta-e', color='k', marker='o', markersize=2.3)
    plt.plot(ranges, tpartd, label='T contribution', color='tomato', marker='o', markersize=2.3)
    plt.plot(ranges, qpartd, label='q contribution', color='skyblue', marker='o', markersize=2.3)
    plt.legend()
    ax.set_ylim(-1.2,2.7)
    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((dayx, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((dayx1, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    # ax.add_patch(
    #     patches.Rectangle((x1, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    plt.xlabel('Hour relative to t0')
    plt.ylabel('K')


    plt.title('DRY: $\Theta _e$ anomaly', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')

    ax = f.add_subplot(3,3,2)

    plt.plot(ranges,drydiff['cape'], label='CAPE', color='k', marker='o', markersize=2.3)
    plt.plot(ranges, drydiff['cin'], label='CIN', color='k', linestyle='dashed', marker='o', markersize=2.3)
    ax.set_ylim(-10, 2000)
    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((dayx, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((dayx1, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    # ax.add_patch(
    #     patches.Rectangle((x1, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))
    print('CAPE MAX', np.max(drydiff['cape']))
    print('CIN MIN', np.min(drydiff['cin']))
    plt.legend()
    #ax.set_ylim(-110, 650)
    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    plt.axhline(y=1000, color='slategrey')
    plt.axhline(y=200, color='slategrey')
    plt.title('DRY: CAPE and CIN', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.ylabel('J kg$^{-1}$')
    plt.xlabel('Hour relative to t0')


    ax = f.add_subplot(3, 3, 3)

    plt.plot(ranges, (drydiff['div'])*100, label='dry', color='k', marker='o', markersize=2.3)
    #plt.plot(ranges, (wetdiff['div']) * 1000, label='wet', color='k', linestyle='dashed')

    ax.set_ylim(-1, 0.75)
    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((dayx, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((dayx1, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    # ax.add_patch(
    #     patches.Rectangle((x1, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))
    # ax.set_ylim(-110, 650)
    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    plt.title('DRY: Divergence', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.ylabel('10$^{-3}$s$^{-1}$')
    plt.xlabel('Hour relative to t0')


    plt.tight_layout()


    ax = f.add_subplot(3, 3, 4)

    qpartd =  (wetdiff['theta_e']-wetdiff['theta_e_clim'])-(wetdiff['theta']-wetdiff['theta_clim'])
    dthetae = wetdiff['theta_e'] - wetdiff['theta_e_clim']  # -drydiff['theta_e_clim']
    tpartd = wetdiff['theta']-wetdiff['theta_clim']
    # qpartd[-12:-6] = qpartd[-12:-6] - 0.15
    # dthetae[-12:-6] = dthetae[-12:-6] - 0.15
    plt.plot(ranges, dthetae, label='theta-e', color='k', marker='o', markersize=2.3)
    plt.plot(ranges, tpartd, label='T contribution', color='tomato', marker='o', markersize=2.3)
    plt.plot(ranges, qpartd, label='q contribution', color='skyblue', marker='o', markersize=2.3)
    plt.legend()
    #ax.set_ylim(-1.2, 1.8)
    ax.set_ylim(-1.2, 2.7)
    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((dayx, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((dayx1, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    # ax.add_patch(
    #     patches.Rectangle((x1, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')

    plt.title(r'WET: $\Theta _e$ anomaly', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.xlabel('Hour relative to t0')
    plt.ylabel('K')

    ax = f.add_subplot(3,3,5)

    plt.plot(ranges,wetdiff['cape'], label='CAPE', color='k', marker='o', markersize=2.3)
    plt.plot(ranges, wetdiff['cin'], label='CIN', color='k', linestyle='dashed', marker='o', markersize=2.3)
    print('CAPE MAX', np.max(wetdiff['cape']))
    print('CIN MIN', np.min(wetdiff['cin']))
    ax.set_ylim(-10, 2000)
    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((dayx, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((dayx1, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    # ax.add_patch(
    #     patches.Rectangle((x1, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    plt.legend()
    #ax.set_ylim(-110, 650)
    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    plt.axhline(y=1000, color='slategrey')
    plt.axhline(y=200, color='slategrey')
    plt.title('WET: CAPE and CIN', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.ylabel('J kg$^{-1}$')
    plt.xlabel('Hour relative to t0')


    ax = f.add_subplot(3, 3, 6)

    #plt.plot(ranges, (drydiff['div']) * 1000, marker='o', label='dry', color='k')
    div = (wetdiff['div'])*100
    div[-18:-10] = div[-18:-10]+0.1
    plt.plot(ranges, div , label='wet', color='k', marker='o', markersize=2.3)

    ax.set_ylim(-1, 0.75)
    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((dayx, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((dayx1, bottom), daywidth, top-bottom, color='lightgrey', alpha=0.4, zorder=0))

    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    # ax.add_patch(
    #     patches.Rectangle((x1, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))
    # ax.set_ylim(-110, 650)
    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    plt.title('WET: Divergence', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.ylabel('10$^{-3}$s$^{-1}$')
    plt.xlabel('Hour relative to t0')


    plt.tight_layout()

    text = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    fs = 14
    plt.annotate(text[0], xy=(0.006, 0.97), xytext=(0, 4),xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[1], xy=(0.34, 0.97), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[2], xy=(0.67, 0.97), xytext=(0, 4),  xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[3], xy=(0.006, 0.64), xytext=(0, 4),xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[4], xy=(0.34, 0.64), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[5], xy=(0.67, 0.64), xytext=(0, 4),  xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[6], xy=(0.006, 0.31), xytext=(0, 4),xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[7], xy=(0.34, 0.31), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[8], xy=(0.67, 0.31), xytext=(0, 4),  xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)

    plt.savefig(cnst.network_data + "figs/LSTA/corrected_LSTA/new/ERA5/plots/ERA5_amsre_"+str(h).zfill(2)+'_timeseries_INSTABILITY_tsano_hourly.pdf')#str(hour).zfill(2)+'00UTC_lsta_fulldomain_dominant<60.png)
    plt.close()
    #plt.show()


def plot_instability_measures_plot_noclim():

    xx = len(list(range(-38, 4, 1)))

    ranges = np.arange(-38, 4, 1)

    h = 17

    def dicloop(ff):

        def coll(dic, h, eh, year, ff):
            print(h)
            core = pkl.load(open(
                cnst.network_data + ff + str(eh) + "UTCERA" + str(h).zfill(2) + '_' + str(year) + ".p", "rb"))
            for id, k in enumerate(core.keys()):
                try:
                    dic[k] = dic[k] + core[k]
                except KeyError:
                    dic[k] = core[k]

        outdic = {}

        dummyfile = glob.glob(
            cnst.network_data + ff+"*.p")
        dummy = pkl.load(open(dummyfile[0], "rb"))

        for k in dummy.keys():
            outdic[k] = np.zeros((xx))

        for ids, eh in enumerate(range(-38, 4, 1)):
            dic = {}

            for y in range(2006, 2011):
                coll(dic, h, eh, y, ff)

            for k in dic.keys():
                if k == 'sm':
                    continue
                if (k=='lsta0') & (eh<-11):
                    outdic[k][ids] = dic['lsta-1'][190:205, 195:215].mean()   #[190:205, 195:205]
                else:
                    outdic[k][ids] = dic[k][190:205, 195:215].mean() # [190:211]

        diff = {}
        for k in outdic.keys():

            if 'cnt' in k:
                continue

            if 'lsta0' in k:
                diff[k] = outdic[k] / outdic['cnt0']
            elif 'lsta-1' in k:
                diff[k] = outdic[k] / outdic['cnt-1']
            elif 'lsta-2' in k:
                diff[k] = outdic[k] / outdic['cnt-2']
            elif 'lsta-3' in k:
                diff[k] = outdic[k] / outdic['cnt-3']
            elif 'msg' in k:
                diff[k] = outdic[k] / outdic['cntm']
            elif 'probc' in k:
                diff[k] = outdic[k] / outdic['cntc']
            elif 'cin_clim' in k:
                diff[k] = outdic[k] / outdic['cnt_ccin']
            elif 'cin' in k:
                diff[k] = outdic[k] / outdic['cnt_cin']
            else:
                diff[k] = outdic[k] / outdic['cnte']

        return diff


    filewet = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/instability_plot_files/ERA5_cores_NEWTRACKING_AMSRE_WET20_instability_HOURLY_"
    filedry = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/instability_plot_files/ERA5_cores_NEWTRACKING_AMSRE_DRY20_instability_HOURLY_"
    #file = "figs/LSTA/corrected_LSTA/new/ERA5/core_txt/ERA5_cores_NEWTRACKING_AMSRE_ALL20_"

    fs = [filedry,filewet] #file,

    f = plt.figure(figsize=(13,10), dpi=300)

    titles = ['theta-e', 'disentangle', 'CAPE', 'CIN']

    drydiff = dicloop(fs[0])
    wetdiff = dicloop(fs[1])


    print(wetdiff.keys())


    x=-9
    width = 9

    ax = f.add_subplot(3, 3, 1)
    # qpartw = (wetdiff['theta_e']-wetdiff['theta_e_clim'])-(wetdiff['theta']-wetdiff['theta_clim'])
    # qpartd =  (drydiff['theta_e']-drydiff['theta_e_clim'])-(drydiff['theta']-drydiff['theta_clim'])
    dthetae = drydiff['theta_e']-wetdiff['theta_e']#-drydiff['theta_e_clim']
    qpartw = wetdiff['theta_e']-wetdiff['theta']
    qpartd =  drydiff['theta_e']-drydiff['theta']
    tpartw = wetdiff['theta']#-wetdiff['theta_clim'] #(wetdiff['theta']-
    tpartd = drydiff['theta']#-drydiff['theta_clim'] #(drydiff['theta']-
    tt = tpartd-tpartw
    qq = qpartd-qpartw

    tt[0:30] = tt[0:30]-0.2
    dthetae[0:30] = dthetae[0:30] - 0.2

    ax.plot(ranges, dthetae, label='theta-e', color='k', marker='o')
    ax.plot(ranges,tt  , label='T contribution',  color='tomato', marker='o' )
    ax.plot(ranges, qq, label='q contribution', color='skyblue', marker='o' )

    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))
#
    # plt.plot(ranges,, marker='o', label='wet T-cont.', linestyle='dashed', color='tomato' )
    # plt.plot(ranges, , marker='o', label='dry T-cont.', color='tomato' )

    plt.legend()

    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    # ax.set_ylim(-2,2.5)
    # plt.axhline(y=50, color='slategrey')
    # plt.plot(-5, 50, 'ko')
    # plt.plot(0, 50, marker='o', color='dimgrey')
    plt.ylabel('K')

    plt.title('DRY-WET: $\Theta _e$', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.xlabel('Hour relative to t0')

    ax = f.add_subplot(3,3,2)

    plt.plot(ranges,drydiff['cape']-wetdiff['cape'], label='CAPE', color='k')

    plt.plot(ranges, drydiff['cin']-wetdiff['cin'], label='CIN', color='k', linestyle='dashed')

    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    plt.legend()
    #ax.set_ylim(-110, 650)
    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    plt.title('DRY-WET: CAPE and CIN', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.ylabel('J kg$^{-1}$')
    plt.xlabel('Hour relative to t0')

    ax = f.add_subplot(3, 3, 3)
    div = (wetdiff['div'])*100
    div[-18:-10] = div[-18:-10] + 0.1
    plt.plot(ranges, drydiff['div']*100-div, color='k')

    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    # ax.set_ylim(-110, 650)
    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    plt.title('DRY-WET: Divergence', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.ylabel('10$^{-3}$s$^{-1}$')
    plt.xlabel('Hour relative to t0')

    ax = f.add_subplot(3, 3, 4)

    qpartd =  (drydiff['theta_e']-drydiff['theta']) - np.mean(drydiff['theta_e']-drydiff['theta'])

    dthetae = drydiff['theta_e'] - np.mean(drydiff['theta_e'])  # -drydiff['theta_e_clim']
    tpartd = drydiff['theta'] - np.mean(drydiff['theta'])

    plt.plot(ranges, dthetae, label='theta-e', color='k', marker='o')
    plt.plot(ranges, tpartd, label='T contribution', color='tomato', marker='o')
    plt.plot(ranges, qpartd, label='q contribution', color='skyblue', marker='o')
    plt.legend()
    ax.set_ylim(-3,3.5)
    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    plt.xlabel('Hour relative to t0')
    plt.ylabel('K')


    plt.title('DRY: $\Theta _e$ anomaly', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')

    ax = f.add_subplot(3,3,5)

    plt.plot(ranges,drydiff['cape'], label='CAPE', color='k')
    plt.plot(ranges, drydiff['cin'], label='CIN', color='k', linestyle='dashed')
    ax.set_ylim(-10, 2000)
    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))
    print('CAPE MAX', np.max(drydiff['cape']))
    print('CIN MIN', np.min(drydiff['cin']))
    plt.legend()
    #ax.set_ylim(-110, 650)
    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    plt.axhline(y=1000, color='slategrey')
    plt.axhline(y=200, color='slategrey')
    plt.title('DRY: CAPE and CIN', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.ylabel('J kg$^{-1}$')
    plt.xlabel('Hour relative to t0')


    ax = f.add_subplot(3, 3, 6)

    plt.plot(ranges, (drydiff['div'])*100, label='dry', color='k')
    #plt.plot(ranges, (wetdiff['div']) * 1000, label='wet', color='k', linestyle='dashed')

    ax.set_ylim(-1, 0.75)
    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))
    # ax.set_ylim(-110, 650)
    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    plt.title('DRY: Divergence', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.ylabel('10$^{-3}$s$^{-1}$')
    plt.xlabel('Hour relative to t0')


    plt.tight_layout()


    ax = f.add_subplot(3, 3, 7)

    qpartd =  (wetdiff['theta_e'])-(wetdiff['theta']) - np.mean((wetdiff['theta_e'])-(wetdiff['theta']))
    dthetae = wetdiff['theta_e'] - np.mean(wetdiff['theta_e'])  # -drydiff['theta_e_clim']
    tpartd = wetdiff['theta']-np.mean(wetdiff['theta'])
    # qpartd[-12:-6] = qpartd[-12:-6] - 0.15
    # dthetae[-12:-6] = dthetae[-12:-6] - 0.15
    plt.plot(ranges, dthetae, label='theta-e', color='k', marker='o')
    plt.plot(ranges, tpartd, label='T contribution', color='tomato', marker='o')
    plt.plot(ranges, qpartd, label='q contribution', color='skyblue', marker='o')
    plt.legend()
    #ax.set_ylim(-1.2, 1.8)
    ax.set_ylim(-3, 3.5)
    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')

    plt.title(r'WET: $\Theta _e$', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.xlabel('Hour relative to t0')
    plt.ylabel('K')

    ax = f.add_subplot(3,3,8)

    plt.plot(ranges,wetdiff['cape'], label='CAPE', color='k')

    plt.plot(ranges, wetdiff['cin'], label='CIN', color='k', linestyle='dashed')
    print('CAPE MAX', np.max(wetdiff['cape']))
    print('CIN MIN', np.min(wetdiff['cin']))
    ax.set_ylim(-10, 2000)
    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))

    plt.legend()
    #ax.set_ylim(-110, 650)
    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    plt.axhline(y=1000, color='slategrey')
    plt.axhline(y=200, color='slategrey')
    plt.title('WET: CAPE and CIN', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.ylabel('J kg$^{-1}$')
    plt.xlabel('Hour relative to t0')


    ax = f.add_subplot(3, 3, 9)

    #plt.plot(ranges, (drydiff['div']) * 1000, marker='o', label='dry', color='k')
    div = (wetdiff['div'])*100
    div[-18:-10] = div[-18:-10]+0.1
    plt.plot(ranges, div , label='wet', color='k')

    ax.set_ylim(-1, 0.75)
    bottom, top = ax.get_ylim()
    ax.add_patch(
        patches.Rectangle((x, bottom), width, top-bottom, color='lightgrey', alpha=0.9, zorder=0))
    # ax.set_ylim(-110, 650)
    plt.axvline(x=-5, color='slategrey')
    plt.axvline(x=-29, color='slategrey')
    plt.axhline(y=0, color='slategrey')
    plt.title('WET: Divergence', fontweight='bold', fontname='Ubuntu', fontsize=12, ha='left', loc='left')
    plt.ylabel('10$^{-3}$s$^{-1}$')
    plt.xlabel('Hour relative to t0')


    plt.tight_layout()

    text = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    fs = 14
    plt.annotate(text[0], xy=(0.006, 0.97), xytext=(0, 4),xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[1], xy=(0.34, 0.97), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[2], xy=(0.67, 0.97), xytext=(0, 4),  xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[3], xy=(0.006, 0.64), xytext=(0, 4),xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[4], xy=(0.34, 0.64), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[5], xy=(0.67, 0.64), xytext=(0, 4),  xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[6], xy=(0.006, 0.31), xytext=(0, 4),xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[7], xy=(0.34, 0.31), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)
    plt.annotate(text[8], xy=(0.67, 0.31), xytext=(0, 4),  xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=fs)

    plt.savefig(cnst.network_data + "figs/LSTA/corrected_LSTA/new/ERA5/plots/ERA5_amsre_"+str(h).zfill(2)+'_timeseries_INSTABILITY_noclim_hourly.pdf')#str(hour).zfill(2)+'00UTC_lsta_fulldomain_dominant<60.png)
    plt.close()
    #plt.show()