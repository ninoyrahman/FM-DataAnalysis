import pandas as pd
import numpy as np
from tkinter import filedialog, simpledialog

def convert_dat_to_cvs_MH():
    """
    Convert PPMS .dat measurement files into a combined CSV dataset.

    The script supports two PPMS device formats. It locates the ``[Data]``
    section, loads the measurement data, removes unused instrument columns,
    drops incomplete rows, converts magnetic field from Oe to T, normalizes
    magnetic moment by sample mass, concatenates up to three files, and saves
    the result as a CSV file.
    """

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

    filename_output = filenames[0].replace('.dat', '.csv').replace('.DAT', '.csv')
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
        masses[index] = float(filename.split('_')[-1].replace('mg.dat', '').replace('mg.DAT', ''))

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
        df['Magnetic Field (T)'] = np.round(df['Magnetic Field (Oe)'] / (10000.0), 4)
        df['Moment (Am^2/kg)'] = df['Moment (emu)'] / ((masses[index]/1000))
        df['Temperature (K)'] = np.round(df['Temperature (K)'], 0)

        if index == 0:
            dfall = df.copy(deep=True)
        else:
            dfall = pd.concat([dfall, df])

        index += 1

    # Save the combined processed measurements as a CSV file.
    dfall.to_csv(filename_output, index=False)

    # Print data
    print('PPMS device number = ', ppms_dev_num)
    print('masses = ', masses)
    print('filename_output = ', filename_output)
    print(dfall)

