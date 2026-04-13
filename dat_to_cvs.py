import numpy as np
import scipy as sp
import pandas as pd

# # read file names for concat
# filename_1 = input('first file name: ')
# filename_2 = input('second file name: ')
# filename_3 = input('third file name: ')

# # print file names
# print('file names:')
# print(filename_1)
# print(filename_2)
# print(filename_3)

filename_1 = "raw_data/FM2025_0448_PP_(La0.9Ce0.1)1.06Fe12B6_M-T(0.02,1,2,5,10T)_2.878mg.dat"
filename_2 = "raw_data/FM2025_0448_PP_(La0.9Ce0.1)1.06Fe12B6_M-T(0.25-6T)_2.859mg.dat"
filename_3 = "raw_data/FM2025_0448_PP_(La0.9Ce0.1)1.06Fe12B6_M-T(6.25-9.75T)_2.859mg.dat"

mass_1 = 2.878
mass_2 = 2.859
mass_3 = 2.859

# read input files
f1 = open(filename_1, 'r')
f2 = open(filename_2, 'r')
f3 = open(filename_3, 'r')

# create output file
f4 = open('raw_data/combined_raw_data.csv', 'w')

# find header for first file
header_line_number_1 = 0
for _ in range(40):
    line = f1.readline()
    header_line_number_1 = header_line_number_1 + 1

    if line.rstrip() == "[Data]":
        break

# write first file
for line in f1:
    f4.write(line)

# find header for second file
header_line_number_2 = 0
for _ in range(40):
    line = f2.readline()
    header_line_number_2 = header_line_number_2 + 1

    if line.rstrip() == "[Data]":
        break

# write second file
line = f2.readline()
for line in f2:
    f4.write(line)

# find header for third file
header_line_number_3 = 0
for _ in range(40):
    line = f3.readline()
    header_line_number_3 = header_line_number_3 + 1

    if line.rstrip() == "[Data]":
        break

# write third file
line = f3.readline()
for line in f3:
    f4.write(line)

f1.close()
f2.close()
f3.close()
f4.close()

print(header_line_number_1, header_line_number_2, header_line_number_3)

# df = pd.read_csv('raw_data/combined_raw_data.csv', encoding='cp1252')
df1 = pd.read_csv(filename_1, encoding='cp1252', skiprows=header_line_number_1)
df1['Moment (Am^2/kg)'] = df1['Moment (emu)'] / ((mass_1/1000))
df1.drop(columns=['Comment', 'Time Stamp (sec)', 'Moment (emu)', 'M. Std. Err. (emu)','Transport Action',
                  'Averaging Time (sec)','Frequency (Hz)','Peak Amplitude (mm)','Center Position (mm)','Coil Signal\' (mV)',
                  'Coil Signal\" (mV)','Range (mV)','M. Quad. Signal (emu)','M. Raw\' (emu)','M. Raw\" (emu)','Min. Temperature (K)',
                  'Max. Temperature (K)','Min. Field (Oe)','Max. Field (Oe)','Mass (grams)','Motor Lag (deg)','Pressure (Torr)',
                  'VSM Status (code)','Motor Status (code)','Measure Status (code)','Measure Count','PPMS Status (code)','System Temp. (K)',
                  'System Field (Oe)','Sample Position (deg)','Bridge 1 Resistance (ohms)','Bridge 1 Excitation (µA)','Bridge 2 Resistance (ohms)',
                  'Bridge 2 Excitation (µA)','Bridge 3 Resistance (ohms)','Bridge 3 Excitation (µA)','Bridge 4 Resistance (ohms)','Bridge 4 Excitation (µA)',
                  'Signal 1 Vin (V)','Signal 2 Vin (V)','Digital Inputs (code)','Drive 1 Iout (mA)','Drive 1 Ipower (W)','Drive 2 Iout (mA)',
                  'Drive 2 Ipower (W)','Pressure ()','Map 20 ()','Map 21 ()','Map 22 ()','Map 23 ()','Map 24 ()','Map 25 ()','Map 26 ()','Map 27 ()','Map 28 ()','Map 29 ()'], 
                  axis=1, inplace=True)
