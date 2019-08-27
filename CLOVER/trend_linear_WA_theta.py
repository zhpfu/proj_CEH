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

            data = data[((data['time.month'] >= month[0]) & (data['time.month'] <= month[1])) & (data['time.hour'] == hour) & (data['time.year'] >= 1984) & (data['time.year'] <= 2017)]
        else:

            data = data[(data['time.month'] == month[0]) & (data['time.hour'] == hour) & (data['time.year'] >= 1984) & (data['time.year'] <= 2017)]
    else:
        if len(month)>1:
            data = data[((data['time.month'] >= month[0]) & (data['time.month'] <= month[1]))& (data['time.year'] >= 1984) & (data['time.year'] <= 2017)]
        else:
            data = data[(data['time.month'] == month[0]) & (data['time.year'] >= 1984) & (data['time.year'] <= 2017)]

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
        dtrend = datastacked.groupby('allpoints').apply(u_darrays.linear_trend_mk, alpha=alpha, eps=0.01,nb_missing=10)
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

    srfc = cnst.ERA5_MONTHLY_SRFC_SYNOP #cnst.ERA_MONTHLY_SRFC_SYNOP
    pl = cnst.ERA5_MONTHLY_PL_SYNOP #cnst.ERA_MONTHLY_PL_SYNOP
    mcs = cnst.GRIDSAT + 'aggs/gridsat_WA_-70_monthly_count_15-21UTC_5000km2.nc'#gridsat_WA_-70_monthly_mean_5000km2.nc' #gridsat_WA_-50_monthly_count_-50base.nc' #gridsat_WA_-70_monthly_mean_5000km2.nc'  gridsat_WA_-50_monthly_count

    fpath = cnst.network_data + 'figs/CLOVER/months/ERA5_WA/'

    box=[-18,30,0,25]#  [-18,40,0,25] #

    da = xr.open_dataset(pl) #xr.open_dataset(pl)
    #da = xr.decode_cf(da)
    da = u_darrays.flip_lat(da)
    da = da.sel(longitude=slice(box[0], box[1]), latitude=slice(box[2],box[3]))
    da2 = xr.open_dataset(srfc) #xr.open_dataset(srfc)
    #da2 = xr.decode_cf(da2)
    da2 = u_darrays.flip_lat(da2)
    da2 = da2.sel(longitude=slice(box[0], box[1]), latitude=slice(box[2],box[3]))
    da3 = xr.open_dataarray(mcs)/30*100#/30*100
    da3 = da3.sel(lon=slice(box[0], box[1]), lat=slice(box[2],box[3]))
    #ipdb.set_trace()
    da = da.isel(time=(da['time.hour']==12))
    da2 = da2.isel(time=(da2['time.hour']==12))

    lons = da.longitude
    lats = da.latitude


    press = da2['tcwv']
    #press = press[press['time.hour'] == 12]
    #press.values = press.values#*1000
    low_press = 925
    up_press = 650
    mid_press = 700

    q = da['q'].sel(level=slice(low_press-30, low_press)).mean('level')
    t2d = da2['t2m']


    theta_low = u_met.theta_e(low_press, da['t'].sel(level=slice(low_press-30, low_press)).mean('level').values-273.15, da['q'].sel(level=slice(low_press-30, low_press)).mean('level').values)
    theta_high = u_met.theta_e(mid_press, da['t'].sel(level=slice(up_press, mid_press)).mean('level').values-273.15, da['q'].sel(level=slice(up_press, mid_press)).mean('level').values)
    theta_high_d = u_met.theta(mid_press, da['t'].sel(level=slice(up_press, mid_press)).mean('level').values - 273.15)
    theta_low_d = u_met.theta(low_press, da['t'].sel(level=slice(low_press - 30, low_press)).mean('level').values - 273.15)

    theta_diff = theta_low - theta_high
    theta_diff_d = theta_low_d - theta_high_d

    theta_e = t2d.copy(deep=True)
    theta_e.name = 'theta'
    theta_e.values = theta_diff

    theta_d = t2d.copy(deep=True)
    theta_d.name = 'theta'
    theta_d.values = theta_diff_d

    u600 = da['u'].sel(level=slice(up_press, mid_press)).mean('level')
    v600 = da['v'].sel(level=slice(up_press, mid_press)).mean('level')
    ws600 = u_met.u_v_to_ws_wd(u600, v600)

    u800 = da['u'].sel(level=slice(low_press-30, low_press)).mean('level')

    v800 = da['v'].sel(level=slice(low_press-30, low_press)).mean('level')

    shear_u = u600-u800
    shear_v = v600-v800
    ws_shear = u_met.u_v_to_ws_wd(shear_u.values, shear_v.values)

    ws_600 = t2d.copy(deep=True)
    ws_600.name = 'ws'

    ws_600.values = ws600[0]

    shear = t2d.copy(deep=True)
    shear.name = 'shear'
    shear.values = ws_shear[0]

    u6 = shear_u
    v6 = shear_v

    q.values = q.values*1000

    grid = t2d.salem.grid.regrid(factor=0.8)
    t2 = t2d # grid.lookup_transform(t2d)
    tir = grid.lookup_transform(da3)  #t2d.salem.lookup_transform(da3['tir']) #

    grid = grid.to_dataset()
    tir = xr.DataArray(tir, coords=[da3['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])


    months= [2,3,4,5,6,7,8,9,10,11]#[3,4,5,6,9,10,11]#,4,5,6,9,10,11#,4,5,6,9,10,11,(3,5), (9,11)]#, 10,5,9]#[(12,2)]#[1,2,3,4,5,6,7,8,9,10,11,12]# #,2,3,11,12]#[(12,2)]#[1,2,3,4,5,6,7,8,9,10,11,12]# #,2,3,11,12]

    dicm = {}
    dicmean = {}

    for m in months:
        method = 'polyfit'

        if type(m)==int:
            m = [m]

        sig = False

        t2trend, t2mean = calc_trend(t2, m,  method=method, sig=sig,hour=12, wilks=False) #hour=12,
        t2_mean = t2mean.mean(axis=0)

        tirtrend, tirmean = calc_trend(tir, m, method=method, sig=True, wilks=False)

        tirm_mean = tirmean.mean(axis=0)

        qtrend, qmean = calc_trend(q, m, method=method, sig=sig,hour=12, wilks=False) #hour=12,
        q_mean = qmean.mean(axis=0)

        sheartrend, shearmean = calc_trend(shear, m, method=method, sig=sig,hour=12, wilks=False) #hour=12,
        shear_mean = shearmean.mean(axis=0)

        presstrend, pressmean = calc_trend(press, m, method=method, sig=sig,hour=12, wilks=False) #hour=12,
        press_mean = pressmean.mean(axis=0)

        u6trend, u6mean = calc_trend(u6, m,  method=method, sig=sig, hour=12,wilks=False) #hour=12,
        u6_mean = u6mean.mean(axis=0)
        v6trend, v6mean = calc_trend(v6, m, method=method, sig=sig, hour=12,wilks=False) #hour=12,
        v6_mean = v6mean.mean(axis=0)

        u8trend, u8mean = calc_trend(u800, m,  method=method, sig=sig, hour=12,wilks=False) #hour=12,
        u8_mean = u8mean.mean(axis=0)
        v8trend, v8mean = calc_trend(v800, m, method=method, sig=sig, hour=12,wilks=False) #hour=12,
        v8_mean = v8mean.mean(axis=0)

        aej = np.argmin(u6_mean, axis=0)
        #ipdb.set_trace()

        thetatrend, thetamean = calc_trend(theta_e, m, method=method, sig=sig, hour=12,wilks=False) #hour=12,
        theta_mean = thetamean.mean(axis=0)

        thetatrend_d, thetamean_d = calc_trend(theta_d, m, method=method, sig=sig, hour=12,wilks=False) #hour=12,
        thetad_mean = thetamean_d.mean(axis=0)

        t_da = t2trend*10. # warming over decade
        q_da = qtrend * 10.  # warming over decade
        s_da = sheartrend * 10.  # warming over decade
        u6trend = u6trend * 10
        v6trend = v6trend * 10
        tcwv_da = presstrend * 10
        theta_da = thetatrend * 10
        thetad_da = thetatrend_d * 10
        u8trend = u8trend * 10
        v8trend = v8trend * 10

        tdata = (tirtrend.values*10. / tirm_mean.values) * 100.
        #ipdb.set_trace()
        tirtrend_out = xr.DataArray(tdata, coords=[grid['y'], grid['x']], dims=['latitude','longitude'])
        tirtrend_out.name = 'tir'
        #tirmean_out = xr.DataArray(tirm_mean, coords=[grid['y'], grid['x']], dims=['latitude','longitude'])

        dicm[m[0]] = tirtrend_out
        dicmean[m[0]] = tirm_mean

        if len(m) == 1:
            fp = fpath + 'use/ERA5_trend_synop_WA_-70_poly_theta_Tirmean_15-21_'+str(m[0]).zfill(2)+'.png'
        else:
            fp = fpath + 'use/ERA5_trend_synop_WA_-70_poly_theta_Tirmean_' + str(m[0]).zfill(2) +'-'+ str(m[1]).zfill(2) + '.png'
        map = shear.salem.get_map()
        ti_da = t2d.salem.transform(tirtrend_out)

        f = plt.figure(figsize=(15,8), dpi=300)

        # transform their coordinates to the map reference system and plot the arrows
        xx, yy = map.grid.transform(shear.longitude.values, shear.latitude.values,
                                    crs=shear.salem.grid.proj)

        xaej, yaej = map.grid.transform(u6_mean.longitude.values, u6_mean.latitude.values[aej.values],
                                    crs=shear.salem.grid.proj)

        xx, yy = np.meshgrid(xx, yy)
        #Quiver only every 7th grid point
        u = u6trend.values[1::2, 1::2]
        v = v6trend.values[1::2, 1::2]

        #Quiver only every 7th grid point
        uu = u8trend.values[1::2, 1::2]
        vv = v8trend.values[1::2, 1::2]

        xx = xx[1::2, 1::2]
        yy = yy[1::2, 1::2]

        # pdic = {
        #     'tlin' : (t2_mean.values-273.15).astype(np.float64),
        #     'tmean' : (t2_mean.values-273.15).astype(np.float64),
        #     'qmean' : (q_mean.values).astype(np.float64),
        #     'qlin'  : q_da.values,
        #     'shearlin' : s_da.values,
        #     'u' : u,
        #     'v' : v,
        #     'xx' : xx,
        #     'yy' : yy,
        #     'tirmean' : tirm_mean,
        #
        #
        # }

        # pkl.dump(dicm,
        #          open(cnst.network_data + 'data/CLOVER/saves/storm_frac_synop12UTC_WA.p',
        #               'wb'))

        ax1 = f.add_subplot(221)
        map.set_data(t_da.values, interp='linear')  # interp='linear'

        map.set_contour(s_da.values, interp='linear', levels=[0.4,0.8,1], colors='darkturquoise')
        map.set_plot_params(levels=[-0.5,-0.4,-0.3,-0.2,0.2,0.3,0.4,0.5], cmap='RdBu_r', extend='both')  # levels=np.arange(-0.5,0.51,0.1),
        qu = ax1.quiver(xx, yy, u, v, scale=50, width=0.002)

        qk = plt.quiverkey(qu, 0.4, 0.03, 1, '1 m s$^{-1}$',
                           labelpos='E', coordinates='figure')

        #map.set_contour((t2_mean.values).astype(np.float64), interp='linear', colors='k', linewidths=0.5, levels=np.linspace(800,925,8))
        #map.set_plot_params(levels=[-0.5,-0.4,-0.3,-0.2,-0.1,-0.05,-0.02, 0.02,0.05,0.1,0.2,0.3,0.4,0.5], cmap='RdBu_r', extend='both')  # levels=np.arange(-0.5,0.51,0.1),

        dic = map.visualize(ax=ax1, title='2m temperature trend | contours: 925-600 hPa wind trend', cbar_title='K decade-1')
        contours = dic['contour'][0]
        plt.clabel(contours, inline=True, fontsize=7, fmt='%1.1f')

        ax2 = f.add_subplot(222)
        map.set_data(theta_da.values,interp='linear')  # interp='linear'
        map.set_contour((q_da.values).astype(np.float64),interp='linear', colors='darkturquoise', levels=[-0.8,-0.6,-0.4,-0.2,0.2,0.4, 0.6,0.8]) #[6,8,10,12,14,16]
        map.set_plot_params(levels=[-1,-0.8,-0.6,-0.4,-0.2,0.2,0.4,0.6, 0.8,1], cmap='RdBu_r', extend='both')  # levels=np.arange(-0.5,0.51,0.1), [-0.6,-0.4,-0.2,0.2,0.4,0.6]

        dic = map.visualize(ax=ax2, title='925hPa Spec. humidity trend | contours: mean q', cbar_title='g kg-1 decade-1')
        contours = dic['contour'][0]
        plt.clabel(contours, inline=True, fontsize=7, fmt='%1.1f')


        ax3 = f.add_subplot(223)
        map.set_data(thetad_da.values, interp='linear')  # interp='linear'
        map.set_contour(tcwv_da.values, interp='linear', levels=[-2,-1.5,-1,-0.5,0.5,1,1.5,2], colors='darkturquoise')

        map.set_plot_params(levels=[-1,-0.8,-0.6,-0.4,-0.2,0.2,0.4,0.6, 0.8,1], cmap='RdBu_r', extend='both')  # levels=np.arange(-0.5,0.51,0.1)

        qu = ax3.quiver(xx, yy, uu, vv, scale=50, width=0.002)

        qk = plt.quiverkey(qu, 0.4, 0.03, 1, '1 m s$^{-1}$',
                           labelpos='E', coordinates='figure')


        dic = map.visualize(ax=ax3, title='Total precipitable water | contours: mean q', cbar_title='g kg-1 decade-1')
        contours = dic['contour'][0]
        plt.clabel(contours, inline=True, fontsize=7, fmt='%1.1f')


        ax4 = f.add_subplot(224)
        map.set_contour((tirm_mean), interp='linear', levels=[0.1,0.5,1,2.5], colors='k', linewidths=0.5)

        ti_da.values[ti_da.values==0] = np.nan
        map.set_data(ti_da)  #
        coord = [18, 25, -28, -20]
        geom = shpg.box(coord[0], coord[2], coord[1], coord[3])
        #map.set_geometry(geom, zorder=99, color='darkorange', linewidth=3, linestyle='--', alpha=0.3)

        map.set_plot_params(cmap='viridis', extend='both', levels=np.arange(10,51,10))  # levels=np.arange(10,51,10)

        ax4.scatter(xaej, yaej, color='r', s=50, edgecolors='r', linewidths=1)

        dic = map.visualize(ax=ax4, title='-70C cloud cover change | >5000km2', cbar_title='$\%$ decade-1')
        contours = dic['contour'][0]
        plt.clabel(contours, inline=True, fontsize=7, fmt='%1.1f')

        plt.tight_layout()
        plt.savefig(fp)
        plt.close('all')

    # pkl.dump(dicm,
    #          open(cnst.network_data + 'data/CLOVER/saves/storm_frac_synop12UTC_WAtirM.p',
    #               'wb'))
    #
    # pkl.dump(dicmean,
    #              open(cnst.network_data + 'data/CLOVER/saves/storm_frac_mean_synop12UTC_WAtirM.p',
    #                   'wb'))