def ppms_data_formatting_MH():
    """
    PPMS Magnetic Data Formatting
    =============================

    This script reformats PPMS magnetic measurement data stored in a CSV file.

    Workflow
    --------
    1. Ask the user for the input and output CSV file paths.
    2. Read the PPMS data into a pandas DataFrame.
    3. Remove rows containing missing (NaN) values.
    4. Identify all unique magnetic-field values.
    5. Separate the measurements into individual DataFrames for each field.
    6. Rename the columns so that each column identifies its corresponding field.
    7. Keep only temperature and mass-normalized magnetic moment for each field.
    8. Combine the field-specific data side-by-side into one DataFrame.
    9. Save the reformatted data as a CSV file.

    Expected input columns
    ----------------------
    The input CSV file is expected to contain at least the following columns:
        - Temperature (K)
        - Magnetic Field (Oe)
        - Magnetic Field (T)
        - Moment (emu)
        - Moment (Am^2/kg)

    Notes
    -----
    - All rows containing at least one NaN value are removed before processing.
    - The unique values in ``Magnetic Field (T)`` determine the field steps.
    - The output contains temperature and mass-normalized moment for each field.
    """

    # -----------------------------------------------------------------------------
    # Read input data and define output file
    # -----------------------------------------------------------------------------
    # Ask the user to provide the input and output file paths. Both files are
    # expected to be CSV files unless another compatible extension is supplied.
    #
    # Example:
    #     input  -> raw_data/combined_raw_data.csv
    #     output -> raw_data/combined_raw_data_sorted.csv
    filename = filedialog.askopenfilename(initialdir="/",
                                                title="Select Input File",
                                                filetype=(("csv files", "*.csv"),("All Files", "*.*")))

    filename_output = filename.replace('.csv', '_MH_sorted.csv')
    filename_output = simpledialog.askstring("Enter Output File", 
                                            "Enter output path/file name (and .ext):", 
                                            initialvalue=filename_output)
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
    # Identify unique temperature values
    # -----------------------------------------------------------------------------
    # Extract all unique temperature values from the ``Temperature (K)``
    # column and convert them to floating-point numbers.
    #
    # ``field_value`` contains the magnetic-field values used as separate field
    # steps in the output, while ``num_field_steps`` gives their total number.
    temp = np.unique(np.array(dfall['Temperature (K)'], dtype=np.float64))
    num_temp_steps = temp.size

    filename_temps = filename.replace('.csv', '_temp.csv')
    df_temps = pd.DataFrame(columns=['Temperature (K)'])
    df_temps['Temperature (K)'] = temp
    df_temps.to_csv(filename_temps, index=False)

    # -----------------------------------------------------------------------------
    # Display processing information
    # -----------------------------------------------------------------------------
    print('input file name:  ', filename)
    print('output file name: ', filename_output)
    print('temperature file name: ', filename_temps)
    print('number of temperature steps = ', num_temp_steps)
    print('temperature value = ', temp)

    # -----------------------------------------------------------------------------
    # Separate the data according to temperature value
    # -----------------------------------------------------------------------------
    # ``dataframe_collection_tmp`` temporarily stores one DataFrame for each
    # temperature value. The key ``index`` identifies the temperature step.
    #
    # ``df_temp`` is progressively reduced during the loop: after extracting one
    # temperature value, those rows are removed before processing the next temperature value.
    df_temp = dfall

    dataframe_collection = {}
    dataframe_collection_tmp = {}
    index = 0
    for temperature in temp:

        # Select all measurements taken at the current temperature.
        dataframe_collection_tmp[index] = df_temp[df_temp['Temperature (K)'] == temperature]

        # Remove the current temperature from the temporary DataFrame so that the next
        # iteration processes only the remaining temperature values.
        df_temp1 = df_temp[df_temp['Temperature (K)'] != temperature]
        df_temp = df_temp1
        
        # Move to the next temperature-step index.
        index = index+1

    # -----------------------------------------------------------------------------
    # Rename columns, reset row numbering, and remove unwanted columns
    # -----------------------------------------------------------------------------
    # Process each magnetic-field-specific DataFrame individually.
    for index in range(0, num_temp_steps):

        # Construct field-specific column names. Rounding to two decimal places
        # keeps the output headers compact and easy to read.
        str1 = 'Temperature (K) @ T='+str(np.round(temp[index], decimals=0))+' K'
        str2 = 'Magnetic Field (Oe) @ T='+str(np.round(temp[index], decimals=2))+' K'
        str3 = 'Magnetic Field (T) @ T='+str(np.round(temp[index], decimals=2))+' K'
        str4 = 'Moment (emu) @ T='+str(np.round(temp[index], decimals=2))+' K'
        str5 = 'Moment (Am^2/kg) @ T='+str(np.round(temp[index], decimals=2))+' K'
        
        # Create a mapping from the original PPMS column names to the new
        # field-specific column names.
        dict = {'Temperature (K)': str1,
                'Magnetic Field (Oe)': str2,
                'Magnetic Field (T)': str3,
                'Moment (emu)': str4,
                'Moment (Am^2/kg)': str5}
        
        # Rename the columns for the current temperature step.
        dataframe_collection[index] = dataframe_collection_tmp[index].rename(columns=dict)
        
        # Replace the original DataFrame index with sequential numbers beginning
        # at 1. This makes each temperature-specific measurement series easier to read.
        dataframe_collection[index].index = np.arange(1, len(dataframe_collection[index]) + 1)
        
        # Keep only the field and mass-normalized moment columns. Magnetic
        # field columns and moment in emu are removed because the field is already
        # encoded in the column names and the desired output uses Am^2/kg.
        dataframe_collection[index] = dataframe_collection[index].drop([str1, str2, str4], axis=1)

        # print(dataframe_collection[index])
        
    # -----------------------------------------------------------------------------
    # Combine all field-specific DataFrames
    # -----------------------------------------------------------------------------
    # Start with the first magnetic-field DataFrame and concatenate every
    # subsequent field-specific DataFrame horizontally (column-wise).
    dfall_new = dataframe_collection[0].copy()
    for index in range(1, num_temp_steps):
        dfall_new = pd.concat([dfall_new, dataframe_collection[index]], axis=1)
        
    # -----------------------------------------------------------------------------
    # Save the reformatted data
    # -----------------------------------------------------------------------------
    # Write the final DataFrame to the output CSV file. ``index=False`` prevents
    # pandas from adding the DataFrame index as an extra column in the CSV.
    dfall_new.to_csv(filename_output, index=False)

