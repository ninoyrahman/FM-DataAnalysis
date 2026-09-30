import pandas as pd
import numpy as np
from tkinter import filedialog, simpledialog
from matplotlib import pyplot as plt
from matplotlib import rcParams
from scipy.interpolate import interp1d
from scipy.integrate import cumulative_trapezoid

def convert_dat_to_cvs_Cp():
    """
    Convert PPMS .dat measurement files into a combined CSV dataset.

    The script supports two PPMS device formats. It locates the ``[Data]``
    section, loads the measurement data, removes unused instrument columns,
    drops incomplete rows, converts magnetic field from Oe to T, normalizes
    magnetic moment by sample mass, concatenates up to three files, and saves
    the result as a CSV file.
    """
    is_pulse = simpledialog.askstring("Pulse Data", 
                                "Is it pulse data(yes/no):", 
                                initialvalue='no')
    
    # Select the expected column layout for the chosen continuous or pulse data.
    if is_pulse == 'yes':
        columns=[' HCTotal (uJ/K)']
    else:
        columns=['Time Stamp (Seconds)', 'Comment ()', 'System Status (Code)', 'Puck Temp (Kelvin)', 'System Temp (Kelvin)', 'Pressure (Torr)', 
                'Temp Rise (Kelvin)', 'Samp HC Err (µJ/K)', 'Addenda HC (µJ/K)', 'Addenda HC Err (µJ/K)', 'Total HC (µJ/K)', 
                'Total HC Err (µJ/K)', 'Fit Deviation (ChiSquare)', 'Time Const tau1 (seconds)', 'Time Const tau2 (seconds)', 'Sample Coupling (Percent)',
                'Debye Temp (Kelvin)', 'Debye Temp Err (Kelvin)', 'Cal Correction (Factor)', 'Therm Resist (Ohms)', 'Htr Resist (Ohms)', 'Puck Resist (Ohms)',
                'Wire Cond (W/K)', 'Meas Time (seconds)', 'Temp Squared (K^2)', 'Samp HC/Temp (µJ/K/K)', 'Addenda Offset HC (µJ/K)']
        
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

        if is_pulse == 'yes':
            field_value = np.round(df[' Field (Oe)'] / (10000.0), 2).max()
            str1 = 'Temperature (pulse) (K) @ H='+str(np.round(field_value, decimals=2))+' T'
            str2 = 'Cp (pulse) (J/Kg/K) @ H='+str(np.round(field_value, decimals=2))+' T'

            df[str1] = df['Temperature (K)']
            df[str2] = df[' HCSample (µJ/K)'] / (masses[index])
            df.drop(columns=['Temperature (K)', ' Field (Oe)', ' HCSample (µJ/K)'], axis=1, inplace=True)
        else:
            df['Magnetic Field (T)'] = np.round(df['Field (Oersted)'] / (10000.0), 2)
            df['Cp (J/Kg/K)'] = df['Samp HC (µJ/K)'] / (masses[index])
            df.drop(columns=['Field (Oersted)', 'Samp HC (µJ/K)'], axis=1, inplace=True)

        if index == 0:
            dfall = df.copy(deep=True)
        else:
            dfall = pd.concat([dfall, df])

        index += 1

    # Save the combined processed measurements as a CSV file.
    dfall.to_csv(filename_output, index=False)

    # Print data
    print('masses = ', masses)
    print('filename_output = ', filename_output)
    print(dfall)

