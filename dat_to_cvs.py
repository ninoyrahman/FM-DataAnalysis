"""Convert PPMS .dat measurement files into a combined CSV dataset.

The script supports two PPMS device formats. It locates the ``[Data]``
section, loads the measurement data, removes unused instrument columns,
drops incomplete rows, converts magnetic field from Oe to T, normalizes
magnetic moment by sample mass, concatenates up to three files, and saves
the result as a CSV file.

The ``debug`` argument controls whether filenames and masses are entered
interactively (``False``) or predefined test data are used (``True``).
"""

import pandas as pd
import numpy as np
from tkinter import filedialog, simpledialog

# function for concating files
def concat_files(debug=True):
    """Process and concatenate one to three PPMS measurement files.

    Args:
        debug (bool): Use predefined test inputs when True; otherwise
            request filenames and sample masses interactively.

    Returns:
        None: The processed data are written to the requested CSV file.
    """
    ppms_dev_num = simpledialog.askinteger('PPMS Device Number', 'Enter PPMS device number', initialvalue=1, minvalue=1, maxvalue=2)

    # Select the expected column layout for the chosen PPMS device.
    if ppms_dev_num == 1:
        columns=['Comment', 'Time Stamp (sec)', 'M. Std. Err. (emu)','Transport Action',
                        'Averaging Time (sec)','Frequency (Hz)','Peak Amplitude (mm)','Center Position (mm)','Coil Signal\' (mV)',
                        'Coil Signal\" (mV)','Range (mV)','M. Quad. Signal (emu)','M. Raw\' (emu)','M. Raw\" (emu)','Min. Temperature (K)',
                        'Max. Temperature (K)','Min. Field (Oe)','Max. Field (Oe)','Mass (grams)','Motor Lag (deg)','Pressure (Torr)',
                        'VSM Status (code)','Motor Status (code)','Measure Status (code)','Measure Count','PPMS Status (code)','System Temp. (K)',
                        'System Field (Oe)','Sample Position (deg)','Bridge 1 Resistance (ohms)','Bridge 1 Excitation (µA)','Bridge 2 Resistance (ohms)',
                        'Bridge 2 Excitation (µA)','Bridge 3 Resistance (ohms)','Bridge 3 Excitation (µA)','Bridge 4 Resistance (ohms)','Bridge 4 Excitation (µA)',
                        'Signal 1 Vin (V)','Signal 2 Vin (V)','Digital Inputs (code)','Drive 1 Iout (mA)','Drive 1 Ipower (W)','Drive 2 Iout (mA)',
                        'Drive 2 Ipower (W)','Pressure ()','Map 20 ()','Map 21 ()','Map 22 ()','Map 23 ()','Map 24 ()','Map 25 ()','Map 26 ()','Map 27 ()','Map 28 ()','Map 29 ()']
    elif ppms_dev_num == 2:
        columns=['Comment', 'Time Stamp (sec)', 'M. Std. Err. (emu)','Transport Action',
                            'Averaging Time (sec)','Frequency (Hz)','Peak Amplitude (mm)','Center Position (mm)','Coil Signal\' (mV)',
                            'Coil Signal\" (mV)','Range (mV)','M. Quad. Signal (emu)','M. Raw\' (emu)','M. Raw\" (emu)','Min. Temperature (K)',
                            'Max. Temperature (K)','Min. Field (Oe)','Max. Field (Oe)','Mass (grams)','Motor Lag (deg)','Pressure (Torr)',
                            'VSM Status (code)','Motor Status (code)','Measure Status (code)','Measure Count','System Temp. (K)',
                            'Temp. Status (code)','Field Status (code)','Chamber Status (code)','Position Status (code)',
                            'Evercool Status (code)','Motor Current (amps)','Motor Heatsink Temp. (C)',
                            'System Field (Oe)','Sample Position (deg)','Bridge 1 Resistance (ohms)','Bridge 1 Excitation (µA)','Bridge 2 Resistance (ohms)',
                            'Bridge 2 Excitation (µA)','Bridge 3 Resistance (ohms)','Bridge 3 Excitation (µA)','Bridge 4 Resistance (ohms)','Bridge 4 Excitation (µA)',
                            'Signal 1 Vin (V)','Signal 2 Vin (V)','Digital Inputs (code)','Drive 1 Iout (mA)','Drive 1 Ipower (W)','Drive 2 Iout (mA)',
                            'Drive 2 Ipower (W)','Pressure ()','Map 20 ()','Map 21 ()','Map 22 ()','Map 23 ()','Map 24 ()','Map 25 ()','Map 26 ()','Map 27 ()','Map 28 ()','Map 29 ()']
    else:
        print('Error: wrong device number')
    
    # Collect input/output filenames and sample masses.
    if not debug:
        filenumber = simpledialog.askinteger('Enter File Number', 'Enter number of input files', initialvalue=1, minvalue=1, maxvalue=3)

        filename_1 = filedialog.askopenfilename(initialdir="/",
                                                title="First File Name",
                                                filetype=(("dat files", "*.dat"),("All Files", "*.*")))
        if filenumber > 1:
            filename_2 = filedialog.askopenfilename(initialdir="/",
                                                    title="Second File Name",
                                                    filetype=(("dat files", "*.dat"),("All Files", "*.*")))
        if filenumber > 2:
            filename_3 = filedialog.askopenfilename(initialdir="/",
                                                    title="Third File Name",
                                                    filetype=(("dat files", "*.dat"),("All Files", "*.*")))
        filename_4 = filename_1.replace('.dat', '.csv')
        filename_4 = simpledialog.askstring("Enter Output File", 
                                            "Enter output path/file name (and .ext):", 
                                            initialvalue=filename_4)

        # input masses
        mass_1 = float(filename_1.split('_')[-1].replace('mg.dat', ''))
        if filenumber > 1:
            mass_2 = float(filename_2.split('_')[-1].replace('mg.dat', ''))
        if filenumber > 2:
            mass_3 = float(filename_3.split('_')[-1].replace('mg.dat', ''))
    else:
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

    # Read the file(s), skipping the PPMS header section.
    # Remove columns not required for analysis.
    # Remove rows containing missing measurement values.
    # Convert magnetic field from Oe to T and round to 2 decimal points.
    # Normalize moment by sample mass.
    df1 = pd.read_csv(filename_1, encoding='cp1252', skiprows=header_line_number_1)
    df1.drop(columns=columns, axis=1, inplace=True)
    dfnew1 = df1.dropna()
    dfnew1['Magnetic Field (T)'] = np.round(dfnew1['Magnetic Field (Oe)'] / (10000.0), 2)
    dfnew1['Moment (Am^2/kg)'] = dfnew1['Moment (emu)'] / ((mass_1/1000))

    if filenumber > 1:
        df2 = pd.read_csv(filename_2, encoding='cp1252', skiprows=header_line_number_2)
        df2.drop(columns=columns, axis=1, inplace=True)
        dfnew2 = df2.dropna()
        dfnew2['Magnetic Field (T)'] = np.round(dfnew2['Magnetic Field (Oe)'] / (10000.0), 2)
        dfnew2['Moment (Am^2/kg)'] = dfnew2['Moment (emu)'] / ((mass_2/1000))

    if filenumber > 2:
        df3 = pd.read_csv(filename_3, encoding='cp1252', skiprows=header_line_number_3)
        df3.drop(columns=columns, axis=1, inplace=True)
        dfnew3 = df3.dropna()
        dfnew3['Magnetic Field (T)'] = np.round(dfnew3['Magnetic Field (Oe)'] / (10000.0), 2)
        dfnew3['Moment (Am^2/kg)'] = dfnew3['Moment (emu)'] / ((mass_3/1000))

    # Combine datasets.
    df4 = dfnew1.copy(deep=True)
    if filenumber > 1:
        df4 = pd.concat([df4, dfnew2])
    if filenumber > 2:
        df4 = pd.concat([df4, dfnew3])
    # df4.drop(columns=['Moment (emu)'], axis=1, inplace=True)
    df4.to_csv(filename_4, index=False)

    # Save the combined processed measurements as a CSV file.
    df = pd.read_csv(filename_4)

    # Reload the saved CSV for a final check.
    print('')
    print('file name:', filename_1, ', mass = ', mass_1)
    if filenumber > 1:
        print('file name:', filename_2, ', mass = ', mass_2)
    if filenumber > 2:
        print('file name:', filename_3, ', mass = ', mass_3)
    print('')
    print('output file name:', filename_4)
    print(df)