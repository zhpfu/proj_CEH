import cdsapi

def download(year, month):
    c = cdsapi.Client()

    c.retrieve(
        'reanalysis-era5-single-levels-monthly-means',
        {
            'format':'netcdf',
            'product_type':'reanalysis-monthly-means-of-daily-means',
            'variable':[
                '100m_u_component_of_wind','100m_v_component_of_wind','10m_u_component_of_wind',
                '10m_v_component_of_neutral_wind','10m_v_component_of_wind','2m_dewpoint_temperature',
                '2m_temperature','boundary_layer_height','convective_available_potential_energy',
                'convective_inhibition','high_cloud_cover','instantaneous_10m_wind_gust',
                'mean_sea_level_pressure','orography','sea_surface_temperature',
                'surface_latent_heat_flux','surface_pressure','surface_sensible_heat_flux',
                'total_column_water','total_precipitation','vertical_integral_of_divergence_of_moisture_flux',
                'vertical_integral_of_thermal_energy','vertically_integrated_moisture_divergence'
            ],
            'year':[str(year) ],
            'month':[
                '01','02','03',
                '04','05','06',
                '07','08','09',
                '10','11','12'
            ],
            'time' : ['00:00'],
        },
        '/users/global/cornkle/mymachine/ERA5/ERA5_monthly_'+str(year)+'.nc')

for y in range(1979,2020):
    download(y)
