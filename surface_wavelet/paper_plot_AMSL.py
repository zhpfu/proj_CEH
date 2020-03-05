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
from matplotlib.gridspec import GridSpec
import collections

matplotlib.rc('xtick', labelsize=10)
matplotlib.rc('ytick', labelsize=10)
matplotlib.rcParams['hatch.linewidth'] = 0.1
from scipy.ndimage.measurements import label
from scipy import ndimage


def run_all():
    for h in [15,16,17,18,19,20,21, 22,23,0,1,2,3,4,5,6,7]:  #,22,23,0,1,2,3,4,5,6,7
        plot_map_AMSRE(h)


def plot_map_AMSRE(hour):

    path = cnst.network_data + 'figs/LSTA/corrected_LSTA/new/wavelet_coefficients'
    key = '2hOverlap'
    dic = pkl.load(open(path+"/coeffs_nans_stdkernel_USE_"+str(hour)+"UTC_15000_2dAMSL_mini_day+1_DRY_" + (key) + ".p", "rb")) #UTC_15000_ALL_-60_5slotSmall

    lsta = (dic['lsta'])[0] / dic['lsta'][1]
    amsr = (dic['amsr'])[0] / dic['amsr'][1]

    cores = dic['cores']

    lcnt = dic['lsta'][1]
    acnt = dic['amsr'][1]

    dist=100
    llevels = np.array(list(np.arange(-0.8, 0, 0.1)) + list(np.arange(0.1, 0.81, 0.1)))#*12000
    alevels = np.array(list(np.arange(-2.5, 0, 0.25)) + list(np.arange(0.25, 2.51, 0.25)))#*12000

    #
    # llevels = np.array(list(np.arange(-1.6, 0, 0.2)) + list(np.arange(0.2, 1.61, 0.2)))#*12000  WET
    # alevels = np.array(list(np.arange(-3, 0, 0.25)) + list(np.arange(0.25, 3.25, 0.25)))#*12000

    # llevels = np.array(list(np.arange(-1, 0, 0.2)) + list(np.arange(0.2, 1.01, 0.2)))#*12000 DRY
    # alevels = np.array(list(np.arange(-4, 0, 0.5)) + list(np.arange(0.5, 4.5, 0.5)))#*12000

    f = plt.figure(figsize=(12, 9), dpi=200)
    ax = f.add_subplot(221)

    plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, (np.arange(0, 2*dist+1) - dist) * 3 , lsta , cmap='RdBu_r', extend='both', levels=llevels)
    plt.colorbar(label='K')
    cs = plt.contour((np.arange(0, 2*dist+1) - dist) * 3, (np.arange(0, 2*dist+1) - dist) * 3 , amsr , colors='k', linewidths=1, linestyles=['dotted'])
    plt.clabel(cs, inline=1, fontsize=8, fmt="%1.1f")
    ax.plot(0,0, 'bo')
    ax.set_xlabel('km')
    ax.set_ylabel('km')
    plt.axvline(x=0, linestyle='dashed', color='k',linewidth=1)
    plt.axhline(y=0, linestyle='dashed', color='k', linewidth=1)

    plt.title('LSTA | Nb cores: ' + str(cores) + '| ' + str(hour).zfill(2) + '00UTC',
              fontsize=10)

    ax = f.add_subplot(222)

    plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, (np.arange(0, 2*dist+1) - dist) * 3 , amsr , cmap='RdBu', extend='both', levels=alevels)
    plt.colorbar(label='%')
    # plt.contour((np.arange(0, 2 * dist + 1) - dist) * 3, (np.arange(0, 2 * dist + 1) - dist) * 3, lsta, colors='k',
    #             linewidths=0.8, linestyles=['dashed'])


    ax.plot(0,0, 'bo')
    ax.set_xlabel('km')
    ax.set_ylabel('km')
    plt.axvline(x=0, linestyle='dashed', color='k', linewidth=1)
    plt.axhline(y=0, linestyle='dashed', color='k', linewidth=1)
    plt.title('AMSRE| Nb cores: ' + str(cores) + '| ' + str(hour).zfill(2) + '00UTC', fontsize=10)

    ax = f.add_subplot(223)

    plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, (np.arange(0, 2*dist+1) - dist) * 3 , lcnt, cmap='RdBu_r', extend='both')
    plt.plot(0,0,'bo')
    plt.colorbar(label='')
    #plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, (np.arange(0, 2*dist+1) - dist) * 3, mask[0,:,:], colors='none', hatches='.', levels = [0.5,1], linewidth=0.25)
    plt.axvline(x=0, linestyle='dashed', color='k', linewidth=1)
    plt.axhline(y=0, linestyle='dashed', color='k', linewidth=1)
    ax.set_xlabel('km')
    ax.set_ylabel('km')
    plt.title('LSTA: Number valid pixels')


    ax = f.add_subplot(224)

    plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, (np.arange(0, 2*dist+1) - dist) * 3 , acnt, cmap='RdBu_r', extend='both')
    plt.plot(0,0,'bo')
    plt.colorbar(label='')
    #plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, (np.arange(0, 2*dist+1) - dist) * 3, mask[0,:,:], colors='none', hatches='.', levels = [0.5,1], linewidth=0.25)
    plt.axvline(x=0, linestyle='dashed', color='k', linewidth=1)
    plt.axhline(y=0, linestyle='dashed', color='k', linewidth=1)
    ax.set_xlabel('km')
    ax.set_ylabel('km')
    plt.title('AMSRE: Number valid pixels')


    plt.tight_layout()
    #plt.savefig(path + '/amsreVSlsta/wcoeff_maps_all_AMSL_SMFINITE_'+str(hour).zfill(2)+'.png')
    #plt.show()
    #plt.close('all')


