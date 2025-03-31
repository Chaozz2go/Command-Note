import os
import json
import logging
import tkinter as tk

# Globale Theme-Variable
theme = {}

def load_theme(app):
    """
    Lädt das Theme basierend auf app.current_theme und aktualisiert die globale theme-Variable.
    """
    global theme
    theme_name = app.current_theme

    # Absoluter Pfad zum Theme-Verzeichnis
    base_dir = os.path.dirname(os.path.abspath(__file__))
    theme_file = os.path.join(base_dir, "..", "themes", f"{theme_name}.json")

    try:
        with open(theme_file, "r", encoding="utf-8") as f:
            theme = json.load(f)
    except Exception as e:
        logging.exception(f"Fehler beim Laden des Themes '{theme_name}' aus {theme_file}")
        theme = {
            "bg": "white",
            "fg": "black",
            "button_bg": "#f0f0f0",
            "button_fg": "#000000",
            "entry_bg": "#ffffff",
            "entry_fg": "#000000",
            "listbox_bg": "#ffffff",
            "listbox_fg": "#000000",
            "text_bg": "#ffffff",
            "text_fg": "#000000",
            "scrollbar_trough": "#f0f0f0",
            "scrollbar_bg": "#c0c0c0"
        }

def apply_theme(widget, theme):
    """
    Wendet das geladene Theme rekursiv auf ein tkinter-Widget und alle untergeordneten Widgets an.
    """
    try:
        if isinstance(widget, tk.Button):
            widget.configure(bg=theme.get("button_bg"), fg=theme.get("button_fg"))
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=theme.get("entry_bg"), fg=theme.get("entry_fg"))
        elif isinstance(widget, tk.Listbox):
            widget.configure(bg=theme.get("listbox_bg"), fg=theme.get("listbox_fg"))
        elif isinstance(widget, tk.Text):
            widget.configure(bg=theme.get("text_bg"), fg=theme.get("text_fg"))
        elif isinstance(widget, tk.Scrollbar):
            widget.configure(
                troughcolor=theme.get("scrollbar_trough", theme.get("bg")),
                background=theme.get("scrollbar_bg", theme.get("bg")),
                highlightbackground=theme.get("bg", "white")
            )
        elif isinstance(widget, tk.OptionMenu):
            widget.configure(bg=theme.get("button_bg"), fg=theme.get("button_fg"))
            widget["menu"].configure(bg=theme.get("button_bg"), fg=theme.get("button_fg"))
        else:
            widget.configure(bg=theme.get("bg"), fg=theme.get("fg"))
    except tk.TclError:
        pass

    for child in widget.winfo_children():
        apply_theme(child, theme)