print(df1.head(5))


df2 = pd.read_csv(filename_2, encoding='cp1252', skiprows=header_line_number_2)
df2['Moment (Am^2/kg)'] = df2['Moment (emu)'] / ((mass_2/1000))
df2.drop(columns=['Comment', 'Time Stamp (sec)', 'Moment (emu)', 'M. Std. Err. (emu)','Transport Action',
                  'Averaging Time (sec)','Frequency (Hz)','Peak Amplitude (mm)','Center Position (mm)','Coil Signal\' (mV)',
                  'Coil Signal\" (mV)','Range (mV)','M. Quad. Signal (emu)','M. Raw\' (emu)','M. Raw\" (emu)','Min. Temperature (K)',
                  'Max. Temperature (K)','Min. Field (Oe)','Max. Field (Oe)','Mass (grams)','Motor Lag (deg)','Pressure (Torr)',
                  'VSM Status (code)','Motor Status (code)','Measure Status (code)','Measure Count','PPMS Status (code)','System Temp. (K)',
                  'System Field (Oe)','Sample Position (deg)','Bridge 1 Resistance (ohms)','Bridge 1 Excitation (µA)','Bridge 2 Resistance (ohms)',
                  'Bridge 2 Excitation (µA)','Bridge 3 Resistance (ohms)','Bridge 3 Excitation (µA)','Bridge 4 Resistance (ohms)','Bridge 4 Excitation (µA)',
                  'Signal 1 Vin (V)','Signal 2 Vin (V)','Digital Inputs (code)','Drive 1 Iout (mA)','Drive 1 Ipower (W)','Drive 2 Iout (mA)',
                  'Drive 2 Ipower (W)','Pressure ()','Map 20 ()','Map 21 ()','Map 22 ()','Map 23 ()','Map 24 ()','Map 25 ()','Map 26 ()','Map 27 ()','Map 28 ()','Map 29 ()'], 
                  axis=1, inplace=True)
print(df2.head(5))

df3 = pd.read_csv(filename_3, encoding='cp1252', skiprows=header_line_number_3)
df3['Moment (Am^2/kg)'] = df3['Moment (emu)'] / ((mass_3/1000))
df3.drop(columns=['Comment', 'Time Stamp (sec)', 'Moment (emu)', 'M. Std. Err. (emu)','Transport Action',
                  'Averaging Time (sec)','Frequency (Hz)','Peak Amplitude (mm)','Center Position (mm)','Coil Signal\' (mV)',
                  'Coil Signal\" (mV)','Range (mV)','M. Quad. Signal (emu)','M. Raw\' (emu)','M. Raw\" (emu)','Min. Temperature (K)',
                  'Max. Temperature (K)','Min. Field (Oe)','Max. Field (Oe)','Mass (grams)','Motor Lag (deg)','Pressure (Torr)',
                  'VSM Status (code)','Motor Status (code)','Measure Status (code)','Measure Count','PPMS Status (code)','System Temp. (K)',
                  'System Field (Oe)','Sample Position (deg)','Bridge 1 Resistance (ohms)','Bridge 1 Excitation (µA)','Bridge 2 Resistance (ohms)',
                  'Bridge 2 Excitation (µA)','Bridge 3 Resistance (ohms)','Bridge 3 Excitation (µA)','Bridge 4 Resistance (ohms)','Bridge 4 Excitation (µA)',
                  'Signal 1 Vin (V)','Signal 2 Vin (V)','Digital Inputs (code)','Drive 1 Iout (mA)','Drive 1 Ipower (W)','Drive 2 Iout (mA)',
                  'Drive 2 Ipower (W)','Pressure ()','Map 20 ()','Map 21 ()','Map 22 ()','Map 23 ()','Map 24 ()','Map 25 ()','Map 26 ()','Map 27 ()','Map 28 ()','Map 29 ()'], 
                  axis=1, inplace=True)
print(df3.head(5))
