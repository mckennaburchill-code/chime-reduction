#imports:

from chime.calibration import load_Learmonth_data
from scipy import interpolate

import numpy as np
import glob
from tqdm import trange
import os
from datetime import datetime
import pandas as pd

learmonth = "/home/scratch/dbautist/CHIME_archive/learmonthData/"
learmonth_files = glob.glob(f'{learmonth}/L25*SRD')

#organizing by months + seeing trends:

months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
month_dict = {}

for month in months:
    string = ""
    month_dict[month] = glob.glob(f'{learmonth}/L25{month}*SRD')
    
day_path = month_dict['12'][0] #for all 12 months 
df = load_Learmonth_data(day_path)

#Filtering Process:

def filtering(df):
    median = (not np.isnan(np.nanmedian(df['410']))) and np.nanmedian(df['410']) !=1 and np.nanmedian(df['410'])
    result = median
    return result 

#empty lists:

good_dat = [] #string of good days of data
bad_dat = [] #string of bad days of data

good_date = []
bad_date = []

#Looping process:

for month in months:
    for i in trange(len(month_dict[month])):
        path = month_dict[month][i]
        df = load_Learmonth_data(path)
        
        if filtering(df):
            good_dat.append(path)
        else:
            bad_dat.append(path)
               
#doing the proper dates:

for date in good_dat:
    base = os.path.basename(date)[3:7]
    num_date = int(base)
    good_date.append(num_date)
    
for nodate in bad_dat:
    nobase = os.path.basename(nodate)[3:7]
    no_num_date = int(nobase)
    bad_date.append(no_num_date)

good_datetime = []
bad_datetime = []

for good in good_dat:
    file = os.path.basename(good)
    new_var = datetime.strptime(file, "L%y%m%d.SRD")
    good_datetime.append(new_var)
    
for bad in bad_dat:
    fileb = os.path.basename(bad)
    bad_var = datetime.strptime(fileb, "L%y%m%d.SRD")
    bad_datetime.append(bad_var)

#calculating the fluxes:

raw_flux = [] #empty list for raw flux values throughout year

for i in trange(len(good_dat)):
    p = good_dat[i]
    df = load_Learmonth_data(p)
    raw_flux.append(np.nanmedian(df['410']))
    
flux_Jy = [x * 10000 for x in raw_flux] #converting from counts to Janskys

#interpolating the data:

f = interpolate.interp1d((good_date), (flux_Jy))

good_thing = f(good_date)
est_flux = f(bad_date)

#Pandas DataFrame:

good_flux_data = {
    "Date": good_datetime,
    "Flux": flux_Jy,
    "Source": "Real"
}

bad_flux_data = {
    "Date": bad_datetime,
    "Flux": est_flux,
    "Source": "Interpoliated"
}

good = pd.DataFrame(good_flux_data)
bad = pd.DataFrame(bad_flux_data)

total = [good, bad]
full_list = pd.concat(total)
full_list_sort = full_list.sort_values(by=["Date"])

full_list_sort["Date"] == str

full_list_sort.to_csv("filtering_data.csv", index=False)
filtering = pd.read_csv("filtering_data.csv")



