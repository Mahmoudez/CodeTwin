"""Canvas heatmap of pairwise similarity scores."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional

from core.models import PairResult

CELL_SIZE = 42
LABEL_WIDTH = 130


class Heatmap(ttk.Frame):
    """Render an NxN similarity matrix with hover and click behavior."""

    def __init__(self, parent: tk.Widget, on_open: Callable[[PairResult], None]) -> None:
        """Create a scrollable canvas heatmap."""
        super().__init__(parent)
        self.canvas = tk.Canvas(self, background="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.on_open = on_open
        self.pairs: List[PairResult] = []
        self.names: List[str] = []
        self.matrix = {}
        self.canvas.bind("<Motion>", self._hover)
        self.canvas.bind("<Button-1>", self._click)
        self.tooltip: Optional[int] = None

    def set_results(self, pairs: List[PairResult]) -> None:
        """Draw a matrix using all students appearing in pair results."""
        self.pairs = pairs
        self.names = sorted({pair.submission_a.display_name for pair in pairs} | {pair.submission_b.display_name for pair in pairs})
        self.matrix = {}
        for pair in pairs:
            key = (pair.submission_a.display_name, pair.submission_b.display_name)
            self.matrix[key] = pair
            self.matrix[key[::-1]] = pair
        self.canvas.delete("all")
        width = LABEL_WIDTH + len(self.names) * CELL_SIZE
        height = LABEL_WIDTH + len(self.names) * CELL_SIZE
        self.canvas.configure(scrollregion=(0, 0, width, height))
        for index, name in enumerate(self.names):
            y = LABEL_WIDTH + index * CELL_SIZE
            self.canvas.create_text(LABEL_WIDTH - 8, y + CELL_SIZE / 2, text=name, anchor="e")
            self.canvas.create_text(LABEL_WIDTH + index * CELL_SIZE + CELL_SIZE / 2, LABEL_WIDTH - 8, text=name, angle=45)
            for column, other in enumerate(self.names):
                x = LABEL_WIDTH + column * CELL_SIZE
                pair = self.matrix.get((name, other))
                score = 1.0 if name == other else pair.score if pair else 0.0
                red = int(242 - 150 * score)
                green = int(245 - 115 * score)
                color = f"#{red:02x}{green:02x}90"
                self.canvas.create_rectangle(x, y, x + CELL_SIZE, y + CELL_SIZE, fill=color, outline="white", tags=(f"cell:{index}:{column}",))
                if pair:
                    self.canvas.create_text(x + CELL_SIZE / 2, y + CELL_SIZE / 2, text=f"{score:.0%}", font=("Segoe UI", 8))

    def _pair_at(self, event: tk.Event) -> Optional[PairResult]:
        """Find the pair under a pointer event, if inside a cell."""
        x = self.canvas.canvasx(event.x) - LABEL_WIDTH
        y = self.canvas.canvasy(event.y) - LABEL_WIDTH
        column, row = int(x // CELL_SIZE), int(y // CELL_SIZE)
        if x < 0 or y < 0 or row >= len(self.names) or column >= len(self.names):
            return None
        return self.matrix.get((self.names[row], self.names[column]))

    def _hover(self, event: tk.Event) -> None:
        """Show a compact pair and score tooltip while hovering over a cell."""
        pair = self._pair_at(event)
        if self.tooltip:
            self.canvas.delete(self.tooltip)
            self.tooltip = None
        if pair:
            self.tooltip = self.canvas.create_text(self.canvas.canvasx(event.x) + 12, self.canvas.canvasy(event.y) + 12, text=f"{pair.submission_a.display_name} / {pair.submission_b.display_name}: {pair.score:.1%}", anchor="nw", fill="#172033")

    def _click(self, event: tk.Event) -> None:
        """Open the selected pair from the matrix."""
        pair = self._pair_at(event)
        if pair:
            self.on_open(pair)
