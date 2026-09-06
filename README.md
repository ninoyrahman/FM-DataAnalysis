# PPMS Data Processing Tools

Two Python scripts for processing PPMS measurement data:

- **`dat_to_cvs.py`** – Reads 1–3 raw `.dat` files, extracts data, converts units (Oe → T, emu → Am²/kg), and merges them into a single CSV.
- **`ppms_data_formatting.py`** – Restructures a combined CSV into wide format, placing moment values for different fields side‑by‑side with field‑specific column headers.

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

---

## Notes

- If you encounter encoding errors, change `encoding='cp1252'` to `'utf-8'` or `'latin1'` in the `read_csv` calls.  

---
