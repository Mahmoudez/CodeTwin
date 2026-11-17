"""Color palettes and ttk styling for the Code Twin application."""

import tkinter as tk
from tkinter import ttk

LIGHT = {"background": "#f4f6fa", "surface": "#ffffff", "foreground": "#172033", "muted": "#667085", "accent": "#315efb", "border": "#d9deea"}
DARK = {"background": "#171b24", "surface": "#222936", "foreground": "#edf1f7", "muted": "#a5afc0", "accent": "#7c9aff", "border": "#394354"}
FONT_FAMILY = "Segoe UI"


def configure_style(root: tk.Tk, dark: bool = False) -> dict:
    """Apply the selected palette and return its color mapping."""
    colors = DARK if dark else LIGHT
    root.configure(background=colors["background"])
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", font=(FONT_FAMILY, 10), background=colors["background"], foreground=colors["foreground"])
    style.configure("TFrame", background=colors["background"])
    style.configure("Surface.TFrame", background=colors["surface"])
    style.configure("TLabel", background=colors["background"], foreground=colors["foreground"])
    style.configure("Surface.TLabel", background=colors["surface"], foreground=colors["foreground"])
    style.configure("TButton", padding=(11, 7))
    style.configure("Treeview", rowheight=29, background=colors["surface"], fieldbackground=colors["surface"], foreground=colors["foreground"])
    style.configure("Treeview.Heading", padding=8, font=(FONT_FAMILY, 9, "bold"))
    style.map("Treeview", background=[("selected", colors["accent"])], foreground=[("selected", "white")])
    return colors
