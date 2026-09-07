# -*- coding: utf-8 -*-
"""
Created on Tue May 28 17:11:13 2024

@author: ninoy
"""

import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# Read input data and define output file
# -----------------------------------------------------------------------------
# Ask the user to provide the input and output file paths. Both files are
# expected to be CSV files unless another compatible extension is supplied.
#
# Example:
#     input  -> raw_data/combined_raw_data.csv
#     output -> raw_data/combined_raw_data_sorted.csv
filename = input('enter input path/file name (and .ext): ')
filename_output = input('enter output path/file name (and .ext): ')

# Read the PPMS data into a pandas DataFrame.
df = pd.read_csv(filename)

# -----------------------------------------------------------------------------
# Remove rows containing missing values
# -----------------------------------------------------------------------------
# PPMS data may contain incomplete rows. ``dropna()`` removes every row that
# contains at least one missing value so that subsequent field-based grouping
# operates only on complete measurements.
dfall = df.dropna()

# -----------------------------------------------------------------------------
# Identify unique magnetic-field values
# -----------------------------------------------------------------------------
# Extract all unique magnetic-field values from the ``Magnetic Field (T)``
# column and convert them to floating-point numbers.
#
# ``field_value`` contains the magnetic-field values used as separate field
# steps in the output, while ``num_field_steps`` gives their total number.
field_value = np.unique(np.array(dfall['Magnetic Field (T)'], dtype=np.float64))
num_field_steps = field_value.size

# -----------------------------------------------------------------------------
# Display processing information
# -----------------------------------------------------------------------------
print('input file name:  ', filename)
print('output file name: ', filename_output)
print('number of field steps = ', num_field_steps)
print('field_value = ', field_value)

# -----------------------------------------------------------------------------
# Separate the data according to magnetic-field value
# -----------------------------------------------------------------------------
# ``dataframe_collection_tmp`` temporarily stores one DataFrame for each
# magnetic-field value. The key ``index`` identifies the field step.
#
# ``df_temp`` is progressively reduced during the loop: after extracting one
# field value, those rows are removed before processing the next field value.
df_temp = dfall

dataframe_collection = {}
dataframe_collection_tmp = {}
index = 0
for mft in field_value:

    # Select all measurements taken at the current magnetic field.
    dataframe_collection_tmp[index] = df_temp[df_temp['Magnetic Field (T)'] == mft]

    # Remove the current field from the temporary DataFrame so that the next
    # iteration processes only the remaining field values.
    df_temp1 = df_temp[df_temp['Magnetic Field (T)'] != mft]
    df_temp = df_temp1
    
    # Move to the next field-step index.
    index = index+1

# -----------------------------------------------------------------------------
# Rename columns, reset row numbering, and remove unwanted columns
# -----------------------------------------------------------------------------
# Process each magnetic-field-specific DataFrame individually.
for index in range(0, num_field_steps):

    # Construct field-specific column names. Rounding to two decimal places
    # keeps the output headers compact and easy to read.
    str1 = 'Temperature (K) @ H='+str(np.round(field_value[index], decimals=2))+' T'
    str2 = 'Magnetic Field (Oe) @ H='+str(np.round(field_value[index], decimals=2))+' T'
    str3 = 'Magnetic Field (T) @ H='+str(np.round(field_value[index], decimals=2))+' T'
    str4 = 'Moment (emu) @ H='+str(np.round(field_value[index], decimals=2))+' T'
    str5 = 'Moment (Am^2/kg) @ H='+str(np.round(field_value[index], decimals=2))+' T'
    
    # Create a mapping from the original PPMS column names to the new
    # field-specific column names.
    dict = {'Temperature (K)': str1,
            'Magnetic Field (Oe)': str2,
            'Magnetic Field (T)': str3,
            'Moment (emu)': str4,
            'Moment (Am^2/kg)': str5}
     
    # Rename the columns for the current magnetic-field step.
    dataframe_collection[index] = dataframe_collection_tmp[index].rename(columns=dict)
    
    # Replace the original DataFrame index with sequential numbers beginning
    # at 1. This makes each field-specific measurement series easier to read.
    dataframe_collection[index].index = np.arange(1, len(dataframe_collection[index]) + 1)
    
    # Keep only the temperature and mass-normalized moment columns. Magnetic
    # field columns and moment in emu are removed because the field is already
    # encoded in the column names and the desired output uses Am^2/kg.
    dataframe_collection[index] = dataframe_collection[index].drop([str2, str3, str4], axis=1)
    
# -----------------------------------------------------------------------------
# Combine all field-specific DataFrames
# -----------------------------------------------------------------------------
# Start with the first magnetic-field DataFrame and concatenate every
# subsequent field-specific DataFrame horizontally (column-wise).
dfall_new = dataframe_collection[0].copy()
for index in range(1, num_field_steps):
    dfall_new = pd.concat([dfall_new, dataframe_collection[index]], axis=1)
    
# -----------------------------------------------------------------------------
# Save the reformatted data
# -----------------------------------------------------------------------------
# Write the final DataFrame to the output CSV file. ``index=False`` prevents
# pandas from adding the DataFrame index as an extra column in the CSV.
dfall_new.to_csv(filename_output, index=False)