def magnetization_demagnetization_seperation():
    """
    Separate PPMS temperature-dependent measurements into magnetization and demagnetization datasets.

    For each specified temperature, this script selects the corresponding
    field and mass-normalized moment columns, removes missing values,
    identifies the maximum-field point, and splits the measurements into
    magnetization and demagnetization segments. The resulting datasets are optionally sorted
    by field and saved as separate CSV files.

    The input CSV is selected using a graphical file-selection dialog.
    """

    # Select the input CSV file.
    filename = filedialog.askopenfilename(initialdir="/",
                                                title="Select Input File",
                                                filetype=(("csv files", "*.csv"),("All Files", "*.*")))
    filename_temps = filename.replace('_MH_sorted.csv', '_temp.csv')
    filename_temps = simpledialog.askstring("Enter Field File", 
                                            "Enter field path/file name (and .ext):", 
                                            initialvalue=filename_temps) 
    # Construct output filenames for the cooling and heating datasets.
    filename_magnetization = filename.replace('.csv', '_magnetization.csv')
    filename_demagnetization = filename.replace('.csv', '_demagnetization.csv')
    # Ask whether each dataset should be sorted by temperature.
    sort = simpledialog.askstring("Sort Data", 
                                "Sort according to field(yes/no):", 
                                initialvalue='no')
    remove_neg_field = simpledialog.askstring("Remove Negative Fields",
                                "Remove negative field values(yes/no):",
                                initialvalue='no')

    print('input file name:  ', filename)
    print('temperature file name:  ', filename_temps)
    print('cooling file name: ', filename_magnetization)
    print('heating file name: ', filename_demagnetization)
    print('sort: ', sort)
    print('Remove negative fields: ', remove_neg_field)

    # Load the combined PPMS measurement data.
    df = pd.read_csv(filename)

    # Temperature values to process, in K.
    df_temps = pd.read_csv(filename_temps)
    temp_values = list(df_temps['Temperature (K)'])
    temp_values.sort()

    # Process each temperature independently.
    for idx in range(len(temp_values)):
        
        str1 = 'Magnetic Field (T) @ T='+str(np.round(temp_values[idx], decimals=0))+' K'
        str2 = 'Moment (Am^2/kg) @ T='+str(np.round(temp_values[idx], decimals=0))+' K'

        # Keep magnetic field and mass-normalized moment for this field.
        df_new = df[[str1, str2]]
        # Remove rows with missing measurement values.
        df_new = df_new.dropna()
        # Remove rows with negative field values.
        if remove_neg_field == 'yes':
            df_new = df_new[df_new[str1] > 0]
        # Use the maximum-field point as the magnetization/demagnetization boundary.
        maxloc = df_new[str1].idxmax()
        df_mag = df_new[:maxloc]
        df_dem = df_new[maxloc:]

        # Optionally sort magnetization from low-to-high field and demagnetization from high-to-low field.
        if sort == 'yes':
            df_mag = df_mag.sort_values(by=[str1], ascending=True)
            df_dem = df_dem.sort_values(by=[str1], ascending=False)

        # Reset the index so it starts at 1.
        df_mag.index = np.arange(1, len(df_mag) + 1)
        df_dem.index = np.arange(1, len(df_dem) + 1)

        # Combined the datasets for magnetization/demagnetization.
        if idx == 0:
            dfnew_mag = df_mag.copy()
            dfnew_dem = df_dem.copy()
        else:
            dfnew_mag = pd.concat([dfnew_mag, df_mag], axis=1)
            dfnew_dem = pd.concat([dfnew_dem, df_dem], axis=1)

    # Save the separated magnetization/demagnetization dataset.
    dfnew_mag.to_csv(filename_magnetization, index=False)
    dfnew_dem.to_csv(filename_demagnetization, index=False)