"""Side-by-side source viewer with matching line highlights."""

import tkinter as tk
from tkinter import ttk

from core.models import PairResult


class DiffViewer(tk.Toplevel):
    """Show both submission sources, score details, and reasons."""

    def __init__(self, parent: tk.Widget, pair: PairResult) -> None:
        """Create a pair inspector window with synchronized scrolling."""
        super().__init__(parent)
        self.title(f"{pair.submission_a.display_name} ↔ {pair.submission_b.display_name}")
        self.geometry("1100x700")
        panes = ttk.Frame(self, padding=10)
        panes.pack(fill="both", expand=True)
        self.texts = []
        for submission, ranges in ((pair.submission_a, pair.matching_ranges[0]), (pair.submission_b, pair.matching_ranges[1])):
            panel = ttk.Frame(panes)
            panel.pack(side="left", fill="both", expand=True, padx=5)
            ttk.Label(panel, text=submission.display_name).pack(anchor="w")
            text = tk.Text(panel, wrap="none", font=("TkFixedFont", 10), undo=False)
            scroll = ttk.Scrollbar(panel, orient="vertical", command=text.yview)
            text.configure(yscrollcommand=scroll.set)
            text.pack(side="left", fill="both", expand=True)
            scroll.pack(side="right", fill="y")
            numbered_source = "\n".join(f"{number:4}  {line}" for number, line in enumerate(submission.source.splitlines(), start=1))
            text.insert("1.0", numbered_source)
            text.configure(state="disabled")
            text.tag_configure("match", background="#ffe8a3")
            for start, end in ranges:
                text.tag_add("match", f"{start}.0", f"{end + 1}.0")
            self.texts.append(text)
        self.texts[0].configure(yscrollcommand=lambda first, last: self._sync_scroll(0, first, last))
        self.texts[1].configure(yscrollcommand=lambda first, last: self._sync_scroll(1, first, last))
        details = ttk.Frame(self, padding=(14, 8))
        details.pack(fill="x")
        ttk.Label(details, text=f"Score {pair.score:.1%} · Sequence {pair.sequence_score:.1%} · Subtrees {pair.subtree_score:.1%} · Control flow {pair.control_score:.1%}", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Label(details, text="Reasons: " + " · ".join(pair.reasons), wraplength=1000).pack(anchor="w", pady=(5, 0))

    def _sync_scroll(self, source_index: int, first: str, last: str) -> None:
        """Update both panes' scrollbars and keep their positions aligned."""
        other_index = 1 - source_index
        self.texts[other_index].yview_moveto(first)
