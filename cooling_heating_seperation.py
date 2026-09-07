"""
Separate PPMS temperature-dependent measurements into cooling and heating datasets.

For each specified magnetic field, this script selects the corresponding
temperature and mass-normalized moment columns, removes missing values,
identifies the minimum-temperature point, and splits the measurements into
cooling and heating segments. The resulting datasets are optionally sorted
by temperature and saved as separate CSV files.

The input CSV is selected using a graphical file-selection dialog.
"""

import numpy as np
import pandas as pd
from tkinter import filedialog, simpledialog

# Select the input CSV file.
filename = filedialog.askopenfilename(initialdir="/",
                                            title="Select Input File",
                                            filetype=(("csv files", "*.csv"),("All Files", "*.*")))
# Construct output filenames for the cooling and heating datasets.
filename_cooling = filename.replace('.csv', '_cooling.csv')
filename_heating = filename.replace('.csv', '_heating.csv')
# Ask whether each dataset should be sorted by temperature.
sort = simpledialog.askstring("Sort Data", 
                            "Sort according to temperature(yes/no):", 
                            initialvalue='no')

print('input file name:  ', filename)
print('cooling file name: ', filename_cooling)
print('heating file name: ', filename_heating)
print('sort: ', sort)

# Load the combined PPMS measurement data.
df = pd.read_csv(filename)

# Magnetic-field values to process, in tesla.
field_values = [0.02, 2.0, 5.0, 10.0]

# Process each magnetic field independently.
for idx in range(len(field_values)):
    
    str1 = 'Temperature (K) @ H='+str(np.round(field_values[idx], decimals=2))+' T'
    str2 = 'Moment (Am^2/kg) @ H='+str(np.round(field_values[idx], decimals=2))+' T'

    # Keep temperature and mass-normalized moment for this field.
    df_new = df[[str1, str2]]
    # Remove rows with missing measurement values.
    df_new = df_new.dropna()
    # Use the minimum-temperature point as the cooling/heating boundary.
    minloc = df_new[str1].idxmin()
    df_cool = df_new[:minloc]
    df_heat = df_new[minloc:]

    # Optionally sort cooling from high-to-low T and heating from low-to-high T.
    if sort == 'yes':
        df_cool = df_cool.sort_values(by=[str1], ascending=False)
        df_heat = df_heat.sort_values(by=[str1], ascending=True)

    # Reset the index so it starts at 1.
    df_cool.index = np.arange(1, len(df_cool) + 1)
    df_heat.index = np.arange(1, len(df_heat) + 1)

    # Combined the datasets for cooling/heating.
    if idx == 0:
        dfnew_cool = df_cool.copy()
        dfnew_heat = df_heat.copy()
    else:
        dfnew_cool = pd.concat([dfnew_cool, df_cool], axis=1)
        dfnew_heat = pd.concat([dfnew_heat, df_heat], axis=1)

# Save the separated cooling/heating dataset.
dfnew_cool.to_csv(filename_cooling, index=False)
dfnew_heat.to_csv(filename_heating, index=False)