def plot_amsr_lsta_only(hour):

    path = cnst.network_data + 'figs/LSTA/corrected_LSTA/new/wavelet_coefficients/'
    key = '2hOverlap'
    dic = pkl.load(open(path+"/coeffs_nans_stdkernel_USE_"+str(hour)+"UTC_15000_2dAMSL_mini_day-1_DRY_" + (key) + ".p", "rb")) #UTC_15000_ALL_-60_5slotSmall

    lsta = (dic['lsta'])[0] / dic['lsta'][1]
    amsr = (dic['amsr'])[0] / dic['amsr'][1]

    cores = dic['cores']

    lcnt = dic['lsta'][1]
    acnt = dic['amsr'][1]

    dist=200
    # llevels = np.array(list(np.arange(-0.8, 0, 0.1)) + list(np.arange(0.1, 0.81, 0.1)))#*12000
    # alevels = np.array(list(np.arange(-2.5, 0, 0.25)) + list(np.arange(0.25, 2.51, 0.25)))#*12000

    # llevels = np.array(list(np.arange(-1.6, 0, 0.2)) + list(np.arange(0.2, 1.61, 0.2)))#*12000  WET
    # alevels = np.array(list(np.arange(-3, 0, 0.25)) + list(np.arange(0.25, 3.25, 0.25)))#*12000

    llevels = np.array(list(np.arange(-1.5, 0, 0.2)) + list(np.arange(0.2, 1.51, 0.2)))#*12000 DRY
    alevels = np.array(list(np.arange(-5, 0, 0.5)) + list(np.arange(0.5, 5.5, 0.5)))#*12000

    f = plt.figure(figsize=(17, 3), dpi=200)
    ax = f.add_subplot(121)

    plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, (np.arange(0, 2*dist+1) - dist) * 3 , lsta , cmap='RdBu_r', extend='both', levels=llevels)
    plt.colorbar(label='K')
    cs = plt.contour((np.arange(0, 2*dist+1) - dist) * 3, (np.arange(0, 2*dist+1) - dist) * 3 , amsr , colors='k', linewidths=1, linestyles=['dotted'])
    plt.clabel(cs, inline=1, fontsize=8, fmt="%1.1f")
    ax.plot(0,0, 'bo')
    ax.set_xlabel('km')
    ax.set_ylabel('km')
    plt.axvline(x=0, linestyle='dashed', color='k',linewidth=1)
    plt.axhline(y=0, linestyle='dashed', color='k', linewidth=1)

    plt.title('LSTA | Nb cores: ' + str(cores) + '| ' + str(hour).zfill(2) + '00UTC',
              fontsize=10)

    ax = f.add_subplot(122)

    plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, (np.arange(0, 2*dist+1) - dist) * 3 , amsr , cmap='RdBu', extend='both', levels=alevels)
    plt.colorbar(label='%')
    # plt.contour((np.arange(0, 2 * dist + 1) - dist) * 3, (np.arange(0, 2 * dist + 1) - dist) * 3, lsta, colors='k',
    #             linewidths=0.8, linestyles=['dashed'])


    ax.plot(0,0, 'bo')
    ax.set_xlabel('km')
    ax.set_ylabel('km')
    plt.axvline(x=0, linestyle='dashed', color='k', linewidth=1)
    plt.axhline(y=0, linestyle='dashed', color='k', linewidth=1)
    plt.title('AMSRE| Nb cores: ' + str(cores) + '| ' + str(hour).zfill(2) + '00UTC', fontsize=10)
    plt.tight_layout()
    #plt.show()
    plt.savefig(path + '2hOverlap/amsreVSlsta/wcoeff_maps_all_AMSL_dry-1_' + str(hour).zfill(2) + '.png')



