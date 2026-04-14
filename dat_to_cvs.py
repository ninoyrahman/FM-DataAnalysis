import numpy as np
import scipy as sp
import pandas as pd

# function for concating files
def concat_files(*args, **kwargs):
    columns=['Comment', 'Time Stamp (sec)', 'M. Std. Err. (emu)','Transport Action',
                    'Averaging Time (sec)','Frequency (Hz)','Peak Amplitude (mm)','Center Position (mm)','Coil Signal\' (mV)',
                    'Coil Signal\" (mV)','Range (mV)','M. Quad. Signal (emu)','M. Raw\' (emu)','M. Raw\" (emu)','Min. Temperature (K)',
                    'Max. Temperature (K)','Min. Field (Oe)','Max. Field (Oe)','Mass (grams)','Motor Lag (deg)','Pressure (Torr)',
                    'VSM Status (code)','Motor Status (code)','Measure Status (code)','Measure Count','PPMS Status (code)','System Temp. (K)',
                    'System Field (Oe)','Sample Position (deg)','Bridge 1 Resistance (ohms)','Bridge 1 Excitation (µA)','Bridge 2 Resistance (ohms)',
                    'Bridge 2 Excitation (µA)','Bridge 3 Resistance (ohms)','Bridge 3 Excitation (µA)','Bridge 4 Resistance (ohms)','Bridge 4 Excitation (µA)',
                    'Signal 1 Vin (V)','Signal 2 Vin (V)','Digital Inputs (code)','Drive 1 Iout (mA)','Drive 1 Ipower (W)','Drive 2 Iout (mA)',
                    'Drive 2 Ipower (W)','Pressure ()','Map 20 ()','Map 21 ()','Map 22 ()','Map 23 ()','Map 24 ()','Map 25 ()','Map 26 ()','Map 27 ()','Map 28 ()','Map 29 ()']

    # read file names for concat
    # filenumber = int(input('Enter number of files:\n'))
    # filename_1 = input('first file name: ')
    # if filenumber > 1:
    #     filename_2 = input('second file name: ')
    # if filenumber > 2:
    #     filename_3 = input('third file name: ')
    # filename_4 = input('output file name: ')

    # # input masses
    # mass_1 = float(input('Enter mass in mg for first file:\n'))
    # if filenumber > 1:
    #     mass_2 = float(input('Enter mass in mg for second file:\n'))
    # if filenumber > 2:
    #     mass_3 = float(input('Enter mass in mg for third file:\n'))

    filenumber = 3
    filename_1 = "raw_data/FM2025_0448_PP_(La0.9Ce0.1)1.06Fe12B6_M-T(0.02,1,2,5,10T)_2.878mg.dat"
    filename_2 = "raw_data/FM2025_0448_PP_(La0.9Ce0.1)1.06Fe12B6_M-T(0.25-6T)_2.859mg.dat"
    filename_3 = "raw_data/FM2025_0448_PP_(La0.9Ce0.1)1.06Fe12B6_M-T(6.25-9.75T)_2.859mg.dat"
    filename_4 = "raw_data/combined_raw_data.csv"

    mass_1 = 2.878
    mass_2 = 2.859
    mass_3 = 2.859

    # read input files
    f1 = open(filename_1, 'r')
    if filenumber > 1:
        f2 = open(filename_2, 'r')
    if filenumber > 2:
        f3 = open(filename_3, 'r')

    # find header for first file
    header_line_number_1 = 0
    for _ in range(40):
        line = f1.readline()
        header_line_number_1 = header_line_number_1 + 1

        if line.rstrip() == "[Data]":
            break
    f1.close()

    if filenumber > 1:
        # find header for second file
        header_line_number_2 = 0
        for _ in range(40):
            line = f2.readline()
            header_line_number_2 = header_line_number_2 + 1

            if line.rstrip() == "[Data]":
                break
        f2.close()

    if filenumber > 2:
        # find header for third file
        header_line_number_3 = 0
        for _ in range(40):
            line = f3.readline()
            header_line_number_3 = header_line_number_3 + 1

            if line.rstrip() == "[Data]":
                break
        f3.close()

    # print(header_line_number_1, header_line_number_2, header_line_number_3)

    df1 = pd.read_csv(filename_1, encoding='cp1252', skiprows=header_line_number_1)
    df1.drop(columns=columns, axis=1, inplace=True)
    dfnew1 = df1.dropna()
    dfnew1['Moment (Am^2/kg)'] = dfnew1['Moment (emu)'] / ((mass_1/1000))

    if filenumber > 1:
        df2 = pd.read_csv(filename_2, encoding='cp1252', skiprows=header_line_number_2)
        df2.drop(columns=columns, axis=1, inplace=True)
        dfnew2 = df2.dropna()
        dfnew2['Moment (Am^2/kg)'] = dfnew2['Moment (emu)'] / ((mass_2/1000))

    if filenumber > 2:
        df3 = pd.read_csv(filename_3, encoding='cp1252', skiprows=header_line_number_3)
        df3.drop(columns=columns, axis=1, inplace=True)
        dfnew3 = df3.dropna()
        dfnew3['Moment (Am^2/kg)'] = dfnew3['Moment (emu)'] / ((mass_3/1000))

    df4 = dfnew1.copy(deep=True)
    if filenumber > 1:
        df4 = pd.concat([df4, dfnew2])
    if filenumber > 2:
        df4 = pd.concat([df4, dfnew3])
    # df4.drop(columns=['Moment (emu)'], axis=1, inplace=True)
    df4.to_csv(filename_4, index=False)

    df = pd.read_csv(filename_4)

    # print 
    print('')
    print('file name:', filename_1, ', mass = ', mass_1)
    if filenumber > 1:
        print('file name:', filename_2, ', mass = ', mass_2)
    if filenumber > 2:
        print('file name:', filename_3, ', mass = ', mass_3)
    print('')
    print('output file name:', filename_4)
    print(df)