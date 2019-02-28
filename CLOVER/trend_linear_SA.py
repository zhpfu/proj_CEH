import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from utils import u_darrays
import ipdb
from utils import constants as cnst, u_met
import salem
from utils import u_statistics as us
from scipy import stats
import numpy.ma as ma
import pickle as pkl
import shapely.geometry as shpg
import seaborn


def calc_trend(data, month, hour=None, method=None, sig=False, wilks=False):

    if method is None:
        'Please provide trend calc method: polyfit or mk (mann kendall)'
    if hour is not None:

        if len(month)>1:

            data = data[((data['time.month'] >= month[0]) | (data['time.month'] <= month[1])) & (data['time.hour'] == hour)]# & (data['time.year'] >= 1983) & (data['time.year'] <= 2017)]
        else:

            data = data[(data['time.month'] == month[0]) & (data['time.hour'] == hour)]# & (data['time.year'] >= 1983) & (data['time.year'] <= 2017)]
    else:
        if len(month)>1:
            data = data[((data['time.month'] >= month[0]) | (data['time.month'] <= month[1]))] #& (data['time.year'] >= 1983) & (data['time.year'] <= 2017)]
        else:
            data = data[(data['time.month'] == month[0])]# & (data['time.year'] >= 1983) & (data['time.year'] <= 2017)]

    if len(data.time)==0:
        print('Data does not seem to have picked month or hour. Please check input data')


    mean_years = data.groupby('time.year').mean(axis=0)

    # stack lat and lon into a single dimension called allpoints
    datastacked = mean_years.stack(allpoints=['latitude', 'longitude'])

    # apply the function over allpoints to calculate the trend at each point
    print('Entering trend calc')

    alpha = 0.05
    # NaNs means there is not enough data, slope = 0 means there is no significant trend.
    if method=='mk':
        dtrend = datastacked.groupby('allpoints').apply(u_darrays.linear_trend_mk, alpha=alpha, eps=0.001,nb_missing=5)
        dtrend = dtrend.unstack('allpoints')
        if sig:
            (dtrend['slope'].values)[dtrend['ind'].values==0] = 0

    # NaNs means there is not enough data, slope = 0 means there is no significant trend.
    if method=='polyfit':
        dtrend = datastacked.groupby('allpoints').apply(u_darrays.linear_trend_lingress,nb_missing=10)
        dtrend = dtrend.unstack('allpoints')

        if sig:
            (dtrend['slope'].values)[dtrend['pval'].values > alpha] = 0

    ddtrend = dtrend['slope']

    if wilks and sig:
        try:
            pthresh = us.fdr_threshold(dtrend['pval'].values[np.isfinite(dtrend['pval'].values)], alpha=alpha)
            ddtrend.values[(dtrend['pval'].values > pthresh) | np.isnan(dtrend['pval'].values)] = np.nan
        except ValueError:
            ddtrend.values = ddtrend.values * np.nan
            pthresh = np.nan
        print('p value threshold', pthresh)

    # unstack back to lat lon coordinates
    return ddtrend, mean_years




