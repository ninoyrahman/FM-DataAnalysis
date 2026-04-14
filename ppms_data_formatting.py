# -*- coding: utf-8 -*-
"""
Created on Tue May 28 17:11:13 2024

@author: ninoy
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

## inputs
cal_type = str(input('Linear field values? type y/n: \n'))
num_field_steps = int(input('Specify the number of field steps:\n'))

if cal_type == 'y':
    initial_field_value = float(input('Specify the initial field value:\n'))
    final_field_value = float(input('Specify the final field value:\n'))
    print('number of field steps = ', num_field_steps)
    print('initial field value = ', initial_field_value)
    print('final field value = ', final_field_value)
    field_value = np.linspace(0.0, final_field_value, num_field_steps)
    field_value[0] = initial_field_value

else: 
    field_value = np.zeros(num_field_steps)
    for i in range(0, num_field_steps):
        field_value[i] = float(input('Enter field values:'))
    print('number of field steps = ', num_field_steps)

## Read data
# df = pd.read_csv('raw data.csv')
df = pd.read_csv('raw_data/combined_raw_data.csv')

## Field mid value calculation
field_value_mid = 0.5*(field_value[1:]+field_value[:-1])
print('field_value = ', field_value)
print('field_value_mid = ', field_value_mid)
# stop

## Unit conversion
mass = float(input('Enter mass in mg:\n'))
dfall = df.dropna()
dfall['Magnetic Field (T)'] = dfall['Magnetic Field (Oe)'] / 10000
# dfall['Moment (Am^2/kg)'] = dfall['Moment (emu)'] / ((mass/1000))
# print(df1.head())

## Separating data based on field values
df_temp = dfall

dataframe_collection = {}
index = num_field_steps-1
for mid in field_value_mid[::-1]:
    # print(mid)
    
    dataframe_collection[index] = df_temp[df_temp['Magnetic Field (T)'] > mid]    
    
    df_temp1 = df_temp[df_temp['Magnetic Field (T)'] < mid]
    df_temp = df_temp1
    # print(dataframe_collection[index]['Magnetic Field (T)'])
    index = index-1
    # print(index)
    
dataframe_collection[index] = df_temp

# rename columns and renumbering index
for index in range(0, num_field_steps):

    str1 = 'Temperature (K) @ H='+str(np.round(field_value[index], decimals=2))+' T'
    str2 = 'Magnetic Field (Oe) @ H='+str(np.round(field_value[index], decimals=2))+' T'
    str3 = 'Magnetic Field (T) @ H='+str(np.round(field_value[index], decimals=2))+' T'
    str4 = 'Moment (emu) @ H='+str(np.round(field_value[index], decimals=2))+' T'
    str5 = 'Moment (Am^2/kg) @ H='+str(np.round(field_value[index], decimals=2))+' T'
    
    # create a dictionary
    dict = {'Temperature (K)': str1,
            'Magnetic Field (Oe)': str2,
            'Magnetic Field (T)': str3,
            'Moment (emu)': str4,
            'Moment (Am^2/kg)': str5}
     
    # rename columns
    dataframe_collection[index].rename(columns=dict, inplace=True)
    
    # renumbering dataframe_collection index starting from 1
    dataframe_collection[index].index = np.arange(1, len(dataframe_collection[index]) + 1)
    
    # drop unwanted columns
    dataframe_collection[index] = dataframe_collection[index].drop([str2, str4], axis=1)
    
    # writing to csv file
    # dataframe_collection[index].to_csv("corrected_raw_data_(La0.7Ce0.3)1.06Fe12B6.csv", 
    #                                     mode='a', index=False, header=True, 
    #                                     columns=[str1, str3, str5])
    
# combine all  dataframe_collection to a single dataframe
dfall_new = dataframe_collection[0].copy()
for index in range(1, num_field_steps):
    dfall_new = pd.concat([dfall_new, dataframe_collection[index]], axis=1)
    
# Save output data
dfall_new.to_csv('raw_data/corrected_raw_data.csv', index=False)
                                       
## plot
# # plt.plot(df1['Temperature (K)'], df1['Moment (emu)'])
# plt.plot(df1['Temperature (K)'], df1['Magnetic Field (T)'])
# plt.xlabel('Temperature (K)')
# # plt.ylabel('Moment (emu)')
# plt.ylabel('Magnetic Field (T)')
# plt.show()