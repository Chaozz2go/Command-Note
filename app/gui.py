import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import os
import json

from utils import search_handler
from app.category_manager import CategoryManager
from app.themes import load_theme, apply_theme
from app.utils import sanitize_filename

logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s %(levelname)s:%(message)s')

current_theme = "light"
theme = {}

class CommandManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Command Manager")
        self.geometry("900x600")

        settings = self.load_settings()
        self.current_theme = settings.get("theme", current_theme)
        self.current_category = settings.get("last_category")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        load_theme(self)
        self.configure(bg=theme.get("bg", "white"))
        apply_theme(self, theme)

        self.categories = CategoryManager.get_all_categories()
        if not self.categories:
            messagebox.showerror("Fehler", "Keine Kategorien gefunden!")
            self.destroy()
            return

        if self.current_category not in self.categories:
            self.current_category = self.categories[0]

        self.commands = CategoryManager.load_commands(self.current_category)

        self.create_menubar()
        self.create_widgets()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_menubar(self):
        self.menubar = tk.Menu(self)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="Neue Kategorie", command=self.create_new_category)
        file_menu.add_separator()
        file_menu.add_command(label="Kategorie importieren", command=self.import_category)
        file_menu.add_command(label="Kategorie exportieren", command=self.export_category)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.on_close)
        self.menubar.add_cascade(label="Datei", menu=file_menu)

        commands_menu = tk.Menu(self.menubar, tearoff=0)
        commands_menu.add_command(label="Befehl hinzufügen", command=self.add_command)
        commands_menu.add_command(label="Befehl bearbeiten", command=self.edit_command)
        commands_menu.add_command(label="Befehl löschen", command=self.delete_command)
        self.menubar.add_cascade(label="Befehle", menu=commands_menu)

        view_menu = tk.Menu(self.menubar, tearoff=0)
        theme_menu = tk.Menu(view_menu, tearoff=0)
        for name in ["light", "dark", "hacker"]:
            theme_menu.add_radiobutton(label=name.capitalize(), command=lambda n=name: self.set_theme(n))
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        self.menubar.add_cascade(label="Ansicht", menu=view_menu)

        self.config(menu=self.menubar)

    def create_widgets(self):
        ttk.Label(self, text="Willkommen im Command Manager!").pack(pady=10)

        self.category_var = tk.StringVar(value=self.current_category)
        self.category_menu = ttk.Combobox(self, textvariable=self.category_var, values=self.categories, state="readonly")
        self.category_menu.pack(pady=5)
        self.category_menu.bind("<<ComboboxSelected>>", self.change_category)

        search_frame = ttk.Frame(self)
        search_frame.pack(pady=5)
        ttk.Label(search_frame, text="Filter (Tag):").pack(side="left", padx=(10, 0))
        self.tag_filter_var = tk.StringVar(value="Alle")
        self.tag_combobox = ttk.Combobox(search_frame, textvariable=self.tag_filter_var, state="readonly")
        self.tag_combobox.pack(side="left", padx=5)
        self.tag_combobox.bind("<<ComboboxSelected>>", self.perform_search)
        ttk.Label(search_frame, text="Suche:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", self.perform_search)

        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.command_listbox = tk.Listbox(list_frame, height=15)
        self.command_listbox.pack(side="left", fill="both", expand=True)
        self.command_listbox.bind("<<ListboxSelect>>", self.show_command_details)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.command_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.command_listbox.config(yscrollcommand=scrollbar.set)

        self.detail_text = tk.Text(self, height=10)
        self.detail_text.pack(fill="x", padx=10, pady=(0, 10))

        self.update_listbox(self.commands)

    def perform_search(self, event=None):
        search_term = self.search_var.get()
        selected_tag = self.tag_filter_var.get()
        filtered = search_handler.filter_commands(self.commands, search_term, selected_tag)
        self.update_listbox(filtered)

    def update_tag_dropdown(self):
        tags = set()
        for cmd in self.commands:
            for tag in cmd.get("tags", []):
                tags.add(tag)
        values = ["Alle"] + sorted(tags)
        self.tag_combobox["values"] = values

    def update_listbox(self, commands):
        self.update_tag_dropdown()
        self.command_listbox.delete(0, tk.END)
        for cmd in commands:
            self.command_listbox.insert(tk.END, cmd.get("command", ""))

    def show_command_details(self, event=None):
        selection = self.command_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        command_name = self.command_listbox.get(index)
        for cmd in self.commands:
            if cmd.get("command") == command_name:
                self.detail_text.delete("1.0", tk.END)
                self.detail_text.insert(tk.END, cmd.get("beschreibung", ""))
                break

    def change_category(self, event=None):
        selected = self.category_var.get()
        if selected:
            self.current_category = selected
            self.commands = CategoryManager.load_commands(selected)
            self.update_listbox(self.commands)

    def create_new_category(self):
        def create():
            name = entry.get().strip()
            if not name:
                messagebox.showwarning("Fehler", "Bitte einen Namen eingeben.")
                return
            if name in self.categories:
                messagebox.showinfo("Hinweis", "Kategorie existiert bereits.")
                return
            self.categories.append(name)
            self.category_menu["values"] = self.categories
            self.category_var.set(name)
            self.current_category = name
            self.commands = []
            CategoryManager.save_commands(name, self.commands)
            self.update_listbox(self.commands)
            new_window.destroy()

        new_window = tk.Toplevel(self)
        new_window.title("Neue Kategorie")
        ttk.Label(new_window, text="Name der neuen Kategorie:").pack(padx=10, pady=5)
        entry = ttk.Entry(new_window)
        entry.pack(padx=10, pady=5)
        ttk.Button(new_window, text="Erstellen", command=create).pack(pady=10)

    def import_category(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON-Dateien", "*.json")])
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            name = os.path.splitext(os.path.basename(file_path))[0]
            if name not in self.categories:
                self.categories.append(name)
                self.category_menu["values"] = self.categories
            CategoryManager.save_commands(name, data)
            messagebox.showinfo("Import", f"Kategorie '{name}' erfolgreich importiert.")
        except Exception as e:
            logging.exception("Fehler beim Importieren")
            messagebox.showerror("Fehler", f"Import fehlgeschlagen: {e}")

    def export_category(self):
        if not self.current_category:
            messagebox.showwarning("Export", "Keine Kategorie ausgewählt.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON-Dateien", "*.json")],
            initialfile=f"{self.current_category}.json"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.commands, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Export", "Kategorie erfolgreich exportiert.")
            except Exception as e:
                logging.exception("Fehler beim Exportieren")
                messagebox.showerror("Fehler", f"Export fehlgeschlagen: {e}")

    def set_theme(self, theme_name):
        global current_theme, theme
        current_theme = theme_name
        self.current_theme = theme_name
        load_theme(self)
        self.configure(bg=theme.get("bg"))
        apply_theme(self, theme)

        # ttk styles
        self.style.configure("TLabel", background=theme.get("bg"), foreground=theme.get("fg"))
        self.style.configure("TButton", background=theme.get("button_bg"), foreground=theme.get("button_fg"))
        self.style.configure("TEntry", fieldbackground=theme.get("entry_bg"), foreground=theme.get("entry_fg"))
        self.style.configure("TCombobox", fieldbackground=theme.get("entry_bg"), foreground=theme.get("entry_fg"))
        self.style.configure("TMenubutton", background=theme.get("button_bg"), foreground=theme.get("button_fg"))

    def load_settings(self):
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_settings(self):
        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump({
                    "theme": self.current_theme,
                    "last_category": self.current_category
                }, f, indent=2)
        except Exception as e:
            logging.exception("Fehler beim Speichern der Einstellungen")

    def on_close(self):
        self.save_settings()
        self.destroy()

    def add_command(self):
        def save():
            cmd = command_var.get().strip()
            desc = beschreibung_entry.get("1.0", tk.END).strip()
            tags = [t.strip() for t in tags_var.get().split(",") if t.strip()]
            if not cmd:
                messagebox.showwarning("Fehler", "Kein Befehl eingegeben.")
                return
            self.commands.append({"command": cmd, "beschreibung": desc, "tags": tags})
            CategoryManager.save_commands(self.current_category, self.commands)
            self.update_listbox(self.commands)
            window.destroy()

        window = tk.Toplevel(self)
        window.title("Befehl hinzufügen")
        ttk.Label(window, text="Command:").pack()
        command_var = tk.StringVar()
        ttk.Entry(window, textvariable=command_var).pack()
        ttk.Label(window, text="Beschreibung:").pack()
        beschreibung_entry = tk.Text(window, height=4)
        beschreibung_entry.pack()
        ttk.Label(window, text="Tags (Komma getrennt):").pack()
        tags_var = tk.StringVar()
        ttk.Entry(window, textvariable=tags_var).pack()
        ttk.Button(window, text="Speichern", command=save).pack(pady=10)

    def edit_command(self):
        selection = self.command_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        cmd_obj = self.commands[index]

        def save():
            cmd_obj["command"] = command_var.get().strip()
            cmd_obj["beschreibung"] = beschreibung_entry.get("1.0", tk.END).strip()
            cmd_obj["tags"] = [t.strip() for t in tags_var.get().split(",") if t.strip()]
            CategoryManager.save_commands(self.current_category, self.commands)
            self.update_listbox(self.commands)
            window.destroy()

        window = tk.Toplevel(self)
        window.title("Befehl bearbeiten")
        ttk.Label(window, text="Command:").pack()
        command_var = tk.StringVar(value=cmd_obj.get("command"))
        ttk.Entry(window, textvariable=command_var).pack()
        ttk.Label(window, text="Beschreibung:").pack()
        beschreibung_entry = tk.Text(window, height=4)
        beschreibung_entry.insert(tk.END, cmd_obj.get("beschreibung", ""))
        beschreibung_entry.pack()
        ttk.Label(window, text="Tags (Komma getrennt):").pack()
        tags_var = tk.StringVar(value=", ".join(cmd_obj.get("tags", [])))
        ttk.Entry(window, textvariable=tags_var).pack()
        ttk.Button(window, text="Speichern", command=save).pack(pady=10)

    def delete_command(self):
        selection = self.command_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        cmd = self.commands[index].get("command", "")
        confirm = messagebox.askyesno("Löschen", f"Befehl '{cmd}' wirklich löschen?")
        if confirm:
            del self.commands[index]
            CategoryManager.save_commands(self.current_category, self.commands)
            self.update_listbox(self.commands)