def plot_amsr_lsta_trio(hour):
    path = cnst.network_data + 'figs/LSTA/corrected_LSTA/new/wavelet_coefficients/'
    key = '2hOverlap'

    f = plt.figure(figsize=(10.5, 3), dpi=300)

    labels = ['Day-1', 'Day0', 'Day+1']

    left = 0.01
    bottom = 0.1
    width = 0.3
    height=0.8

    spot = [[]]

    for ids, ll in enumerate(['day-1', 'day0', 'day+1']):


        dic = pkl.load(
            open(path + "/coeffs_nans_stdkernel_USE_" + str(hour) + "UTC_15000_2dAMSL_"+ll+"_ALLS_minusMean_INIT_" + (key) + ".p",
                 "rb"))

        lsta = (dic['lsta'])[0] / dic['lsta'][1]
        amsr = (dic['amsr'])[0] / dic['amsr'][1]

        amsr = ndimage.gaussian_filter(amsr, 6, mode='nearest')

        cores = dic['cores']

        lcnt = dic['lsta'][1]
        acnt = dic['amsr'][1]

        dist = 200
        llevels = np.array(list(np.arange(-0.8, 0, 0.1)) + list(np.arange(0.1, 0.81, 0.1)))#*12000
        alevels = np.array(list(np.arange(-2.5, 0, 0.5)) + list(np.arange(0.5, 2.51, 0.5)))#*12000
        alevels = [-2.5,-2,-1.5,-1,-0.5,-0.25,0,0.25,0.5,1,1.5,2,2.5]

        # # llevels = np.array(list(np.arange(-1.6, 0, 0.2)) + list(np.arange(0.2, 1.61, 0.2)))#*12000  WET
        # # alevels = np.array(list(np.arange(-3, 0, 0.25)) + list(np.arange(0.25, 3.25, 0.25)))#*12000
        #
        # llevels = np.array(list(np.arange(-1.5, 0, 0.2)) + list(np.arange(0.2, 1.51, 0.2)))  # *12000 DRY
        # alevels = np.array(list(np.arange(-5, 0, 0.5)) + list(np.arange(0.5, 5.5, 0.5)))  # *12000

        ax = f.add_subplot(1,3,ids+1)

        mp1 = plt.contourf((np.arange(0, 2 * dist + 1) - dist) * 3, (np.arange(0, 2 * dist + 1) - dist) * 3, lsta,
                     cmap='RdBu_r', extend='both', levels=llevels)
        #plt.colorbar(label='K')
        cs = plt.contour((np.arange(0, 2 * dist + 1) - dist) * 3, (np.arange(0, 2 * dist + 1) - dist) * 3, amsr,
                         colors='k', linewidths=1, linestyles=['solid'], levels=alevels) #cmap='RdBu'
        plt.clabel(cs, inline=1, fontsize=8, fmt="%1.1f")

        ax.set_xlabel('km')
        if ids == 0:
            ax.set_ylabel('km')

        # if ids > 0:
        #     ax.set_yticklabels('')

        plt.axvline(x=0, linestyle='dashed', color='dimgrey', linewidth=1.2)
        plt.axhline(y=0, linestyle='dashed', color='dimgrey', linewidth=1.2)
        plt.plot(0, 0, marker='o', color='dimgrey')

        plt.title(labels[ids],fontsize=10)


    plt.tight_layout()
    text = ['a', 'b', 'c']
    plt.annotate(text[0], xy=(0.06, 0.92), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=13)
    plt.annotate(text[1], xy=(0.36, 0.92), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=13)
    plt.annotate(text[2], xy=(0.65, 0.92), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=13)

    f.subplots_adjust(right=0.91)
    cax = f.add_axes([0.92, 0.18, 0.015, 0.73])
    cbar = f.colorbar(mp1, cax)
    cbar.ax.tick_params(labelsize=10)
    cbar.set_label('K', fontsize=10)

    plt.savefig(path + '2hOverlap/amsreVSlsta/MAPS_AMSL_TRIO_ALLS_minusMean_noCore_INIT' + str(hour).zfill(2) + '.png')
    plt.close('all')


