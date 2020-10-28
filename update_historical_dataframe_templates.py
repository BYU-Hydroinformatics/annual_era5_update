import netCDF4 as nc
import pandas as pd
import datetime

# needs to be able to read the historical simulation netcdf and be able to write to the volume
# which holds all the region netcdf files

# CREATES THE ERA 5 TEMPLATE DATAFRAME
hist_sim_netcdf = nc.Dataset('/path/to/historical/simulation/file')
dates_series = nc.num2date(hist_sim_netcdf['time'][:], hist_sim_netcdf['time'].units, only_use_cftime_datetimes=False, only_use_python_datetimes=True)
dates_series = [datetime.datetime.strftime(i, '%Y-%m-%dT%H:%M:%SZ') for i in dates_series]
dates_series = pd.DataFrame(dates_series, columns=['datetime'])
dates_series['datetime'] = pd.to_datetime(dates_series['datetime'])
dates_series['flow'] = 0
dates_series.index = pd.to_datetime(dates_series['datetime'])
del dates_series['datetime']
dates_series.index = dates_series.index.strftime('%Y-%m-%dT%H:%M:%SZ')
dates_series.to_pickle('/path/to/era5_template_pandas_dataframe.pickle')

# Creates the ERA Interim template but this should never need to be run again
# a = pd.read_pickle('/path/to/era5_pandas_dataframe_template.pickle')
# a.index = pd.to_datetime(a.index)
# a = a[a.index.year >= 1980]
# a = a[a.index.year <= 2014]
# a.index = a.index.strftime('%Y-%m-%dT%H:%M:%SZ')
# a.to_pickle('/path/to/save/erainterim_pandas_dataframe_template.pickle')