def ppms_data_formatting_Cp():
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
        - Sample Temp (Kelvin)
        - Magnetic Field (T)
        - Cp (J/Kg/K)

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
    is_pulse = simpledialog.askstring("Pulse Data", 
                                "Is it pulse data(yes/no):", 
                                initialvalue='no')
    
    # Select the expected column layout for the chosen continuous or pulse data.
    if is_pulse == 'yes':
        filename = filedialog.askopenfilename(initialdir="/",
                                            title="Select Input File",
                                            filetype=(("csv files", "*.csv"),("All Files", "*.*")))

        filename_output = filename.replace('.csv', '_sorted.csv')
        filename_output = simpledialog.askstring("Enter Output File", 
                                                "Enter output path/file name (and .ext):", 
                                                initialvalue=filename_output)
        
        # Read the PPMS data into a pandas DataFrame.
        df = pd.read_csv(filename)
        temp = np.array(df[df.columns[0]], dtype=np.float64)
        Cp = np.array(df[df.columns[1]], dtype=np.float64)
        tidx = temp.argmax()

        dfnew = pd.DataFrame(columns=df.columns)
        dfnew[dfnew.columns[0]] = temp[:tidx]
        dfnew[dfnew.columns[1]] = Cp[:tidx]
        dfnew.to_csv(filename_output, index=False)
        return

    filename = filedialog.askopenfilename(initialdir="/",
                                        title="Select Input File",
                                        filetype=(("csv files", "*.csv"),("All Files", "*.*")))

    filename_output = filename.replace('.csv', '_sorted.csv')
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
    # Identify unique magnetic-field values
    # -----------------------------------------------------------------------------
    # Extract all unique magnetic-field values from the ``Magnetic Field (T)``
    # column and convert them to floating-point numbers.
    #
    # ``field_value`` contains the magnetic-field values used as separate field
    # steps in the output, while ``num_field_steps`` gives their total number.
    field_value = np.unique(np.array(dfall['Magnetic Field (T)'], dtype=np.float64))
    num_field_steps = field_value.size

    filename_fields = filename.replace('.csv', '_fields.csv')
    df_fields = pd.DataFrame(columns=['Magnetic Field (T)'])
    df_fields['Magnetic Field (T)'] = np.round(field_value , 2)
    df_fields.to_csv(filename_fields, index=False)

    # -----------------------------------------------------------------------------
    # Display processing information
    # -----------------------------------------------------------------------------
    print('input file name:  ', filename)
    print('output file name: ', filename_output)
    print('field file name: ', filename_fields)
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
        str2 = 'Magnetic Field (T) @ H='+str(np.round(field_value[index], decimals=2))+' T'
        str3 = 'Cp (J/Kg/K) @ H='+str(np.round(field_value[index], decimals=2))+' T'
        
        # Create a mapping from the original PPMS column names to the new
        # field-specific column names.
        dict = {'Sample Temp (Kelvin)': str1,
                'Magnetic Field (T)': str2,
                'Cp (J/Kg/K)': str3}
        
        # Rename the columns for the current magnetic-field step.
        dataframe_collection[index] = dataframe_collection_tmp[index].rename(columns=dict)
        
        # Replace the original DataFrame index with sequential numbers beginning
        # at 1. This makes each field-specific measurement series easier to read.
        dataframe_collection[index].index = np.arange(1, len(dataframe_collection[index]) + 1)
        
        # Keep only the temperature and mass-normalized moment columns. Magnetic
        # field columns and moment in emu are removed because the field is already
        # encoded in the column names and the desired output uses Am^2/kg.
        dataframe_collection[index] = dataframe_collection[index].drop([str2], axis=1)
        
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

