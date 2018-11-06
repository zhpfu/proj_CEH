import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from utils import u_darrays
import pdb
from utils import constants as cnst
import salem
from utils import u_statistics as us
from scipy import stats
import numpy.ma as ma
import pickle as pkl


def calc_trend(data, month, hour=None, method=None, sig=False, wilks=False):

    if method is None:
        'Please provide trend calc method: polyfit or mk (mann kendall)'
    if hour is not None:
        if len(month)>1:

            data = data[((data['time.month'] >= month[0]) & (data['time.month'] <= month[1])) & (data['time.hour'] == hour)]
        else:

            data = data[(data['time.month'] == month[0]) & (data['time.hour'] == hour)]
    else:
        if len(month)>1:
            data = data[((data['time.month'] >= month[0]) & (data['time.month'] <= month[1]))]
        else:
            data = data[(data['time.month'] == month[0])]

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
        dtrend = datastacked.groupby('allpoints').apply(u_darrays.linear_trend_mk, alpha=alpha, eps=0.0001,nb_missing=10)
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
    mcs = cnst.GRIDSAT + 'aggs/gridsat_WA_-70_monthly_count.nc'

    fpath = cnst.network_data + 'figs/CLOVER/months/'

    box=[-18,40,0,25]

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

    q = da['q'].sel(level=slice(850,925)).mean('level')
    t2d = da['t'].sel(level=slice(850, 925)).mean('level')
    u925 = da['u'].sel(level=slice(850, 925)).mean('level')
    u600 = da['u'].sel(level=slice(550,700)).mean('level')

    shear = u600#-u925

    q.values = q.values*1000

    grid = t2d.salem.grid.regrid(factor=0.5)
    t2 = grid.lookup_transform(t2d)
    tir = grid.lookup_transform(da3['tir'])
    q = grid.lookup_transform(q)
    shear = grid.lookup_transform(shear)

    # tir = t2d.salem.lookup_transform(da3['tir'])
    # t2 = t2d
    # #tir = da3['tir']
    # q = q
    # shear = shear

    grid = grid.to_dataset()

    t2 = xr.DataArray(t2, coords=[t2d['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])
    q = xr.DataArray(q, coords=[t2d['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])
    tir = xr.DataArray(tir, coords=[da3['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])
    shear = xr.DataArray(shear, coords=[t2d['time'],  grid['y'], grid['x']], dims=['time',  'latitude','longitude'])

    months=[3]

    dicm = {}
    dicmean = {}

    for m in months:
        method = 'mk'

        if len([m])==1:
            m = [m]

        t2trend, t2mean = calc_trend(t2, m, hour=12, method=method, sig=True, wilks=False)

        tirtrend, tirmean = calc_trend(tir, m, method=method, sig=True, wilks=False)
        tirm_mean = tirmean.mean(axis=0)

        qtrend, qmean = calc_trend(q, m, hour=12, method=method, sig=True, wilks=False)
        sheartrend, shearmean = calc_trend(shear, m, hour=12, method=method, sig=True, wilks=False)

        t2trend_unstacked = t2trend*10. # warming over decade
        qtrend_unstacked = qtrend * 10.  # warming over decade
        sheartrend_unstacked = sheartrend * 10.  # warming over decade
        tirtrend_unstacked = ((tirtrend.values)*10. / tirm_mean.values) * 100.

        dicm[m[0]] = tirtrend_unstacked
        dicmean[m[0]] = tirm_mean

        t_da = t2trend_unstacked
        q_da = qtrend_unstacked
        s_da = sheartrend_unstacked
        ti_da = tirtrend_unstacked

        fp = fpath + 'trend_mk_-70C_synop_sig'+str(m[0]).zfill(2)+'.png'
        map = shear.salem.get_map()

        f = plt.figure(figsize=(8, 5), dpi=300)
        ax1 = f.add_subplot(221)

        # map.set_shapefile(rivers=True)
        map.set_plot_params()

        map.set_data(t_da, interp='linear')
        map.set_plot_params(levels=np.linspace(-0.5,0.5,10), cmap='RdBu_r', extend='both')
        map.visualize(ax=ax1, title='t2')

        ax2 = f.add_subplot(222)
        map.set_data(q_da, interp='linear')
        map.set_plot_params(levels=np.linspace(-0.5,0.5,10), cmap='RdBu', extend='both')
        map.visualize(ax=ax2, title='q')

        ax3 = f.add_subplot(223)
        map.set_data(s_da, interp='linear')
        map.set_plot_params(levels=np.linspace(-1,1.1,10), cmap='RdBu_r', extend='both')
        map.visualize(ax=ax3, title='u-shear')

        ax4 = f.add_subplot(224)
        map.set_data(ti_da)
        map.set_plot_params(cmap='Blues', extend='both', levels=np.arange(20,101,20)) #levels=np.arange(20,101,20)
        map.visualize(ax=ax4, title='-70C frequency')

        plt.tight_layout()
        plt.savefig(fp)
        plt.close('all')

    pkl.dump(dicm,
             open(cnst.network_data + 'data/CLOVER/saves/storm_frac_synop12UTC.p',
                  'wb'))

    pkl.dump(dicmean,
                 open(cnst.network_data + 'data/CLOVER/saves/storm_frac_mean_synop12UTC.p',
                      'wb'))