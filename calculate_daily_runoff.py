#!/usr/bin/env python
"""
Save as file calculate-daily-tp.py and run "python calculate-daily-tp.py".

Input file : 2017-01.nc
Output file: 2017-01-01.nc
"""
import time, sys
from datetime import datetime, timedelta

from netCDF4 import Dataset, date2num, num2date
import numpy as np

#listas de fechas
days = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22',
		'23','24','25','26','27','28']
#days = ['29']
#days = ['29', '30']
#days = ['31']
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
#months = ['02']
#months = ['01', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
#months = ['01', '03', '05', '07', '08', '10', '12']
years = ['1979', '1980', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016',
		 '2017', '2018']
#years = ['1981', '1982', '1983', '1984', '1985', '1986', '1987', '1988', '1989', '1990', '1991', '1992', '1993', '1994',
#		 '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002', '2003', '2004']
#years = ['1980', '2008', '2012', '2016']
#years = ['1984', '1988', '1992', '1996', '2000', '2004']

for year in years:
	for month in months:
		for day in days:

			dia = year+month+day
			print(dia)

			d = datetime.strptime(str(dia), '%Y%m%d')
			f_in = '/Volumes/files/ERA-5_hourly_data/ERA5_RO_{0}/era5_Ro1_{0}{1}{2}.nc'.format(year, month, day)
			#f_in = '/Volumes/files/ERA-5_hourly_data/ERA5_RO_{0}/era5_hourly_runoff_{0}{1}{2}.nc'.format(year, month, day)
			#f_in = 'Y:\ERA-5_hourly_data\ERA5_RO_{0}\era5_Ro1_{0}{1}{2}.nc'.format(year, month, day)
			# f_in = 'Y:\ERA-5_hourly_data\ERA5_RO_{0}\era5_hourly_runoff_{0}{1}{2}.nc'.format(year, month, day)
			f_out = '/Volumes/files/ECMWF_Runoff/ERA_5/Daily/{0}{1}{2}.nc'.format(year, month, day)
			# f_out = 'Y:\ECMWF_Runoff\ERA_5\Daily\{0}-{1}-{2}.nc'.format(year, month, day)

			print('{0}-{1}-{2}'.format(year, month, day))

			time_needed = []

			for i in range(1, 25):
				time_needed.append(d + timedelta(hours=i))

			with Dataset(f_in) as ds_src:
				var_time = ds_src.variables['time']
				time_avail = num2date(var_time[:], var_time.units, calendar=var_time.calendar)

				indices = []

				for tm in time_needed:
					a = np.where(time_avail == tm)[0]
					if len(a) == 0:
						sys.stderr.write('Error: precipitation data is missing/incomplete - %s!\n' % tm.strftime('%Y%m%d %H:%M:%S'))
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

				#data = data/24

				with Dataset(f_out, mode='w', format='NETCDF3_64BIT_OFFSET') as ds_dest:
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
					var[:] = date2num([d], units=time_units, calendar=time_cal)
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
					ds_dest.setncattr('history', '%s %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ' '.join(time.tzname)))

					print('Done! Daily total runoff saved in %s' % f_out)
