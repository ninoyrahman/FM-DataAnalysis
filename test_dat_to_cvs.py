"""
Convert PPMS .dat measurement files into a combined CSV dataset.

The script supports two PPMS device formats. It locates the ``[Data]``
section, loads the measurement data, removes unused instrument columns,
drops incomplete rows, converts magnetic field from Oe to T, normalizes
magnetic moment by sample mass, concatenates up to three files, and saves
the result as a CSV file.
"""
import pandas as pd
import numpy as np
from tkinter import filedialog, simpledialog

# Select the expected column layout for the chosen PPMS device.
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

# Collect input/output filenames.
filenames = filedialog.askopenfilenames(initialdir="/",
                                                title="File Names",
                                                filetype=(("dat files", "*.dat"),("All Files", "*.*")))

filename_output = filenames[0].replace('.dat', '.csv')
filename_output = simpledialog.askstring("Enter Output File", 
                                            "Enter output path/file name (and .ext):", 
                                            initialvalue=filename_output)

filenumber = len(filenames)
masses = np.zeros(filenumber, dtype=np.float64)
header_line_numbers = np.zeros(filenumber, dtype=np.int32)

# Find mass from the file name.
# Read the file(s), skipping the PPMS header section.
# Remove columns not required for analysis.
# Remove rows containing missing measurement values.
# Convert magnetic field from Oe to T and round to 2 decimal points.
# Normalize moment by sample mass.
# Combine datasets.
index = 0
for filename in filenames:
    file = open(filename, 'r')
    masses[index] = float(filename.split('_')[-1].replace('mg.dat', ''))

    for _ in range(40):
        line = file.readline()
        header_line_numbers[index] += 1
        if line.rstrip() == "[Data]":
            break

    file.close()

    df = pd.read_csv(filename, encoding='cp1252', skiprows=header_line_numbers[index])
    df.drop(columns=columns, axis=1, inplace=True)
    df.dropna(inplace=True)
    df = df.copy()
    df['Magnetic Field (T)'] = np.round(df['Magnetic Field (Oe)'] / (10000.0), 2)
    df['Moment (Am^2/kg)'] = df['Moment (emu)'] / ((masses[index]/1000))

    if index == 0:
        dfall = df.copy(deep=True)
    else:
        dfall = pd.concat([dfall, df])

    index += 1

# Save the combined processed measurements as a CSV file.
# dfall.to_csv(filename_output, index=False)

# Print data
print('PPMS device number = ', ppms_dev_num)
print('masses = ', masses)
print('filename_output = ', filename_output)
print(dfall)