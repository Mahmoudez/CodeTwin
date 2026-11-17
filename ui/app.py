"""Application window and background analysis orchestration."""

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from core.analyzer import Analyzer
from core.models import AnalysisReport, PairResult
from io_utils.exporter import export_csv, export_json
from ui.diff_viewer import DiffViewer
from ui.heatmap import Heatmap
from ui.results_table import ResultsTable
from ui.theme import configure_style
from ui.widgets import StatusBar, Toolbar


class CodeTwinApp:
    """Build and run the Code Twin desktop interface."""

    def __init__(self) -> None:
        """Initialize window state and connect user actions."""
        self.root = tk.Tk()
        self.root.title("Code Twin · Python submission analyzer")
        self.root.geometry("1050x700")
        self.dark = False
        self.colors = configure_style(self.root)
        self.folder: Path | None = None
        self.report: AnalysisReport | None = None
        self.events: queue.Queue = queue.Queue()
        self.threshold = tk.DoubleVar(value=0)
        self.toolbar = Toolbar(self.root, {"folder": self.choose_folder, "analyze": self.start_analysis, "csv": self.save_csv, "json": self.save_json, "theme": self.toggle_theme, "filter": self.filter_results}, self.threshold)
        self.toolbar.pack(fill="x")
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        results_frame = ttk.Frame(self.tabs, padding=8)
        self.table = ResultsTable(results_frame, self.open_pair)
        self.table.pack(fill="both", expand=True)
        self.tabs.add(results_frame, text="Ranked pairs")
        self.heatmap = Heatmap(self.tabs, self.open_pair)
        self.tabs.add(self.heatmap, text="Similarity heatmap")
        self.skipped = ttk.Treeview(self.tabs, columns=("file", "reason"), show="headings")
        self.skipped.heading("file", text="File")
        self.skipped.heading("reason", text="Reason")
        self.skipped.column("file", width=230)
        self.skipped.column("reason", width=700)
        self.tabs.add(self.skipped, text="Skipped files")
        self.status = StatusBar(self.root)
        self.status.pack(fill="x", side="bottom")
        self.root.bind("<Control-o>", lambda _event: self.choose_folder())
        self.root.bind("<Control-r>", lambda _event: self.start_analysis())
        self.root.bind("<Control-e>", lambda _event: self.save_csv())
        self.root.after(100, self._poll_events)

    def run(self) -> None:
        """Enter Tk's event loop."""
        self.root.mainloop()

    def choose_folder(self) -> None:
        """Ask the user to select a folder of student scripts."""
        selected = filedialog.askdirectory(title="Choose folder of Python submissions")
        if selected:
            self.folder = Path(selected)
            self.status.set_message(f"Selected {self.folder}")

    def start_analysis(self) -> None:
        """Start analysis on a worker thread without blocking Tk."""
        if self.folder is None:
            self.choose_folder()
        if self.folder is None:
            return
        self.status.progress.start(10)
        folder = self.folder
        def worker() -> None:
            try:
                report = Analyzer().run(folder, self.events.put)
                self.events.put(("complete", report))
            except Exception as error:  # Surface unexpected input/runtime errors safely.
                self.events.put(("error", str(error)))
        threading.Thread(target=worker, daemon=True).start()

    def _poll_events(self) -> None:
        """Transfer worker messages into widgets on Tk's main thread."""
        try:
            while True:
                event = self.events.get_nowait()
                if isinstance(event, tuple) and event[0] == "complete":
                    self._show_report(event[1])
                elif isinstance(event, tuple) and event[0] == "error":
                    self.status.progress.stop()
                    messagebox.showerror("Analysis failed", event[1])
                else:
                    self.status.set_message(str(event))
        except queue.Empty:
            pass
        self.root.after(100, self._poll_events)

    def _show_report(self, report: AnalysisReport) -> None:
        """Populate all report views and finish the progress display."""
        self.report = report
        self.status.progress.stop()
        self.filter_results()
        self.heatmap.set_results(report.pairs)
        self.skipped.delete(*self.skipped.get_children())
        for path, reason in report.skipped_files.items():
            self.skipped.insert("", "end", values=(path.name, reason))
        self.status.set_message(f"Analyzed {report.file_count} files · {len(report.pairs)} pairs · {len(report.skipped_files)} skipped · {report.elapsed_seconds:.2f}s")

    def filter_results(self, _value: str | None = None) -> None:
        """Apply the current percentage threshold to ranked pairs."""
        if self.report:
            self.table.set_results(self.report.pairs, self.threshold.get() / 100)

    def open_pair(self, pair: PairResult) -> None:
        """Open a detailed side-by-side view for one pair."""
        DiffViewer(self.root, pair)

    def save_csv(self) -> None:
        """Export the current report as CSV."""
        self._export("csv")

    def save_json(self) -> None:
        """Export the current report as JSON."""
        self._export("json")

    def _export(self, format_name: str) -> None:
        """Prompt for an export path and write the report."""
        if not self.report:
            messagebox.showinfo("No report", "Run an analysis before exporting.")
            return
        dialog = filedialog.asksaveasfilename(defaultextension=f".{format_name}", filetypes=[(format_name.upper(), f"*.{format_name}")])
        if not dialog:
            return
        try:
            (export_csv if format_name == "csv" else export_json)(self.report, Path(dialog))
            self.status.set_message(f"Exported {dialog}")
        except OSError as error:
            messagebox.showerror("Export failed", str(error))

    def toggle_theme(self) -> None:
        """Switch between the light and dark ttk palettes."""
        self.dark = not self.dark
        self.colors = configure_style(self.root, self.dark)
        self.heatmap.canvas.configure(background=self.colors["surface"])
