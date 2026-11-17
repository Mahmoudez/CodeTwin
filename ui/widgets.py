"""Reusable toolbar and status widgets."""

import tkinter as tk
from tkinter import ttk
from typing import Callable


class Toolbar(ttk.Frame):
    """Toolbar with folder, analysis, export, and theme controls."""

    def __init__(self, parent: tk.Widget, callbacks: dict, threshold: tk.DoubleVar) -> None:
        """Create toolbar controls and a live threshold slider."""
        super().__init__(parent, padding=(14, 10))
        for label, callback in (("Choose Folder", callbacks["folder"]), ("Analyze", callbacks["analyze"]), ("Export CSV", callbacks["csv"]), ("Export JSON", callbacks["json"]), ("Toggle Theme", callbacks["theme"])):
            ttk.Button(self, text=label, command=callback).pack(side="left", padx=(0, 7))
        ttk.Label(self, text="Minimum score").pack(side="left", padx=(18, 7))
        ttk.Scale(self, from_=0, to=100, variable=threshold, orient="horizontal", length=150, command=callbacks["filter"]).pack(side="left")


class StatusBar(ttk.Frame):
    """Status message and determinate/indeterminate progress indicator."""

    def __init__(self, parent: tk.Widget) -> None:
        """Create status label and progress bar."""
        super().__init__(parent, padding=(12, 7))
        self.message = tk.StringVar(value="Choose a folder containing student .py files")
        ttk.Label(self, textvariable=self.message).pack(side="left", fill="x", expand=True)
        self.progress = ttk.Progressbar(self, mode="indeterminate", length=170)
        self.progress.pack(side="right")

    def set_message(self, message: str) -> None:
        """Update the visible status text."""
        self.message.set(message)