def func(temp_base, Cp_base, temp_pulse, Cp_pulse, s_base, temp_min, temp_max, shift):

    rcParams['figure.figsize'] = 4, 4
    plt.plot(temp_base, Cp_base, label='base')
    plt.plot(temp_pulse, Cp_pulse+shift, label='pulse')
    plt.xlabel('T (K)')
    plt.ylabel('Cp (J/Kg/K)')
    plt.legend()
    plt.tight_layout()
    plt.show()    

    temp_min = simpledialog.askfloat("Input Min. Temp", "Input min. temp", initialvalue=temp_min)
    temp_max = simpledialog.askfloat("Input Max. Temp", "Input max. temp", initialvalue=temp_max)
    shift = simpledialog.askfloat("Input Cp Shift", "Input Cp shift", initialvalue=shift)

    idx_temp_base_min = np.abs(temp_base - temp_min).argmin()
    idx_temp_base_max = np.abs(temp_base - temp_max).argmin()
    idx_temp_pulse_min = np.abs(temp_pulse - temp_min).argmin()
    idx_temp_pulse_max = np.abs(temp_pulse - temp_max).argmin()
    
    temp_all = np.concatenate((temp_base[:idx_temp_base_min], temp_pulse[idx_temp_pulse_min:idx_temp_pulse_max+1], temp_base[idx_temp_base_max:]))
    Cp_all = np.concatenate((Cp_base[:idx_temp_base_min], Cp_pulse[idx_temp_pulse_min:idx_temp_pulse_max+1] + shift, Cp_base[idx_temp_base_max:]))
    
    temp_mid = np.zeros(temp_all.size+1, dtype=np.float64)
    temp_mid[1:-1] = (temp_all[:-1] + temp_all[1:]) / 2.0
    temp_mid[-1] = temp_all[-1]
    dT = temp_mid[1:] - temp_mid[:-1]
    s_all = (Cp_all * dT / temp_all).cumsum()

    f = interp1d(temp_all, Cp_all/temp_all, bounds_error=False, fill_value="extrapolate")
    x = np.linspace(temp_base.min(), temp_base.max(), 200)
    y = f(x)
    x_mid = np.zeros(x.size+1, dtype=np.float64)
    x_mid[1:-1] = (x[:-1] + x[1:]) / 2.0
    x_mid[-1] = x[-1]
    dx = x_mid[1:] - x_mid[:-1]
    s_int = (y * dx).cumsum()
    
    rcParams['figure.figsize'] = 8, 4

    plt.subplot(1, 2, 1)
    plt.plot(temp_base, Cp_base, label='base')
    plt.plot(temp_pulse[idx_temp_pulse_min:idx_temp_pulse_max+1], Cp_pulse[idx_temp_pulse_min:idx_temp_pulse_max+1] + shift, label='pulse+shift')
    plt.xlabel('T (K)')
    plt.ylabel('Cp (J/Kg/K)')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(temp_base, s_base, label='base')
    plt.plot(x, s_int, label='base+pulse+shift (int)')
    plt.xlabel('T (K)')
    plt.ylabel('s (J/Kg/K)')
    plt.legend()

    plt.tight_layout()
    plt.show()

    loop = simpledialog.askstring("Continue Loop", 
                                "Continue (yes/no):", 
                                initialvalue='yes')

    return shift, loop, temp_min, temp_max

