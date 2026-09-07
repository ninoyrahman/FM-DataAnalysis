# PPMS Data Processing Tools

Two Python scripts for processing PPMS measurement data:

- **`dat_to_cvs.py`** – Reads 1–3 raw `.dat` files, extracts data, converts units (Oe → T, emu → Am²/kg), and merges them into a single CSV.
- **`ppms_data_formatting.py`** – Restructures a combined CSV into wide format, placing moment values for different fields side‑by‑side with field‑specific column headers.
- **`cooling_heating_seperation.py`** – Separates temperature-dependent measurements into cooling and heating datasets for selected magnetic fields, with optional temperature sorting.

---

## Requirements

```bash
pip install pandas numpy
```

---

## Quick Start

### 1. Combine raw files (`dat_to_cvs.py`)

- By default, runs in **debug mode** with hard‑coded example files.  
- To use your own data, set `debug=False` in the `concat_files()` call (inside the script) to enable interactive prompts.

**Interactive input:**  
- PPMS device number (1 or 2)  
- Number of files (1–3)  
- File paths, output CSV name, and sample mass (mg) for each file.

Output: a CSV with added `Magnetic Field (T)` and `Moment (Am²/kg)` columns.

### 2. Reshape to wide format (`ppms_data_formatting.py`)

```bash
python ppms_data_formatting.py
```

Enter the input CSV (from step 1) and desired output CSV name.  
The script:
- Splits data by unique field values.
- Renames columns to include the field (e.g., `Temperature (K) @ H=0.02 T`).
- Drops magnetic field and moment‑in‑emu columns.
- Concatenates horizontally into a wide table.

Output: a CSV with columns ordered by field.

### 3. Separate cooling and heating data (cooling_heating_seperation.py)

```bash
python cooling_heating_seperation.py
```

Select the input CSV using the file-selection dialog.

The script:

- Processes measurements at 0.02, 2, 5, and 10 T.
- Separates each field's data into cooling and heating segments at the minimum-temperature point.
- Optionally sorts the cooling data from high to low temperature and the heating data from low to high temperature.
- Combines the field-specific cooling and heating datasets side-by-side.

Output: two CSV files with _cooling.csv and _heating.csv appended to the input filename.

---

## Notes

- If you encounter encoding errors, change `encoding='cp1252'` to `'utf-8'` or `'latin1'` in the `read_csv` calls.  

---
