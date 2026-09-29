
import io
import tkinter as tk
import threading
from contextlib import redirect_stdout, redirect_stderr
from tkinter import messagebox, ttk

try:
    from data_processing_class import (
        convert_dat_to_cvs,
        ppms_data_formatting,
        cooling_heating_seperation,
        calculate_areas,
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
    IMPORT_ERROR = None
except Exception as exc:
    IMPORT_ERROR = exc


class PPMSDataProcessingGUI:
    """Compact workflow-oriented GUI for PPMS data processing."""

    def __init__(self, root):
        self.root = root
        self.root.title("PPMS Data Processing Tools")
        self.root.geometry("820x760")
        self.root.minsize(720, 620)

        self.workflows = {
            "M–T": {
                "title": "M–T PROCESSING",
                "steps": [
                    ("Convert", "Convert PPMS .dat files to CSV.", self.run_mt_convert),
                    ("Format", "Format the combined M–T CSV by magnetic field.", self.run_mt_format),
                    ("Separate", "Separate cooling and heating data.", self.run_mt_separate),
                ],
            },
            "M–H": {
                "title": "M–H PROCESSING",
                "steps": [
                    ("Convert", "Convert PPMS .dat files to CSV.", self.run_mh_convert),
                    ("Format", "Format the combined M–H CSV by temperature.", self.run_mh_format),
                    ("Separate", "Separate magnetization and demagnetization data.", self.run_mh_separate),
                ],
            },
            "Cp–S": {
                "title": "Cp–s PROCESSING",
                "steps": [
                    ("Convert", "Convert PPMS .dat files to CSV.", self.run_Cps_convert),
                    ("Format", "Format the combined Cp–s CSV by magnetic field.", self.run_Cps_format),
                    ("Calculate", "Calculate entropy.", self.run_calculate_entropy),
                ],
            },            
            "TIFF Analysis": {
                "title": "TIFF ANALYSIS",
                "steps": [
                    ("Calculate Areas", "Calculate intensity-distribution areas from TIFF images.", self.run_tiff),
                ],
            },
        }

        self.current_workflow = "M–T"
        self.current_step = 0
        self.running = False

        self.workflow_buttons = {}
        self.step_buttons = []
        self.output_text = None
        self.log_text = None
        self.progress = None
        self.status_var = tk.StringVar(value="Ready")
        self.step_title_var = tk.StringVar()
        self.step_description_var = tk.StringVar()

        self._build_style()
        self._build_gui()
        self._select_workflow("M–T")
        self._write_result("Ready. Select a workflow and processing step.")

    def _build_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Title.TLabel", font=("TkDefaultFont", 16, "bold"))
        style.configure("Workflow.TButton", font=("TkDefaultFont", 11, "bold"), padding=(18, 9))
        style.configure("ActiveWorkflow.TButton", font=("TkDefaultFont", 11, "bold"), padding=(18, 9))
        style.configure("Step.TButton", font=("TkDefaultFont", 10), padding=(15, 8))
        style.configure("ActiveStep.TButton", font=("TkDefaultFont", 10, "bold"), padding=(15, 8))
        style.configure("Run.TButton", font=("TkDefaultFont", 10, "bold"), padding=(18, 8))
        style.configure("Status.TLabel", font=("TkDefaultFont", 9))
        style.configure("Card.TFrame", relief="solid", borderwidth=1)

    def _build_gui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        header = ttk.Frame(self.root, padding=(18, 14, 18, 10))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="PPMS Data Processing Tools", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )

        workflow_bar = ttk.Frame(header)
        workflow_bar.grid(row=1, column=0, sticky="ew", pady=(12, 0))

        for column, name in enumerate(self.workflows):
            workflow_bar.columnconfigure(column, weight=1)
            button = ttk.Button(
                workflow_bar,
                text=name,
                style="Workflow.TButton",
                command=lambda workflow=name: self._select_workflow(workflow),
            )
            button.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 5, 5))
            self.workflow_buttons[name] = button

        separator = ttk.Separator(self.root, orient="horizontal")
        separator.grid(row=1, column=0, sticky="ew")

        main = ttk.Frame(self.root, padding=(18, 16, 18, 12))
        main.grid(row=2, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        workflow_panel = ttk.Frame(main)
        workflow_panel.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        workflow_panel.columnconfigure(0, weight=1)

        ttk.Label(workflow_panel, textvariable=self.step_title_var, font=("TkDefaultFont", 12, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(workflow_panel, textvariable=self.step_description_var, wraplength=760).grid(
            row=1, column=0, sticky="w", pady=(3, 10)
        )

        self.steps_frame = ttk.Frame(workflow_panel)
        self.steps_frame.grid(row=2, column=0, sticky="ew")

        controls = ttk.Frame(workflow_panel)
        controls.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        controls.columnconfigure(0, weight=1)

        self.run_button = ttk.Button(controls, text="Run", style="Run.TButton", command=self._run_current_step)
        self.run_button.grid(row=0, column=1, padx=(8, 0))

        self.previous_button = ttk.Button(controls, text="Previous", command=self._previous_step)
        self.previous_button.grid(row=0, column=2, padx=(8, 0))

        self.next_button = ttk.Button(controls, text="Next", command=self._next_step)
        self.next_button.grid(row=0, column=3, padx=(8, 0))

        results_frame = ttk.Frame(main, style="Card.TFrame", padding=8)
        results_frame.grid(row=1, column=0, sticky="nsew")
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        notebook = ttk.Notebook(results_frame)
        notebook.grid(row=0, column=0, sticky="nsew")

        result_tab = ttk.Frame(notebook, padding=8)
        result_tab.columnconfigure(0, weight=1)
        result_tab.rowconfigure(0, weight=1)
        notebook.add(result_tab, text="Results")

        self.output_text = tk.Text(result_tab, wrap="word", height=10, state="disabled")
        output_scroll = ttk.Scrollbar(result_tab, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=output_scroll.set)
        self.output_text.grid(row=0, column=0, sticky="nsew")
        output_scroll.grid(row=0, column=1, sticky="ns")

        log_tab = ttk.Frame(notebook, padding=8)
        log_tab.columnconfigure(0, weight=1)
        log_tab.rowconfigure(0, weight=1)
        notebook.add(log_tab, text="Processing Log")

        self.log_text = tk.Text(log_tab, wrap="word", height=10, state="disabled")
        log_scroll = ttk.Scrollbar(log_tab, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll.grid(row=0, column=1, sticky="ns")

        clear_button = ttk.Button(results_frame, text="Clear Output", command=self._clear_output)
        clear_button.grid(row=1, column=0, sticky="e", pady=(8, 0))

        status_bar = ttk.Frame(self.root, padding=(18, 8, 18, 12))
        status_bar.grid(row=3, column=0, sticky="ew")
        status_bar.columnconfigure(0, weight=1)

        ttk.Label(status_bar, textvariable=self.status_var, style="Status.TLabel").grid(
            row=0, column=0, sticky="w"
        )

        self.progress = ttk.Progressbar(status_bar, mode="indeterminate", length=140)
        self.progress.grid(row=0, column=1, padx=12)

        ttk.Button(status_bar, text="Exit", command=self.root.destroy).grid(row=0, column=2, sticky="e")

    def _select_workflow(self, workflow):
        if self.running:
            return

        self.current_workflow = workflow
        self.current_step = 0

        for name, button in self.workflow_buttons.items():
            button.configure(style="ActiveWorkflow.TButton" if name == workflow else "Workflow.TButton")

        self._rebuild_steps()
        self._update_step_display()

    def _rebuild_steps(self):
        for widget in self.steps_frame.winfo_children():
            widget.destroy()

        self.step_buttons = []
        steps = self.workflows[self.current_workflow]["steps"]

        for index, (name, _, _) in enumerate(steps):
            button = ttk.Button(
                self.steps_frame,
                text=("\u2713 " if index == self.current_step else "\u274C ") + name, # \u25CF (black circle), \u2713 (tick), \u274C (cross), \u26D2 (cross circle)
                style="ActiveStep.TButton" if index == self.current_step else "Step.TButton",
                command=lambda step=index: self._select_step(step),
            )
            button.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 5, 5))
            self.steps_frame.columnconfigure(index, weight=1)
            self.step_buttons.append(button)

    def _select_step(self, step):
        if self.running:
            return
        self.current_step = step
        self._update_step_display()

    def _update_step_display(self):
        workflow = self.workflows[self.current_workflow]
        name, description, _ = workflow["steps"][self.current_step]

        self.step_title_var.set(workflow["title"])
        self.step_description_var.set(f"{name}: {description}")

        for index, button in enumerate(self.step_buttons):
            step_name = workflow["steps"][index][0]
            button.configure(
                text=("\u2713 " if index == self.current_step else "\u274C ") + step_name,
                style="ActiveStep.TButton" if index == self.current_step else "Step.TButton",
            )

        self.previous_button.configure(state="normal" if self.current_step > 0 else "disabled")
        self.next_button.configure(
            state="normal" if self.current_step < len(workflow["steps"]) - 1 else "disabled"
        )

    def _previous_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self._update_step_display()

    def _next_step(self):
        if self.current_step < len(self.workflows[self.current_workflow]["steps"]) - 1:
            self.current_step += 1
            self._update_step_display()

    def _run_current_step(self):
        if self.running:
            return

        function = self.workflows[self.current_workflow]["steps"][self.current_step][2]
        self._run_function(function)

    def _run_function(self, function):
        self.running = True
        self.run_button.configure(state="disabled")
        self.previous_button.configure(state="disabled")
        self.next_button.configure(state="disabled")
        self.status_var.set("Processing...")
        self.progress.start(10)

        def worker():
            import contextlib
            import io
            import traceback

            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            error = None

            try:
                with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                    function()
            except Exception:
                error = traceback.format_exc()

            stdout = stdout_buffer.getvalue()
            stderr = stderr_buffer.getvalue()

            self.root.after(0, lambda: self._finish_function(function.__name__, stdout, stderr, error))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_function(self, function_name, stdout, stderr, error):
        self.running = False
        self.progress.stop()
        self.run_button.configure(state="normal")
        self._update_step_display()

        if stdout.strip():
            self._write_result(stdout.strip())
            self._write_log(stdout.strip())

        if stderr.strip():
            self._write_log(stderr.strip())

        if error:
            self.status_var.set("Processing failed")
            self._write_result(f"Processing failed.\n\n{error}")
            self._write_log(error)
            messagebox.showerror("Processing Error", error)
        else:
            self.status_var.set("Ready")
            self._write_result("Processing completed successfully.")

        self._write_log(f"Finished: {function_name}")

    def _write_result(self, message):
        if self.output_text is None:
            return
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def _write_log(self, message):
        if self.log_text is None:
            return
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_output(self):
        self._write_result("")
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self.status_var.set("Ready")

    def run_mt_convert(self):
        convert_dat_to_cvs()

    def run_mt_format(self):
        ppms_data_formatting()

    def run_mt_separate(self):
        cooling_heating_seperation()

    def run_mh_convert(self):
        convert_dat_to_cvs_MH()

    def run_mh_format(self):
        ppms_data_formatting_MH()

    def run_mh_separate(self):
        magnetization_demagnetization_seperation()
        
    def run_Cps_convert(self):
        convert_dat_to_cvs_Cp()

    def run_Cps_format(self):
        ppms_data_formatting_Cp()

    def run_calculate_entropy(self):
        calculate_entropy_Cp()

    def run_tiff(self):
        calculate_areas()


def main():
    root = tk.Tk()
    app = PPMSDataProcessingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