def calculate_entropy_Cp():
    """Calculate entropy from formatted PPMS Cp data.

    Processing workflow
    -------------------
    1. Select the base ``*_sorted.csv`` file containing formatted Cp data.
    2. Select one or more pulse-data CSV files.
    3. Derive the corresponding ``*_fields.csv`` file from the base filename.
    4. Read the formatted Cp data and determine the available magnetic fields.
    5. For each magnetic field:
       - Read the temperature and Cp columns.
       - Optionally sort the data by temperature when ``multi_protocol`` is
         enabled.
       - For multi-protocol data, retain every ``skip``-th point.
       - Calculate entropy from the numerical integral of ``Cp / T``.
    6. Search the pulse files for matching pulse temperature/Cp columns.
    7. If pulse data are available, optionally adjust their temperature range
       and Cp offset interactively through ``func()``.
    8. Combine the base and pulse data over the selected temperature interval.
    9. Interpolate the combined Cp data onto a regular temperature grid.
    10. Calculate entropy for both the combined and base-only datasets.
    11. Store the processed columns for each magnetic field.
    12. Save the complete result as ``*_entropy.csv``.

    Input files
    -----------
    Base file:
        A formatted Cp CSV, normally ending in ``_sorted.csv``.

    Field file:
        The file obtained by replacing ``_sorted.csv`` with ``_fields.csv``.
        It contains the magnetic-field values to process.

    Pulse files:
        CSV files that may contain columns named
        ``Temperature (pulse) (K) @ H=... T`` and
        ``Cp (pulse) (J/Kg/K) @ H=... T``.

    Entropy calculation
    -------------------
    Base entropy is calculated with SciPy's ``cumulative_trapezoid`` using
    ``Cp / T`` as the integrand and temperature as the integration variable.

    When pulse data are available, the selected pulse interval is inserted
    between the corresponding base-data temperature limits after applying
    the user-selected Cp shift. The combined data are interpolated before
    the final entropy calculation.

    Output
    ------
    A CSV file ending in ``_entropy.csv`` containing temperature, Cp, and
    entropy data for each processed magnetic field. When pulse data are
    available, pulse and interpolated combined datasets are also included.

    """

    # Select the input CSV file.
    filename = filedialog.askopenfilename(initialdir="/",
                                        title="Select Base File",
                                        filetype=(("csv files", "*.csv"),("All Files", "*.*")))
    filename_pulses = filedialog.askopenfilenames(initialdir="/",
                                        title="Select Pulse Files",
                                        filetype=(("csv files", "*.csv"),("All Files", "*.*")))
    
    filename_fields = filename.replace('_sorted.csv', '_fields.csv')
    filename_output = filename.replace('_sorted.csv', '_entropy.csv')
    multi_protocol = simpledialog.askstring("Multi Protocol", 
                                "Contains multi protocol(yes/no):", 
                                initialvalue='yes')
    skip = 1
    if multi_protocol == 'yes':
        skip = 2

    # Read the PPMS data into a pandas DataFrame.
    df = pd.read_csv(filename)

    # Magnetic-field values to process, in tesla.
    df_fields = pd.read_csv(filename_fields)
    field_values = list(df_fields['Magnetic Field (T)'])
    field_values.sort()

    # Process each magnetic field independently to find global temperature minimum and maximum.
    temp_min = 1e6
    temp_max = 0
    for idx in range(len(field_values)):
        str1 = 'Temperature (K) @ H='+str(np.round(field_values[idx], decimals=2))+' T'
        temp = np.array(df[str1], dtype=np.float64)
        temp_min = min(temp_min, temp.min())
        temp_max = max(temp_max, temp.max())

    # -----------------------------------------------------------------------------
    # Display processing information
    # -----------------------------------------------------------------------------
    print('input file name:    ', filename)
    print('field file name:    ', filename_fields)
    print('output file name:   ', filename_output)
    print('fields:             ', field_values)    
    print('temp_base_min,    temp_base_max  = ', temp_min, temp_max)

    # Process each magnetic field independently.
    for idx in range(len(field_values)):
        
        str1 = 'Temperature (K) @ H='+str(np.round(field_values[idx], decimals=2))+' T'
        str2 = 'Cp (J/Kg/K) @ H='+str(np.round(field_values[idx], decimals=2))+' T'
        str3 = 'Entropy (J/Kg/K) @ H='+str(np.round(field_values[idx], decimals=2))+' T'
        str4 = 'Temperature (pulse) (K) @ H='+str(np.round(field_values[idx], decimals=2))+' T'
        str5 = 'Cp (pulse) (J/Kg/K) @ H='+str(np.round(field_values[idx], decimals=2))+' T'

        # Keep temperature and mass-normalized moment for this field.
        df_new = pd.DataFrame()

        temp = np.array(df[str1], dtype=np.float64)
        Cp = np.array(df[str2], dtype=np.float64)
        
        if multi_protocol == 'yes':
            sort_idx = temp.argsort()
            temp = temp[sort_idx]
            Cp = Cp[sort_idx]

            temp = temp[::skip]
            Cp = Cp[::skip]

        temp_mid = np.zeros(temp.size+1, dtype=np.float64)
        temp_mid[1:-1] = (temp[:-1] + temp[1:]) / 2.0
        temp_mid[-1] = temp[-1]
        dT = temp_mid[1:] - temp_mid[:-1]
        # entropy_with_base = (Cp * dT / temp).cumsum()
        entropy_with_base = cumulative_trapezoid(y=Cp / temp, x=temp, initial=0) + 0.5 * Cp[0]

        df_new[str1] = temp
        df_new[str2] = Cp
        df_new[str3] = entropy_with_base

        for filename_pulse in filename_pulses:
            dfp = pd.read_csv(filename_pulse)
            if str4 in dfp.columns:
                break

        if str4 in dfp.columns:

            temp_pulse = np.array(dfp[str4])
            Cp_pulse = np.array(dfp[str5])

            # loop = simpledialog.askstring("Continue Loop", 
            #                     "Continue pulse data modification loop (yes/no):", 
            #                     initialvalue='no')
            loop = 'no'
            temp_pulse_min = temp_pulse.min()
            temp_pulse_max = temp_pulse.max()
            shift = 0
            while loop == 'yes':
                shift, loop, temp_pulse_min, temp_pulse_max = func(temp, Cp, temp_pulse, Cp_pulse, entropy_with_base, temp_pulse_min, temp_pulse_max, shift)
                print('shift, temp_min, temp_max = ', shift, temp_pulse_min, temp_pulse_max)
            
            idx_temp_pulse_min = np.abs(temp_pulse - temp_pulse_min).argmin()
            idx_temp_pulse_max = np.abs(temp_pulse - temp_pulse_max).argmin()
            
            idx_temp_base_min = np.abs(temp - temp_pulse_min).argmin()
            idx_temp_base_max = np.abs(temp - temp_pulse_max).argmin()
            print('temp_pulse_start, temp_pulse_end = ', temp_pulse[idx_temp_pulse_min], temp_pulse[idx_temp_pulse_max])

            temp_all = np.concatenate((temp[:idx_temp_base_min], temp_pulse[idx_temp_pulse_min:idx_temp_pulse_max+1], temp[idx_temp_base_max:]))
            Cp_all = np.concatenate((Cp[:idx_temp_base_min], Cp_pulse[idx_temp_pulse_min:idx_temp_pulse_max+1] + shift, Cp[idx_temp_base_max:]))

            temp_int = np.linspace(temp.min(), temp.max(), 200)
            f = interp1d(temp_all, Cp_all/temp_all, bounds_error=False, fill_value="extrapolate")
            Cp_T_int = f(temp_int)
            f = interp1d(temp_all, Cp_all, bounds_error=False, fill_value="extrapolate")
            Cp_int = f(temp_int)

            entropy_with_pulse = cumulative_trapezoid(y=Cp_T_int, x=temp_int, initial=0) + 0.5 * temp_int[0] * Cp_T_int[0]

            f = interp1d(temp, Cp/temp, bounds_error=False, fill_value="extrapolate")
            Cp_T_int = f(temp_int)
            entropy_with_base_int = cumulative_trapezoid(y=Cp_T_int, x=temp_int, initial=0) + 0.5 * temp_int[0] * Cp_T_int[0]

            str7 = 'Temperature (all) (K) @ H='+str(np.round(field_values[idx], decimals=2))+' T'
            str8 = 'Cp (all) (J/Kg/K) @ H='+str(np.round(field_values[idx], decimals=2))+' T'
            str9 = 'Entropy (all) (J/Kg/K) @ H='+str(np.round(field_values[idx], decimals=2))+' T'
            str10= 'Entropy (base) (J/Kg/K) @ H='+str(np.round(field_values[idx], decimals=2))+' T'

            df_new = pd.concat([ df_new, dfp[[str4, str5]] ], axis=1)
            df_tmp = pd.DataFrame()
            df_tmp[str7] = pd.Series(temp_int)
            df_tmp[str8] = pd.Series(Cp_int)
            df_tmp[str9] = pd.Series(entropy_with_pulse)
            df_tmp[str10]= pd.Series(entropy_with_base_int)
            df_new = pd.concat([ df_new, df_tmp ], axis=1)

        # Combined the datasets for entropy.
        if idx == 0:
            dfnew_ent = df_new.copy()
        else:
            dfnew_ent = pd.concat([dfnew_ent, df_new], axis=1)

    # Save the entropy dataset.
    dfnew_ent.to_csv(filename_output, index=False)
