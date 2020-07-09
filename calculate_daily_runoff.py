#!/usr/bin/env python
"""
Creates daily total runoff netcdfs based on the era5 hourly runoff files (named era5_Ro1_YYYYMMDD.nc) which each contain
24 timesteps (corresponding to the hours of the day)

Args:
    1: path to a directory of era5 hourly runoff files (named era5_Ro1_YYYYMMDD).nc
    2: path to a directory where the aggregated runoff files will be saved

Example Usage:
    python calculate_daily_runoff.py /path/to/hourly/netcdfs/dir /path/to/save/aggregated/netcdfs/dir
"""
import glob
import os
import sys
import time
from datetime import datetime, timedelta

import netCDF4
import numpy as np

# for running this script from the command line
if __name__ == '__main__':
    # Accept the arguments
    runoff_hourly_nc_dir = sys.argv[1]
    runoff_daily_nc_dir = sys.argv[2]

    # find all the hourly netcdf files
    runoff_files = glob.glob(os.path.join(runoff_hourly_nc_dir, '*.nc'))
    for file in runoff_files:
        date = datetime.strptime(os.path.basename(file), 'era5_Ro1_%Y%m%d.nc')
        agg_nc_path = os.path.join(runoff_daily_nc_dir, f'{date.strftime("%Y%m%d")}.nc')
        time_needed = [date + timedelta(hours=i) for i in range(1, 25)]

        with netCDF4.Dataset(file) as ds_src:
            var_time = ds_src.variables['time']
            time_avail = netCDF4.num2date(var_time[:], var_time.units, calendar=var_time.calendar)

            indices = []

            for tm in time_needed:
                a = np.where(time_avail == tm)[0]
                if len(a) == 0:
                    sys.stderr.write(
                        'Error: precipitation data is missing/incomplete - %s!\n' % tm.strftime('%Y%m%d %H:%M:%S'))
                    sys.exit(200)
                else:
                    print('Found %s' % tm.strftime('%Y%m%d %H:%M:%S'))
                    indices.append(a[0])

            var_tp = ds_src.variables['RO']
            tp_values_set = False

            for idx in indices:
                if not tp_values_set:
                    data = var_tp[idx, :, :]
                    tp_values_set = True
                else:
                    data += var_tp[idx, :, :]

            with netCDF4.Dataset(agg_nc_path, mode='w', format='NETCDF3_64BIT_OFFSET') as ds_dest:
                # Dimensions
                for name in ['lat', 'lon']:
                    dim_src = ds_src.dimensions[name]
                    ds_dest.createDimension(name, dim_src.size)
                    var_src = ds_src.variables[name]
                    var_dest = ds_dest.createVariable(name, var_src.datatype, (name,))
                    var_dest[:] = var_src[:]
                    var_dest.setncattr('units', var_src.units)
                    var_dest.setncattr('long_name', var_src.long_name)

                ds_dest.createDimension('time', None)
                var = ds_dest.createVariable('time', np.int32, ('time',))
                time_units = 'hours since 1900-01-01 00:00:00'
                time_cal = 'gregorian'
                var[:] = netCDF4.date2num([date], units=time_units, calendar=time_cal)
                var.setncattr('units', time_units)
                var.setncattr('long_name', 'time')
                var.setncattr('calendar', time_cal)

                # Variables
                var = ds_dest.createVariable(var_tp.name, np.double, var_tp.dimensions)
                var[0, :, :] = data
                var.setncattr('units', var_tp.units)
                var.setncattr('long_name', var_tp.long_name)

                # Attributes
                ds_dest.setncattr('Conventions', 'CF-1.6')
                ds_dest.setncattr('history',
                                  '%s %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ' '.join(time.tzname)))

                print('Done! Daily total runoff saved in %s' % agg_nc_path)
