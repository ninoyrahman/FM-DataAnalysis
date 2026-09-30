# PPMS & SEM Data Processing Tools

A Python/Tkinter-based graphical interface for processing magnetic measurement data collected using **Physical Property Measurement System (PPMS)** and **Scattering Electron Measurement (SEM)**.

The project consists of following Python files:

* **`data_processing_class.py`** – Contains PPMS M–T processing functions.
* **`data_processing_class_MH.py`** – Contains PPMS M–H processing functions.
* **`data_processing_class_Cp.py`** – Contains PPMS Cp-s processing functions.
* **`area_calculation_class.py`** – Contains SEM image-processing functions.
* **`ppms_data_processing_gui.py`** – Provides a graphical Tkinter interface for running all processing functions.

The GUI imports functions from all processing modules, so the Python files should be kept in the same directory.

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

### Cp–s processing

7. **Convert PPMS `.dat` → CSV (Cp–s)**
8. **Format PPMS CSV (Cp–s)**
9. **Calculate entropy**

### SEM Image analysis
10. **Calculate areas from TIFF images**

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

## Running the application

Keep the Python files together:

```text
Data_Tools/
├── data_processing_class.py
├── data_processing_class_MH.py
├── data_processing_class_Cp.py
├── area_calculation_class.py
├── ppms_data_processing_gui.py
├── ppms_data_processing.spec
└── README.md
```


Run the application with:

```bash
python ppms_data_processing_gui.py
```

or run the generated executable from the `dist/` directory.

---