def plot_amsr_dry_wet(hour):

    path = cnst.network_data + 'figs/LSTA/corrected_LSTA/new/wavelet_coefficients/'
    key = '2hOverlap'
    daykey = 'day+1'
    dic1 = pkl.load(open(path+"/coeffs_nans_stdkernel_USE_"+str(hour)+"UTC_15000_2dAMSL_day0_ALLS_minusMean_CMORPH_WET_old_2hOverlap.p", "rb")) #UTC_15000_ALL_-60_5slotSmall
    dic2 = pkl.load(open(path+"/coeffs_nans_stdkernel_USE_"+str(hour)+"UTC_15000_2dAMSL_day+1_ALLS_minusMean_CMORPH_WET_old_2hOverlap.p", "rb")) #UTC_15000_ALL_-60_5slotSmall
    dic3 = pkl.load(open(path+"/coeffs_nans_stdkernel_USE_"+str(hour)+"UTC_15000_2dAMSL_day0_ALLS_minusMean_CMORPH_DRY_old_2hOverlap.p", "rb")) #UTC_15000_ALL_-60_5slotSmall
    dic4 = pkl.load(open(path+"/coeffs_nans_stdkernel_USE_"+str(hour)+"UTC_15000_2dAMSL_day+1_ALLS_minusMean_CMORPH_DRY_old_2hOverlap.p", "rb"))


    # dic1 = pkl.load(open(path+"/coeffs_nans_stdkernel_USE_"+str(hour)+"UTC_15000_2dAMSL_day0_ALLS_minusMean_CMORPH_WET_INIT_2hOverlap.p", "rb")) #UTC_15000_ALL_-60_5slotSmall
    # dic2 = pkl.load(open(path+"/coeffs_nans_stdkernel_USE_"+str(hour)+"UTC_15000_2dAMSL_day+1_ALLS_minusMean_CMORPH_WET_INIT_2hOverlap.p", "rb")) #UTC_15000_ALL_-60_5slotSmall
    # dic3 = pkl.load(open(path+"/coeffs_nans_stdkernel_USE_"+str(hour)+"UTC_15000_2dAMSL_day0_ALLS_minusMean_CMORPH_DRY_INIT_2hOverlap.p", "rb")) #UTC_15000_ALL_-60_5slotSmall
    # dic4 = pkl.load(open(path+"/coeffs_nans_stdkernel_USE_"+str(hour)+"UTC_15000_2dAMSL_day+1_ALLS_minusMean_CMORPH_DRY_INIT_2hOverlap.p", "rb"))
    #
    import matplotlib

    cmap = matplotlib.cm.get_cmap('viridis')
    rgba = cmap(0.5)

    names = ['DRY - day0', 'DRY - day+1', 'WET - day0', 'WET - day+1']

    pick = [dic4, '',dic2]

    f = plt.figure(figsize=(8.5, 6), dpi=300)
    for ids, dic in enumerate([dic3,dic4,dic1,dic2]):

        lsta = (dic['lsta'])[0] / dic['lsta'][1]
        amsr = (dic['amsr'])[0] / dic['amsr'][1]
        cmorph = (dic['cmorph'])[0] / dic['cmorph'][1]

        cmorph = ndimage.gaussian_filter(cmorph, 6, mode='nearest')
        amsr = ndimage.gaussian_filter(amsr, 3, mode='nearest')

        msg = (dic['msg'])[0] / dic['msg'][1]
        cores = dic['cores']


        dist=200
        llevels = np.array(list(np.arange(-0.8, 0, 0.1)) + list(np.arange(0.1, 0.81, 0.1)))#*12000
        alevels = np.array(list(np.arange(-2.5, 0, 0.25)) + list(np.arange(0.25, 2.51, 0.25)))#*12000

        alevels = [-4,-3,-2,-1,-0.5, -0.25, 0.25,0.5,1,2,3,4]

        ax = f.add_subplot(2,2,ids+1)

        plt.contourf((np.arange(0, 2*dist+1) - dist) * 3, (np.arange(0, 2*dist+1) - dist) * 3 , amsr , cmap='RdBu', extend='both', levels=alevels)
        plt.colorbar(label='%')

        if ids == 3:
            lev = np.arange(10, 71, 20)
            #lev = np.arange(10, 71, 5)
            colors = [cmap(0.05), cmap(0.5)]
        else:
            lev = np.arange(10, 71, 20)
            #lev = np.arange(10, 71, 5)
            colors = [cmap(0.05), cmap(0.6), cmap(0.99)]

        cs = plt.contour((np.arange(0, 2 * dist + 1) - dist) * 3, (np.arange(0, 2 * dist + 1) - dist) * 3, cmorph*100*1.2,
                    linewidths=1.2, linestyles=['solid'], levels=lev, colors='k')
        plt.clabel(cs, inline=1, fontsize=9, fmt="%1.0f")

        lev = [-99, 50]
        cs = plt.contour((np.arange(0, 2 * dist + 1) - dist) * 3, (np.arange(0, 2 * dist + 1) - dist) * 3, cmorph*100*1.2,
                    linewidths=1.5, linestyles=['solid'], levels=lev, colors='k')
        plt.clabel(cs, inline=1, fontsize=9, fmt="%1.0f")


        if ids in [0,2]:
            cmorph2 = ((pick[ids])['cmorph'])[0] / ((pick[ids])['cmorph'])[1]
            cmorph2 = ndimage.gaussian_filter(cmorph2, 6, mode='nearest')
            lev = [-99,50]

            cs = plt.contour((np.arange(0, 2 * dist + 1) - dist) * 3, (np.arange(0, 2 * dist + 1) - dist) * 3,
                             cmorph2 * 100 * 1.2,
                             linewidths=1.5, linestyles=['dashed'], levels=lev, colors='b')

            plt.clabel(cs, inline=1, fontsize=9, fmt="%1.0f")


        # cs = plt.contourf((np.arange(0, 2 * dist + 1) - dist) * 3, (np.arange(0, 2 * dist + 1) - dist) * 3, cmorph*100, cmap='viridis',
        #            levels=np.arange(0,101,10), extend='both')

        # cs = plt.contour((np.arange(0, 2 * dist + 1) - dist) * 3, (np.arange(0, 2 * dist + 1) - dist) * 3, msg*100, cmap='jet',
        #             linewidths=1, linestyles=['solid'], levels=np.arange(10,91,10))


        #plt.colorbar()

        if ids in [0,2]:
            ax.set_ylabel('km')
        ax.set_xlabel('km')
        plt.axvline(x=0, linestyle='dashed', color='dimgrey', linewidth=1.2)
        plt.axhline(y=0, linestyle='dashed', color='dimgrey', linewidth=1.2)
        plt.plot(0, 0, marker='o', color='dimgrey')

        plt.title(names[ids] , fontweight='bold', fontname='Ubuntu', fontsize=10) #+ ' | ' + str(cores) + ' cores'



    plt.tight_layout()
    text = ['a', 'b', 'c', 'd']
    plt.annotate(text[0], xy=(0.04, 0.96), xytext=(0, 4),xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=13)
    plt.annotate(text[1], xy=(0.54, 0.96), xytext=(0, 4), xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=13)
    plt.annotate(text[2], xy=(0.04, 0.49), xytext=(0, 4),  xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=13)
    plt.annotate(text[3], xy=(0.54, 0.49), xytext=(0, 4),  xycoords=('figure fraction', 'figure fraction'),
                 textcoords='offset points', fontweight='bold', fontname='Ubuntu', fontsize=13)

    plt.savefig(path + '2hOverlap/amsreVSlsta/wcoeff_maps_all_AMSL_DRYWET_CMORPH_OPLOT_' + str(hour).zfill(2) + '.png')
    plt.close('all')