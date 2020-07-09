# Update ERA-5 Workflow

The purpose of these scripts is to update the ERA-5 RAPID simulation and corresponding return periods each year. The ERA-5 Historical Simulation is part of the GEOGloWS ECMWF Streamflow Model.

## Required Setup

1. Install RAPID and RAPIDpy. The version of RAPIDpy should come from https://github.com/BYU-Hydroinformatics/RAPIDpy because it can process the ERA-5 grid.
2. RAPID needs access to a folder with the ERA-5 gridded runoff data from ECMWF. This data is normally stored in daily netcdf files.
    1. The runoff grids need to be aggregated from hourly to DAILY values. There is a script included if needed.
3. Create a rapid-input directory that has subfolders for each region. Each region needs the required RAPID input files and the ERA-5 weight table (weight_era_t640.csv). This can be the same input folder used for the forecasts.
    1. The input folder for each region also needs to have an initial flows file from the last ERA-5 simulation (eg: "qinit_era5_t640_24hr_19790101to20181231.csv"). The filename must start with "qinit_era5" and end with "YYYYMMDDtoYYYYMMDD.csv".
4. Create or identify the output folder. This should be different from the forecast output directory and could be named 'era-5'. The output folder for rapid can be the same location as where the complete historical simulation files are stored.
5. Create a directory for log files.
7. Other python dependencies in addition to RAPIDpy: python 3+, netCDF4, numpy, pandas, statistics

## Workflow description
There are 4 scripts involved in this workflow which you need to execute in this order:
1. calculate-daily-runoff.py
    1. This script aggregates hourly runoff to daily. 
2. run_era5_rapid.py
    1. This script runs rapid for a whole year of ERA-5 Runoff data (should be aggregated to daily). It reads an initial flows file which was created at the end of the previous simulation. A new file will be created at the end of the next simulation as well.
    2. The script needs to be stored in a place where it can access the RAPIDpy code.
3. append_era5.py
    1. This script appends the recently created 1-yr simulation onto the 40-yr+ netCDF for each region.
4. generate_gumbel_return_periods.py
    1. This script calculates gumbel return periods based on the newly updated simulation. It needs daily values to work.  


## Running the scripts.

Each script needs additional arguments in order to run. These are explained in each .py file. For example:

For Example: 
```bash
python run_era5_rapid.py /home/rapid/run/rapid /mnt/era5_daily_runoff /home/rapid-io/input /home/era-5 /home/logs 2020
```
```bash
python append_era5.py /home/era-5 /home/era-5 /home/logs 2020
```
```bash
python generate_gumbel_return_periods.py /home/era-5 /home/logs 2020
```


Lastly, the scripts need to be in a place where they can access the RAPIDpy code (see imports_era5_workflow.py). 
