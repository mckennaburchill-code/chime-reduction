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
bad_datetimes = []

for good in good_dat:
    file = os.path.basename(good)
    new_var = datetime.strptime(file, "L%y%m%d.SRD")
    good_datetime.append(new_var)
    
for bad in bad_dat:
    fileb = os.path.basename(bad)
    bad_var = datetime.strptime(fileb, "L%y%m%d.SRD")
    bad_datetimes.append(bad_var)
    
bad_list = [datetime.strptime("L250119.SRD", "L%y%m%d.SRD"),
    datetime.strptime("L250120.SRD", "L%y%m%d.SRD"),
    datetime.strptime("L250719.SRD", "L%y%m%d.SRD"),
    datetime.strptime("L250720.SRD", "L%y%m%d.SRD"),
    datetime.strptime("L250830.SRD", "L%y%m%d.SRD"),
    datetime.strptime("L250831.SRD", "L%y%m%d.SRD"),
    datetime.strptime("L250901.SRD", "L%y%m%d.SRD")]
bad_list.sort()
    
bad_datetime = sorted(bad_datetimes + bad_list)
dates = sorted(good_date + bad_date)

#calculating the fluxes:

raw_flux = [] #empty list for raw flux values throughout year

for i in trange(len(good_dat)):
    p = good_dat[i]
    df = load_Learmonth_data(p)
    raw_flux.append(np.nanmedian(df['410']))
    
flux_Jy = [x * 10000 for x in raw_flux] #converting from counts to Janskys

#interpolating the data:

datetime_bad = []

known_jan_points = list(range(101, 132))
known_feb_points = list(range(201, 229))
known_mar_points = list(range(301, 332))
known_apr_points = list(range(401, 431))
known_may_points = list(range(501, 532))
known-jun_points = list(range(601, 631))
known_jul_points = list(range(701, 732))
known_aug_points = list(range(801, 832))
known_sept_points = list(range(901, 931))
known_oct_points = list(range(1001, 1131))
known_nov_points = list(range(1101, 1131))
known_dec_points = list(range(1201, 1232))



real1 = dates[0:29]      #Jan
real2 = dates[30:47]
real3 = dates[48:79]
real4 = dates[80:110]
real5 = dates[111:142]
real6 = dates[143:178]
real7 = dates[179:208]   #July
real8 = dates[207:237]   #August
real9 = dates[237:266]   #Sept
real10 = dates[265:296]
real11 = dates[295:325]
real12 = dates[32]


dont_existJ = [item for item in known_jan_points if item not in real1]
dont_existJu = [item for item in known_jul_points if item not in real2]
dont_existaug = [item for item in known_aug_points if item not in real3]
dont_existsep = [item for item in known_sept_points if item not in real4]

dont_exist = sorted(dont_existJ + dont_existJu + dont_existaug + dont_existsep)
bad_dates = sorted(bad_date + dont_exist)

f = interpolate.interp1d((good_date), (flux_Jy))

good_thing = f(good_date)
est_flux = f(bad_dates)

datetime_bad = []

for num in bad_dates:
    date_str = f"{int(num):04d}"
    full_date_str = f"2025{date_str}"
    
    dt_obj = datetime.strptime(full_date_str, "%Y%m%d")

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

full_list_sort.to_csv("filtering_data_exist.csv", index=False)

