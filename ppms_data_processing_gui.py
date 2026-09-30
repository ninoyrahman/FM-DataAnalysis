"""
PPMS Data Processing GUI
========================

Tkinter interface for the three processing functions in
data_processing_class.py, data_processing_class_MH.py, data_processing_class_Cp.py, area_calculation_class.py:

    1. convert_dat_to_cvs()
    2. ppms_data_formatting()
    3. cooling_heating_seperation()
    4. convert_dat_to_cvs_MH()
    5. ppms_data_formatting_MH()
    6. magnetization_demagnetization_seperation()
    7. convert_dat_to_cvs_Cp()
    8. ppms_data_formatting_Cp()
    9. calculate_entropy_Cp()
    10. calculate_areas()

"""

import io
import tkinter as tk
from contextlib import redirect_stdout, redirect_stderr
from tkinter import messagebox, ttk

try:
    from data_processing_class import (
        convert_dat_to_cvs,
        ppms_data_formatting,
        cooling_heating_seperation,
    )
    from data_processing_class_MH import (
            convert_dat_to_cvs_MH,
            ppms_data_formatting_MH,
            magnetization_demagnetization_seperation,
        )
    from data_processing_class_Cp import (
        convert_dat_to_cvs_Cp,
        ppms_data_formatting_Cp,
        calculate_entropy_Cp,
        )
    from area_calculation_class import (
            calculate_areas,
        )
    IMPORT_ERROR = None
except Exception as exc:
    IMPORT_ERROR = exc


