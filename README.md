# PPMS Data Processing Tools

A Python/Tkinter-based graphical interface for processing magnetic measurement data collected using a **Physical Property Measurement System (PPMS)**.

The project consists of three Python files:

* **`data_processing_class.py`** – Contains PPMS M–T processing functions and TIFF-image area calculation.
* **`data_processing_class_MH.py`** – Contains PPMS M–H processing functions.
* **`data_processing_class_Cp.py`** – Contains PPMS heat-capacity (Cp) and entropy-processing functions.
* **`ppms_data_processing_gui.py`** – Provides a graphical Tkinter interface for running all processing functions.

The GUI imports functions from all three processing modules, so the Python files should be kept in the same directory.

---

## Features

The application provides the following processing operations:

### M–T processing
1. **Convert PPMS `.dat` → CSV (M–T)**
2. **Format PPMS CSV (M–T)**
3. **Separate Cooling / Heating**

### M–H processing
4. **Convert PPMS `.dat` → CSV (M–H)**
5. **Format PPMS CSV (M–H)**
6. **Separate Magnetization / Demagnetization**

### Cp–S workflow

7. **Convert PPMS `.dat` → CSV (Cp–s)**
8. **Format PPMS CSV (Cp–s)**
9. **Calculate entropy from Cp**

### Image analysis
10. **Calculate Areas from TIFF Images**

The processing functions use Tkinter dialogs for selecting files and entering required parameters.

---

## Requirements

Python 3 is required.

Install the required Python packages with:

```bash
pip install pandas numpy opencv-python matplotlib scipy
```

### Tkinter

`tkinter` is included with most standard Python installations.

On Linux, if Tkinter is not installed, it may be necessary to install it separately. For example, on Debian/Ubuntu:

```bash
sudo apt install python3-tk
```

PyInstaller is required to build the application. Install it using pip:

```bash
pip install -U pyinstaller
```

Then build the executable with the provided spec file:

```bash
pyinstaller ppms_data_processing.spec
```

The built application will be created in the dist/ directory.

---

## File Structure

Keep the Python files together:

```text
PPMS_Data_Tools/
├── data_processing_class.py
├── data_processing_class_MH.py
├── data_processing_class_Cp.py
├── ppms_data_processing_gui.py
├── ppms_data_processing.spec
└── README.md
```

---

Run the application with:

```bash
python ppms_data_processing_gui.py
```

or run the generated executable from the `dist/` directory.

### M–T workflow

1. **Convert** – Convert PPMS `.dat` files to CSV.
2. **Format** – Format the combined M–T CSV by magnetic field.
3. **Separate** – Separate cooling and heating data.

### M–H workflow

1. **Convert** – Convert PPMS `.dat` files to CSV.
2. **Format** – Format the combined M–H CSV by temperature.
3. **Separate** – Separate magnetization and demagnetization data.

### Cp–S workflow

1. **Convert** – Convert PPMS heat-capacity `.dat` files to CSV.
2. **Format** – Format the combined Cp data by magnetic field.
3. **Calculate** – Calculate entropy.

### TIFF Analysis workflow

1. **Calculate Areas** – Calculate intensity-distribution areas from TIFF images.

---

# M–T and M–H Workflows

## M–T workflow

```text
Raw PPMS .dat files
        │
        ▼
┌────────────────────────────┐
│ Convert PPMS .dat → CSV    │
│       convert_dat_to_cvs() │
└────────────┬───────────────┘
             │
             ▼
      Combined M–T CSV
             │
             ▼
┌──────────────────────────────┐
│ Format PPMS CSV              │
│       ppms_data_formatting() │
└────────────┬─────────────────┘
             │
             ▼
       Wide-format M–T CSV
             │
             ▼
┌──────────────────────────────────┐
│ Separate Cooling / Heating       │
│ cooling_heating_seperation()     │
└──────────────┬───────────────────┘
               │
         ┌─────┴─────┐
         ▼           ▼
   Cooling CSV   Heating CSV
```

## M–H workflow

```text
Raw PPMS .dat files
        │
        ▼
┌────────────────────────────┐
│ Convert PPMS .dat → CSV    │
│    convert_dat_to_cvs_MH() │
└────────────┬───────────────┘
             │
             ▼
      Combined M–H CSV
             │
             ▼
┌────────────────────────────────┐
│ Format PPMS CSV                │
│    ppms_data_formatting_MH()   │
└────────────┬───────────────────┘
             │
             ▼
       Wide-format M–H CSV
             │
             ▼
┌──────────────────────────────────────────┐
│ Separate Magnetization / Demagnetization │
│ magnetization_demagnetization_seperation│
└──────────────────┬───────────────────────┘
                   │
             ┌─────┴─────┐
             ▼           ▼
    Magnetization CSV  Demagnetization CSV
```

The M–T and M–H workflows can be run independently when the input data are already in
the required format.

## Cp workflow

```text
Raw PPMS .dat
      │
      ▼
Convert Cp .dat → CSV
      │
      ▼
Combined Cp CSV
      │
      ▼
Format Cp CSV ─────► *_fields.csv
      │
      ▼
   *_sorted.csv
      │
      ▼
Calculate Entropy
      │
      ▼
  *_entropy.csv
```

The Cp–S workflow is independent of the M–T and M–H workflows.

---

# Version Information

The current project contains four main Python modules/files:

- `data_processing_class.py` — M–T processing and TIFF image analysis.
- `data_processing_class_MH.py` — M–H processing.
- `data_processing_class_Cp.py` — Cp processing and entropy calculation.
- `ppms_data_processing_gui.py` — workflow-oriented Tkinter GUI.

The GUI acts as a front end to the processing functions and does not duplicate their data-processing algorithms.

The M–T, M–H, and Cp processing functions are kept in separate modules so that the different measurement workflows can be maintained independently.
