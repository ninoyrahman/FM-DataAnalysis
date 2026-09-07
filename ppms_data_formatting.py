# -*- coding: utf-8 -*-
"""
Created on Tue May 28 17:11:13 2024

@author: ninoy
"""

import numpy as np
import pandas as pd

## Read data (input and output file names)
# df = pd.read_csv('raw_data/combined_raw_data.csv')
filename = input('enter input path/file name (and .ext): ')
filename_output = input('enter output path/file name (and .ext): ')
df = pd.read_csv(filename)

## Drop NAN
dfall = df.dropna()

## read unique Magnetic Field values
field_value = np.unique(np.array(dfall['Magnetic Field (T)'], dtype=np.float64))
num_field_steps = field_value.size

## print out
print('input file name:  ', filename)
print('output file name: ', filename_output)
print('number of field steps = ', num_field_steps)
print('field_value = ', field_value)

## Separating data based on field values
df_temp = dfall

dataframe_collection = {}
dataframe_collection_tmp = {}
index = 0
for mft in field_value:
    
    dataframe_collection_tmp[index] = df_temp[df_temp['Magnetic Field (T)'] == mft]
    
    df_temp1 = df_temp[df_temp['Magnetic Field (T)'] != mft]
    df_temp = df_temp1
    # print(dataframe_collection_tmp[index]['Magnetic Field (T)'])
    index = index+1
    # print(index)

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
    dataframe_collection[index] = dataframe_collection_tmp[index].rename(columns=dict)
    
    # renumbering dataframe_collection index starting from 1
    dataframe_collection[index].index = np.arange(1, len(dataframe_collection[index]) + 1)
    
    # drop unwanted columns
    dataframe_collection[index] = dataframe_collection[index].drop([str2, str3, str4], axis=1)
    
# combine all  dataframe_collection to a single dataframe
dfall_new = dataframe_collection[0].copy()
for index in range(1, num_field_steps):
    dfall_new = pd.concat([dfall_new, dataframe_collection[index]], axis=1)
    
# Save output data
dfall_new.to_csv(filename_output, index=False)