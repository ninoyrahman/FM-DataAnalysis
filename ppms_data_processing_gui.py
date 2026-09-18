"""
PPMS Data Processing GUI
========================

Tkinter interface for the three processing functions in
data_processing_class.py:

    1. convert_dat_to_cvs()
    2. ppms_data_formatting()
    3. cooling_heating_seperation()
    4. calculate_areas()

Keep this GUI and data_processing_class.py in the same folder.
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
        self.geometry("780x720")
        self.minsize(700, 540)

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
            text="PPMS Data Processing Tools",
            style="Title.TLabel",
        ).pack(anchor="w")

        ttk.Label(
            header,
            text=(
                "Run the three PPMS data-processing functions from "
                "data_processing_class.py."
            ),
        ).pack(anchor="w", pady=(6, 0))

        # Processing buttons ------------------------------------------------
        tools = ttk.LabelFrame(
            self,
            text="Processing Functions",
            padding=18,
        )
        tools.pack(fill="x", padx=24, pady=12)

        self.convert_button = self._add_tool(
            tools,
            "1. Convert PPMS .dat → CSV",
            "Convert raw PPMS .dat files into a combined CSV.",
            self.run_convert,
        )

        self.format_button = self._add_tool(
            tools,
            "2. Format PPMS CSV",
            "Restructure the combined CSV into field-by-field wide format.",
            self.run_format,
        )

        self.cooling_button = self._add_tool(
            tools,
            "3. Separate Cooling / Heating",
            "Separate temperature-dependent data into cooling and heating datasets.",
            self.run_cooling_heating,
        )

        self.calculate_areas_button = self._add_tool(
                    tools,
                    "4. Calculate Areas",
                    "Calculate areas from tiff images.",
                    self.run_calculate_areas,
        )

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

    @staticmethod
    def _add_tool(parent, title, description, command):
        """Add a processing button and its description."""
        button = ttk.Button(
            parent,
            text=title,
            style="Tool.TButton",
            command=command,
        )
        button.pack(fill="x", pady=4)

        ttk.Label(
            parent,
            text=description,
            wraplength=680,
        ).pack(anchor="w", padx=12, pady=(0, 10))

        return button

    def _show_import_error(self):
        """Report an error if data_processing_class.py cannot be imported."""
        self._set_buttons("disabled")
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

    def _set_buttons(self, state):
        """Set the state of all processing buttons."""
        self.convert_button.configure(state=state)
        self.format_button.configure(state=state)
        self.cooling_button.configure(state=state)
        self.calculate_areas_button.configure(state=state)

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

        self._set_buttons("disabled")
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

        finally:
            self._set_buttons("normal")

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
