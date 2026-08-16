import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

import settings


class SettingsEditor:
    def __init__(self, master:tk.Tk):
        self.master = master
        self.master.title("TM Settings")
        self.master.geometry("760x520")
        self.master.minsize(700, 420)

        self.original_values = {}
        self.fields = {}

        self._load_original_values()

        main = ttk.Frame(master, padding=12)
        main.pack(fill="both", expand=True)

        title = ttk.Label(main, text="Paramètres du projet", font=("Segoe UI", 12, "bold"))
        title.pack(anchor="w", pady=(0, 10))

        canvas = tk.Canvas(main, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        self.form_frame = ttk.Frame(canvas)

        self.form_frame.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._build_form()

        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(12, 0))

        ttk.Button(actions, text="Enregistrer", command=self.save_settings).pack(side="right")
        ttk.Button(actions, text="Fermer", command=self.master.destroy).pack(side="right", padx=(0, 8))

    def _load_original_values(self):
        for name in dir(settings):
            if name.isupper() and not name.startswith("__"):
                self.original_values[name] = getattr(settings, name)

    def _is_file_setting(self, name, value):
        if name.endswith("_FILE"):
            return True
        if isinstance(value, str):
            lowered = value.lower()
            if lowered.endswith((".csv", ".txt", ".json", ".xlsx", ".xls", ".xml")):
                return True
        return False

    def _build_form(self):
        for name in sorted(self.original_values):
            value = self.original_values[name]
            row = ttk.Frame(self.form_frame, padding=(0, 4))
            row.pack(fill="x")

            label = ttk.Label(row, text=name, width=26, anchor="w")
            label.pack(side="left")

            var = tk.StringVar(value=str(value))
            entry = ttk.Entry(row, textvariable=var)
            entry.pack(side="left", fill="x", expand=True, padx=(10, 6))

            if self._is_file_setting(name, value):
                button = ttk.Button(row, text="Parcourir", command=lambda n=name, v=var: self.choose_file(n, v))
                button.pack(side="left")
            self.fields[name] = var

    def choose_file(self, setting_name, variable):
        current_value = variable.get()
        initial_dir = os.path.dirname(current_value) if current_value else os.getcwd()
        filename = filedialog.askopenfilename(
            title=f"Sélectionner le fichier pour {setting_name}",
            initialdir=initial_dir,
            filetypes=[("Fichiers", "*.*")],
        )
        if filename:
            variable.set(filename)

    def save_settings(self):
        updated = {}
        for name, variable in self.fields.items():
            raw_value = variable.get().strip()
            original_value = self.original_values[name]

            try:
                if isinstance(original_value, bool):
                    value = raw_value.lower() in {"1", "true", "yes", "y", "on"}
                elif isinstance(original_value, int):
                    value = int(raw_value)
                elif isinstance(original_value, float):
                    value = float(raw_value)
                else:
                    value = raw_value
            except ValueError:
                messagebox.showerror(
                    "Valeur invalide",
                    f"La valeur pour {name} est invalide : {raw_value}",
                )
                return

            updated[name] = value

        with open(settings.__file__, "w", encoding="utf-8") as file:
            for name in sorted(updated):
                value = updated[name]

                if isinstance(value, str):
                    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
                    line = f'{name} = "{escaped}"'
                elif isinstance(value, bool):
                    line = f"{name} = {str(value).lower()}"
                elif value is None:
                    line = f"{name} = None"
                else:
                    line = f"{name} = {value}"

                file.write(f"{line}\n")

        messagebox.showinfo("Sauvegardé", "Les paramètres ont bien été enregistrés dans settings.py.")


if __name__ == "__main__":
    root = tk.Tk()
    SettingsEditor(root)
    root.mainloop()