class PPMSDataProcessingGUI(tk.Tk):
    """Main application window for the PPMS processing functions."""

    def __init__(self):
        super().__init__()

        self.title("PPMS Data Processing Tools")
        self.geometry("920x820")
        self.minsize(920, 540)

        self._configure_style()
        self._build_gui()

        if IMPORT_ERROR is not None:
            self._show_import_error()

    def _configure_style(self):
        """Configure the appearance of the application."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Title.TLabel",
            font=("TkDefaultFont", 20, "bold"),
        )
        style.configure(
            "Tool.TButton",
            font=("TkDefaultFont", 11, "bold"),
        )

    def _build_gui(self):
        """Create all widgets in the main window."""

        # Header ------------------------------------------------------------
        header = ttk.Frame(self, padding=(24, 20, 24, 10))
        header.pack(fill="x")

        ttk.Label(
            header,
            text="PPMS & SEM Data Processing Tools",
            style="Title.TLabel",
        ).pack(anchor="w")

        # Processing buttons ------------------------------------------------
        tools = ttk.LabelFrame(
            self,
            text="Processing Functions",
            padding=18,
        )
        tools.pack(fill="x", padx=24, pady=12)

        self.func_names = ['Convert .dat → CSV (M-T)', 'Format CSV (M-T)', 'Separate Cooling/Heating',
                      'Convert .dat → CSV (M-H)', 'Format CSV (M-H)', 'Separate Magnetization/Demagnetization',
                      'Convert .dat → CSV (Cp-s)', 'Format CSV (Cp-s)', 'Calculate Entropy',
                      'Calculate Areas']

        self.current_var = tk.StringVar()
        combobox = ttk.Combobox(tools, values=self.func_names, textvariable=self.current_var, width=40)
        combobox.set('Convert .dat → CSV (M-T)')
        combobox.grid(row=0, column=1, padx=(5, 5), pady=(5, 5))

        button = ttk.Button(tools, text="Run", command=lambda: self._run(), width=20)
        button.grid(row=0, column=3, padx=(5, 5), pady=(5, 5))

        # Status ------------------------------------------------------------
        status = ttk.Frame(self, padding=(24, 2))
        status.pack(fill="x")

        ttk.Label(status, text="Status:").pack(side="left")

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status, textvariable=self.status_var).pack(
            side="left", padx=6
        )

        # Output console ----------------------------------------------------
        output_frame = ttk.LabelFrame(
            self,
            text="Processing Output",
            padding=10,
        )
        output_frame.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=(8, 20),
        )

        console = ttk.Frame(output_frame)
        console.pack(fill="both", expand=True)

        self.output = tk.Text(
            console,
            wrap="word",
            state="disabled",
            font=("Consolas", 9),
        )
        self.output.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            console,
            orient="vertical",
            command=self.output.yview,
        )
        scrollbar.pack(side="right", fill="y")
        self.output.configure(yscrollcommand=scrollbar.set)

        ttk.Button(
            output_frame,
            text="Clear Output",
            command=self.clear_output,
        ).pack(anchor="e", pady=(8, 0))

    def _show_import_error(self):
        """Report an error if data_processing_class.py cannot be imported."""
        self.status_var.set("Import error")

        self.write_output(
            "ERROR: data_processing_class.py could not be imported."
            f"{IMPORT_ERROR}"
            "Make sure both Python files are in the same folder."
        )

        messagebox.showerror(
            "Import Error",
            f"Could not import data_processing_class.py.{IMPORT_ERROR}",
        )

    def write_output(self, text):
        """Append text to the output console."""
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="disabled")

    def clear_output(self):
        """Clear the output console."""
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")
        self.status_var.set("Ready")

    def _run_function(self, function, function_name):
        """Run a selected processing function and capture its print output."""
        if IMPORT_ERROR is not None:
            return

        self.status_var.set(f"Running {function_name}...")

        self.write_output(
            f"\n{'=' * 72}\n"
            f"Starting {function_name}\n"
            f"{'=' * 72}\n"
        )
        self.update_idletasks()

        captured = io.StringIO()

        try:
            # The supplied functions already provide their own Tkinter
            # dialogs for file selection and user input.
            with redirect_stdout(captured), redirect_stderr(captured):
                function()

            output = captured.getvalue()
            if output:
                self.write_output(output)

            self.write_output(
                f"\n{function_name} completed successfully.\n"
            )
            self.status_var.set("Ready")

        except Exception as exc:
            output = captured.getvalue()
            if output:
                self.write_output(output)

            self.write_output(
                f"\nERROR while running {function_name}:\n{exc}\n"
            )
            self.status_var.set("Error")

            messagebox.showerror(
                "Processing Error",
                f"{function_name} failed.\n\n{exc}",
            )

    def _run(self):
        """Run function based on selection from dropdown menu."""
        try:
            current_var = self.current_var.get()
            if current_var == self.func_names[0]:
                self.run_convert()
            elif current_var == self.func_names[1]:
                self.run_format()
            elif current_var == self.func_names[2]:
                self.run_cooling_heating()
            elif current_var == self.func_names[3]:
                self.run_convert_MH()
            elif current_var == self.func_names[4]:
                self.run_format_MH()
            elif current_var == self.func_names[5]:
                self.run_mag_dem()
            elif current_var == self.func_names[6]:
                self.run_convert_Cp()
            elif current_var == self.func_names[7]:
                self.run_format_Cp()
            elif current_var == self.func_names[8]:
                self.run_calculate_entropy()
            elif current_var == self.func_names[9]:
                self.run_calculate_areas()
        
        except:
            tk.messagebox.showerror("Information", "File not selected")
            return None
        return None        

    def run_convert(self):
        """Run the raw .dat to CSV conversion function."""
        self._run_function(
            convert_dat_to_cvs,
            "convert_dat_to_cvs()",
        )

    def run_format(self):
        """Run the PPMS CSV formatting function."""
        self._run_function(
            ppms_data_formatting,
            "ppms_data_formatting()",
        )

    def run_cooling_heating(self):
        """Run the cooling/heating separation function."""
        self._run_function(
            cooling_heating_seperation,
            "cooling_heating_seperation()",
        )

    def run_convert_MH(self):
        """Run the raw .dat to CSV conversion function (M-H)."""
        self._run_function(
            convert_dat_to_cvs_MH,
            "convert_dat_to_cvs_MH()",
        )

    def run_format_MH(self):
        """Run the PPMS CSV formatting function (M-H)."""
        self._run_function(
            ppms_data_formatting_MH,
            "ppms_data_formatting_MH()",
        )

    def run_mag_dem(self):
        """Run the magnetization/demagnetization separation function."""
        self._run_function(
            magnetization_demagnetization_seperation,
            "magnetization_demagnetization_seperation()",
        )

    def run_convert_Cp(self):
        """Run the raw .dat to CSV conversion function (Cp-s)."""
        self._run_function(
            convert_dat_to_cvs_Cp,
            "convert_dat_to_cvs_Cp()",
        )

    def run_format_Cp(self):
        """Run the PPMS CSV formatting function (Cp-s)."""
        self._run_function(
            ppms_data_formatting_Cp,
            "ppms_data_formatting_Cp()",
        )

    def run_calculate_entropy(self):
        """Run the calculate areas function."""
        self._run_function(
            calculate_entropy_Cp,
            "calculate_entropy_Cp()",
        )

    def run_calculate_areas(self):
            """Run the calculate areas function."""
            self._run_function(
                calculate_areas,
                "calculate_areas()",
            )


def main():
    """Start the PPMS Data Processing GUI."""
    app = PPMSDataProcessingGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
