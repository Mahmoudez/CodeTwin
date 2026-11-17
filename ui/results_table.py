"""Ranked similarity results table with sorting and score colors."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List

from core.models import PairResult


class ResultsTable(ttk.Frame):
    """Display and sort filtered suspicious pairs."""

    def __init__(self, parent: tk.Widget, on_open: Callable[[PairResult], None]) -> None:
        """Build the results Treeview and connect open actions."""
        super().__init__(parent)
        columns = ("student_a", "student_b", "score", "verdict")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        labels = {"student_a": "Student A", "student_b": "Student B", "score": "Score", "verdict": "Verdict"}
        self.sort_reverse = {}
        for column, label in labels.items():
            self.tree.heading(column, text=label, command=lambda key=column: self.sort_by(key))
            self.tree.column(column, width=155 if column != "verdict" else 185, anchor="w")
        self.tree.tag_configure("high", foreground="#c0392b")
        self.tree.tag_configure("medium", foreground="#d97706")
        self.tree.tag_configure("low", foreground="#21805b")
        self.tree.pack(fill="both", expand=True)
        self.results: List[PairResult] = []
        self.visible: List[PairResult] = []
        self.tree.bind("<Double-1>", lambda _event: self.open_selected(on_open))
        self.tree.bind("<Return>", lambda _event: self.open_selected(on_open))

    def set_results(self, results: List[PairResult], minimum: float = 0.0) -> None:
        """Replace rows and show results meeting the score threshold."""
        self.results = results
        self.visible = [pair for pair in results if pair.score >= minimum]
        self.tree.delete(*self.tree.get_children())
        for index, pair in enumerate(self.visible):
            tag = "high" if pair.score >= 0.85 else "medium" if pair.score >= 0.65 else "low"
            self.tree.insert("", "end", iid=str(index), values=(pair.submission_a.display_name, pair.submission_b.display_name, f"{pair.score:.0%}", pair.verdict), tags=(tag,))

    def sort_by(self, column: str) -> None:
        """Sort visible rows by the selected column."""
        reverse = self.sort_reverse.get(column, False)
        if column == "score":
            self.visible.sort(key=lambda pair: pair.score, reverse=not reverse)
        else:
            index = {"student_a": 0, "student_b": 1, "verdict": 2}[column]
            self.visible.sort(key=lambda pair: (pair.submission_a.display_name, pair.submission_b.display_name, pair.verdict)[index], reverse=not reverse)
        self.sort_reverse[column] = not reverse
        current = self.visible[:]
        self.set_results(current)

    def open_selected(self, callback: Callable[[PairResult], None]) -> None:
        """Open the currently selected pair, if any."""
        selection = self.tree.selection()
        if selection:
            callback(self.visible[int(selection[0])])
