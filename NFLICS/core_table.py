import xarray as xr
import numpy as np
import pandas as pd



def from_daily():

    coref = '/home/ck/DIR/cornkle/MCSfiles/blob_map_allscales_-50_JJAS_points_dominant_daily.nc'
    dat = xr.open_dataarray(coref)



    dic = {'date' : [], 'lon' : [], 'lat': [], 'hour': [], 'month': [], 'year': []}
    for t in (dat.time):
        day = dat.sel(time=t)
        #ipdb.set_trace()
        pos = np.where(np.isfinite(day.values))

        for y, x in zip(pos[0], pos[1]):

            point = day.isel(lon=x, lat=y)

            hour = point.values

            date =  str(point['time.year'].values) +'-'+ str(point['time.month'].values).zfill(2) +'-'+ str(point['time.day'].values).zfill(2)+' ' + str(int(hour)).zfill(2) + ':00:00'
            dic['date'].append(date)
            dic['month'].append(int(day['time.month'].values))
            dic['hour'].append(int(hour))
            dic['year'].append(int(day['time.year'].values))
            dic['lon'].append(float(point.lon.values))
            dic['lat'].append(float(point.lat.values))
    pdic = pd.DataFrame.from_dict(dic)


    pdic.to_csv('/home/ck/DIR/cornkle/data/NFLICS/tables/blob_map_allscales_-50_JJAS_points_dominant_daily.csv', na_rep=-999, index_label='id')



def from_cores():

    coref = '/media/ck/Elements/Africa/WestAfrica/cores_fromMeteosat/cores/coresPower_MSG*.nc'
    dats = xr.open_mfdataset(coref)

    dats = dats.sel(lat=slice(10.5,17), lon=slice(-14,-4), time=(dats['time.minute']==0))

    for h in range(15,21):

        dic = {'date' : [], 'lon' : [], 'lat': [], 'hour': [], 'month': [], 'year': [], 'day':[]}
        dat = dats.sel(time=(dats['time.hour']==h))

        for t in (dat.time):
            day = dat['blobs'].sel(time=t).load()

            pos = np.where(day.values < -900)

            for y, x in zip(pos[0], pos[1]):

                point = day.isel(lon=x, lat=y)

                #hour = point.values

                date =  str(point['time.year'].values) +'-'+ str(point['time.month'].values).zfill(2) +'-'+ str(point['time.day'].values).zfill(2)+' ' + str(int(h)).zfill(2) + ':00:00'
                print('Doing ', date)
                dic['date'].append(date)
                dic['month'].append(int(day['time.month'].values))
                dic['hour'].append(int(h))
                dic['year'].append(int(day['time.year'].values))
                dic['day'].append(int(day['time.day'].values))
                dic['lon'].append(float(point.lon.values))
                dic['lat'].append(float(point.lat.values))
            del day
        pdic = pd.DataFrame.from_dict(dic)


        pdic.to_csv('/home/ck/DIR/cornkle/data/NFLICS/tables/coresPower_MSG_-40_700km2_-50points_dominant_vcores_14-4W_'+str(h).zfill(2)+'UTC.csv', na_rep=-999, index_label='id')
        del dat
