import numpy as np
import pandas as pd

dict = {'y': 'yes', 'n': 'no'}

filename = input('enter input path/file name (and .ext): ')
filename_cooling = filename.replace('.csv', '_cooling.csv')
filename_heating = filename.replace('.csv', '_heating.csv')
sort = str(input('sort according to temperature(y/n): '))

print('input file name:  ', filename)
print('cooling file name: ', filename_cooling)
print('heating file name: ', filename_heating)
print('sort: ', dict[sort])

df = pd.read_csv(filename)

field_values = [0.02, 2.0, 5.0, 10.0]

for idx in range(len(field_values)):
    
    str1 = 'Temperature (K) @ H='+str(np.round(field_values[idx], decimals=2))+' T'
    str2 = 'Moment (Am^2/kg) @ H='+str(np.round(field_values[idx], decimals=2))+' T'

    df_new = df[[str1, str2]]
    df_new = df_new.dropna()
    minloc = df_new[str1].idxmin()
    df_cool = df_new[:minloc]
    df_heat = df_new[minloc:]

    if sort == 'y':
        df_cool = df_cool.sort_values(by=[str1], ascending=False)
        df_heat = df_heat.sort_values(by=[str1], ascending=True)

    df_cool.index = np.arange(1, len(df_cool) + 1)
    df_heat.index = np.arange(1, len(df_heat) + 1)

    if idx == 0:
        dfnew_cool = df_cool.copy()
        dfnew_heat = df_heat.copy()
    else:
        dfnew_cool = pd.concat([dfnew_cool, df_cool], axis=1)
        dfnew_heat = pd.concat([dfnew_heat, df_heat], axis=1)

# print(dfnew_cool)
# print(dfnew_heat)

dfnew_cool.to_csv(filename_cooling, index=False)
dfnew_heat.to_csv(filename_heating, index=False)