def trend_all():

    srfc = cnst.ERA_MONTHLY_SRFC_SYNOP
    pl = cnst.ERA_MONTHLY_PL_SYNOP
    mcs = cnst.GRIDSAT + 'aggs/gridsat_WA_-65_monthly_count_-40base_15-21UTC_1000km2.nc'

    fpath = cnst.network_data + 'figs/CLOVER/months/'

    box=[5,55,-36,0]#  [-18,40,0,25] #

    da = xr.open_dataset(pl)
    da = u_darrays.flip_lat(da)
    da = da.sel(longitude=slice(box[0], box[1]), latitude=slice(box[2],box[3]))
    da2 = xr.open_dataset(srfc)
    da2 = u_darrays.flip_lat(da2)
    da2 = da2.sel(longitude=slice(box[0], box[1]), latitude=slice(box[2],box[3]))
    da3 = xr.open_dataset(mcs)
    da3 = da3.sel(lon=slice(box[0], box[1]), lat=slice(box[2],box[3]))

    lons = da.longitude
    lats = da.latitude


    #t2d = da['t'].sel(level=slice(800,850)).mean('level')

    press = da2['sp']
    press = press[press['time.hour'] == 12]
    press.values = press.values/100
    low_press = 800
    up_press = 500

    q = da['q'].sel(level=low_press)#.mean('level')
    q = q[q['time.hour']==12]
    t2d = da2['t2m']
    #t2d = da['t'].sel(level=low_press)#.mean('level')
    t2d = t2d[t2d['time.hour']==12]

    ws_ar = u_met.u_v_to_ws_wd(da['u'].values, da['v'].values)
    u600 = da['u'].sel(level=up_press)#.mean('level')
    u600 = u600[u600['time.hour']==12]
    v600 = da['v'].sel(level=up_press)#.mean('level')
    v600 = v600[v600['time.hour']==12]

    #da['u'].values = ws_ar[0]

    ws800 = da['u'].sel(level=low_press)#.mean('level')
    ws800 = ws800[ws800['time.hour']==12]

    ws500 = da['u'].sel(level=up_press)#.mean('level')
    ws500 = ws500[ws500['time.hour']==12]


    # t2d.values[press.values <= low_press]=0
    # u925.values[press.values <= low_press] = 0
    # q.values[press.values <= low_press] = 0


    shear = ws500-ws800

    u6 = u600
    v6 = v600

    q.values = q.values*1000

    grid = t2d.salem.grid.regrid(factor=0.5)
    t2 = t2d # grid.lookup_transform(t2d)
    tir = grid.lookup_transform(da3['tir'])
    #q = grid.lookup_transform(q)
    #shear = grid.lookup_transform(shear)
    #u6 = grid.lookup_transform(u6)
    #v6 = grid.lookup_transform(v6)

    # tir = t2d.salem.lookup_transform(da3['tir'])
    # t2 = t2d
    # #tir = da3['tir']
    # q = q
    # shear = shear

    grid = grid.to_dataset()

    # t2 = xr.DataArray(t2, coords=[t2d['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])
    # q = xr.DataArray(q, coords=[t2d['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])
    tir = xr.DataArray(tir, coords=[da3['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])
    # shear = xr.DataArray(shear, coords=[t2d['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])
    # u6 = xr.DataArray(u6, coords=[t2d['time'], grid['y'], grid['x']], dims=['time', 'latitude', 'longitude'])
    # v6 = xr.DataArray(v6, coords=[t2d['time'], grid['y'], grid['x']], dims=['time', 'latitude', 'longitude'])

    months=[(12,2)]#,2,3,11,12]

    dicm = {}
    dicmean = {}

    for m in months:
        method = 'mk'

        if len(m)==1:
            m = [m]

        sig = True

        t2trend, t2mean = calc_trend(t2, m,  method=method, sig=sig,hour=12, wilks=False) #hour=12,
        t2_mean = t2mean.mean(axis=0)


        # plt.figure()
        # plt.imshow(t2_mean, origin='lower')
        #
        # plt.figure()
        # plt.contourf(t2_mean)
        # return

        tirtrend, tirmean = calc_trend(tir, m, method=method, sig=sig, wilks=False)

        tirm_mean = tirmean.mean(axis=0)

        qtrend, qmean = calc_trend(q, m, method=method, sig=sig,hour=12, wilks=False) #hour=12,
        q_mean = qmean.mean(axis=0)

        sheartrend, shearmean = calc_trend(shear, m, method=method, sig=sig,hour=12, wilks=False) #hour=12,
        shear_mean = shearmean.mean(axis=0)

        u6trend, u6mean = calc_trend(u6, m,  method=method, sig=sig, hour=12,wilks=False) #hour=12,
        u6_mean = u6mean.mean(axis=0)
        v6trend, v6mean = calc_trend(v6, m, method=method, sig=sig, hour=12,wilks=False) #hour=12,
        v6_mean = v6mean.mean(axis=0)

        t2trend_unstacked = t2trend*10. # warming over decade
        qtrend_unstacked = qtrend * 10.  # warming over decade
        sheartrend_unstacked = sheartrend * 10.  # warming over decade
        u6trend_unstacked = u6trend * 10
        v6trend_unstacked = v6trend * 10

        tirtrend_unstacked = ((tirtrend.values)*10. / tirm_mean.values) * 100.

        tirtrend_out = xr.DataArray(tirtrend_unstacked, coords=[grid['y'], grid['x']], dims=['latitude','longitude'])
        tirmean_out = xr.DataArray(tirm_mean, coords=[grid['y'], grid['x']], dims=['latitude','longitude'])
        # if len(m) == 1:
        #     u6mean = u6[u6['time.month'] == m].mean('time')
        #     v6mean = v6[v6['time.month'] == m].mean('time')
        # else:
        #     u6mean = u6[(u6['time.month'] >=m[0]) | (u6['time.month'] <=m[1])].mean('time')
        #     v6mean = v6[(v6['time.month'] >=m[0]) | (v6['time.month'] <=m[1])].mean('time')

        dicm[m[0]] = tirtrend_out
        dicmean[m[0]] = tirmean_out

        t_da = t2trend_unstacked
        q_da = qtrend_unstacked
        s_da = sheartrend_unstacked
        ti_da = tirtrend_unstacked
        if len(m) == 1:
            fp = fpath + 'trend_mk_-70C_synop_-50base_linear_'+str(m[0]).zfill(2)+'_200hPa.png'
        else:
            fp = fpath + 'trend_mk_-70C_synop_-50base_linear' + str(m[0]).zfill(2) +'-'+ str(m[1]).zfill(2) + '_200hPa.png'
        map = shear.salem.get_map()

        f = plt.figure(figsize=(15,8), dpi=300)
        ax1 = f.add_subplot(221)
        # map.set_shapefile(rivers=True)
        # bla = ma.masked_invalid(tcorr['r'].values)

        map.set_data(t_da.values, interp='linear')  # interp='linear'
        # transform their coordinates to the map reference system and plot the arrows
        xx, yy = map.grid.transform(shear.longitude.values, shear.latitude.values,
                                    crs=shear.salem.grid.proj)

        xx, yy = np.meshgrid(xx, yy)
        #Quiver only every 7th grid point
        u = u6trend_unstacked.values[1::2, 1::2]
        v = v6trend_unstacked.values[1::2, 1::2]

        #Quiver only every 7th grid point
        uu = u6_mean.values[1::2, 1::2]
        vv = v6_mean.values[1::2, 1::2]

        xx = xx[1::2, 1::2]
        yy = yy[1::2, 1::2]


        #map.set_contour(t2_mean.values-273.15, interp='linear', cmap='Oranges', linewidths=1.3)

        map.set_contour((t2_mean.values-273.15).astype(np.float64), interp='linear', colors='k', linewidths=0.5, levels=[20,23,26,29,32,35])
       #

        map.set_plot_params(levels=[-0.5,-0.4,-0.3,-0.2,-0.1,-0.05,-0.02, 0.02,0.05,0.1,0.2,0.3,0.4,0.5], cmap='RdBu_r', extend='both')  # levels=np.arange(-0.5,0.51,0.1),
        dic = map.visualize(ax=ax1, title='2m temperature trend | contours: mean T', cbar_title='K decade-1')
        contours = dic['contour'][0]
        plt.clabel(contours, inline=True, fontsize=7, fmt='%1.1f')

        ax2 = f.add_subplot(222)
        map.set_data(q_da.values,interp='linear')  # interp='linear'
        map.set_contour((q_mean.values).astype(np.float64),interp='linear', colors='k', levels=[6,8,10,12,14,16], linewidths=0.5)
        map.set_plot_params(levels=[-0.4,-0.3,-0.2,-0.1,-0.05,-0.02, 0.02,0.05,0.1,0.2,0.3,0.4], cmap='RdBu', extend='both')  # levels=np.arange(-0.5,0.51,0.1),
        #qu = ax2.quiver(xx, yy, uu, vv, scale=80, width=0.004)
        dic = map.visualize(ax=ax2, title='800hPa Spec. humidity trend | contours: mean q', cbar_title='g kg-1 decade-1')
        contours = dic['contour'][0]
        plt.clabel(contours, inline=True, fontsize=7, fmt='%1.1f')


        ax3 = f.add_subplot(223)
        map.set_data(s_da.values, interp='linear')  # interp='linear'
        map.set_contour(s_da.values, interp='linear', levels=np.arange(-7,7,8), cmap='Blues')
        #plt.clabel(cntr, inline=1, fontsize=10)
        map.set_plot_params(levels=[-0.5,-0.4,-0.3,-0.2,-0.1,-0.05,-0.02, 0.02,0.05,0.1,0.2,0.3,0.4,0.5], cmap='RdBu_r', extend='both')  # levels=np.arange(-0.5,0.51,0.1)
        map.visualize(ax=ax3, title='800-500hPa wind shear trend, mean 500hPa wind vectors', cbar_title='m s-1 decade-1')
        qu = ax3.quiver(xx, yy, uu, vv, scale=80, width=0.002)

        qk = plt.quiverkey(qu, 0.4, 0.03, 4, '4 m s$^{-1}$',
                           labelpos='E', coordinates='figure')

        ax4 = f.add_subplot(224)
        map.set_contour(tirm_mean.values, interp='linear', levels=[0.1,0.5,1,2.5], colors='k', linewidths=0.5)


        ti_da[ti_da==0] = np.nan
        map.set_data(ti_da)  #
        coord = [18, 25, -28, -20]
        geom = shpg.box(coord[0], coord[2], coord[1], coord[3])
        map.set_geometry(geom, zorder=99, color='darkorange', linewidth=3, linestyle='--', alpha=0.3)

        map.set_plot_params(cmap='viridis', extend='both', levels=np.arange(10,51,10))  # levels=np.arange(20,101,20)  #np.arange(20,101,20)
        dic = map.visualize(ax=ax4, title='-65C cloud cover change | >1000km2 -40C', cbar_title='$\%$ decade-1')
        contours = dic['contour'][0]
        plt.clabel(contours, inline=True, fontsize=7, fmt='%1.1f')

        plt.tight_layout()
        plt.savefig(fp)
        plt.close('all')

    pkl.dump(dicm,
             open(cnst.network_data + 'data/CLOVER/saves/storm_frac_synop12UTC_SA.p',
                  'wb'))

    pkl.dump(dicmean,
                 open(cnst.network_data + 'data/CLOVER/saves/storm_frac_mean_synop12UTC_SA.p',
                      'wb'))
