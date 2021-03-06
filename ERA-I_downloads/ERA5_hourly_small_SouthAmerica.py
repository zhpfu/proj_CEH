import cdsapi

c = cdsapi.Client()
def download(y):
    c.retrieve(
        'reanalysis-era5-pressure-levels',
        {
            'product_type': 'reanalysis',
            'format': 'netcdf',
            'variable': ['q', 'r' ],
            'pressure_level': ['250', '550', '850'],
            'year': [
                str(y)
            ],
            'month': [
                '01', '02', '03',
                '04', '05', '06',
                '07', '08', '09',
                '10', '11', '12',
            ],
            'day': [
                '01', '02', '03',
                '04', '05', '06',
                '07', '08', '09',
                '10', '11', '12',
                '13', '14', '15',
                '16', '17', '18',
                '19', '20', '21',
                '22', '23', '24',
                '25', '26', '27',
                '28', '29', '30',
                '31',
            ],
            'time': '15:00',
            # 'area': [
            #     6, -83, -40,
            #     -32,
            # ],
            'area': [
                6, -82, -25,
                -58,
            ],
        },
        '/media/ck/Elements/SouthAmerica/ERA5/hourly/uv_15UTC/qr_15UTC_'+str(y)+'_peru.nc')



for y in [2019,1989]:#range(1989,2019):  # 89 missing
    download(y)
